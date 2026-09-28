from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.runtime.flow_os.evidence import EvidenceRecord


class BrowserEvidenceError(RuntimeError):
    """Raised when rendered browser evidence is missing, unsafe or invalid."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class PlaywrightBrowserEvidenceAdapter:
    """Capture or ingest real Playwright-rendered evidence into Flow OS evidence.

    The adapter trusts only locally generated artifact files. Remote browsing is denied
    by default; capture accepts localhost URLs and same-origin relative routes unless
    runtime policy explicitly enables remote targets. Screenshot bytes are hashed and
    linked to their JSON observation so a gate can distinguish rendered proof from
    provider prose.
    """

    def __init__(self, qa_root: Path, policy: dict[str, Any]) -> None:
        raw_root = Path(qa_root)
        if raw_root.is_symlink():
            raise BrowserEvidenceError("QA root must not be a symlink")
        self.qa_root = raw_root.resolve()
        self.policy = dict(policy)
        config = dict(self.policy.get("browser_evidence", {}))
        self.allow_remote = bool(config.get("allow_remote", False))
        self.max_artifact_bytes = int(config.get("max_artifact_bytes", 4 * 1024 * 1024))
        self.max_routes = int(config.get("max_routes", 12))
        self.timeout_seconds = int(config.get("timeout_seconds", 180))
        if not self.qa_root.is_dir():
            raise BrowserEvidenceError(f"QA root does not exist: {self.qa_root}")

    def _validate_base_url(self, base_url: str) -> str:
        parsed = urlparse(str(base_url))
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise BrowserEvidenceError("browser evidence base_url must be http(s)")
        if not self.allow_remote and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise BrowserEvidenceError("remote browser targets are disabled by runtime policy")
        return str(base_url)

    def _validate_routes(self, routes: list[str]) -> list[str]:
        normalized = [str(route).strip() for route in routes if str(route).strip()]
        if not normalized or len(normalized) > self.max_routes:
            raise BrowserEvidenceError(f"routes must contain between 1 and {self.max_routes} entries")
        for route in normalized:
            parsed = urlparse(route)
            if (
                not route.startswith("/")
                or route.startswith("//")
                or parsed.scheme
                or parsed.netloc
            ):
                raise BrowserEvidenceError(
                    "browser evidence routes must be same-origin relative paths beginning with exactly one '/'"
                )
        return normalized

    def _artifact_root(self, artifacts_dir: Path | None) -> Path:
        raw = Path(artifacts_dir or (self.qa_root / "artifacts"))
        if raw.is_symlink():
            raise BrowserEvidenceError("browser artifact root must not be a symlink")
        root = raw.resolve()
        try:
            root.relative_to(self.qa_root)
        except ValueError as exc:
            raise BrowserEvidenceError("browser artifact root must stay below qa_root") from exc
        return root

    def capture(self, base_url: str, routes: list[str], artifacts_dir: Path | None = None) -> list[EvidenceRecord]:
        base_url = self._validate_base_url(base_url)
        normalized = self._validate_routes(routes)
        output = self._artifact_root(artifacts_dir)
        output.mkdir(parents=True, exist_ok=True)
        env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP", "LANG", "LC_ALL"}
        }
        env["QA_BASE_URL"] = base_url
        env["QA_ALLOWED_ORIGIN"] = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        env["QA_ROUTES"] = ",".join(normalized)
        env["QA_ARTIFACTS_DIR"] = str(output)
        result = subprocess.run(
            ["npm", "run", "test:browser", "--", "--workers=1"],
            cwd=self.qa_root,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            env=env,
            shell=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout)[-6000:]
            raise BrowserEvidenceError(f"Playwright browser capture failed ({result.returncode}): {detail}")
        return self.collect(output)

    def _safe_artifact(self, root: Path, raw: str) -> Path:
        relative = Path(raw)
        if relative.is_absolute() or not relative.parts:
            raise BrowserEvidenceError("browser evidence paths must be artifact-relative")
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise BrowserEvidenceError(f"browser evidence refuses symlink path: {raw}")
        try:
            candidate = (root / relative).resolve(strict=True)
        except FileNotFoundError as exc:
            raise BrowserEvidenceError(f"browser evidence file missing: {raw}") from exc
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise BrowserEvidenceError(f"browser evidence path escapes artifact root: {raw}") from exc
        if not candidate.is_file():
            raise BrowserEvidenceError(f"browser evidence file is not regular: {raw}")
        if candidate.stat().st_size <= 0 or candidate.stat().st_size > self.max_artifact_bytes:
            raise BrowserEvidenceError(f"browser evidence file has invalid size: {raw}")
        return candidate

    def collect(self, artifacts_dir: Path | None = None, stage_id: str = "qa") -> list[EvidenceRecord]:
        root = self._artifact_root(artifacts_dir)
        if not root.is_dir():
            raise BrowserEvidenceError(f"browser artifact root does not exist: {root}")
        records: list[EvidenceRecord] = []
        files = sorted(root.glob("browser-evidence-*.json"))
        if not files:
            raise BrowserEvidenceError("no browser-evidence-*.json artifacts found")
        if len(files) > self.max_routes:
            raise BrowserEvidenceError("browser evidence artifact count exceeds policy route limit")
        for path in files:
            if path.is_symlink() or path.stat().st_size > self.max_artifact_bytes:
                raise BrowserEvidenceError(f"unsafe browser evidence JSON: {path.name}")
            payload = json.loads(path.read_text(encoding="utf-8"))
            screenshot_raw = str(payload.get("screenshot", "")).strip()
            if not screenshot_raw:
                raise BrowserEvidenceError(f"browser evidence missing screenshot reference: {path.name}")
            screenshot = self._safe_artifact(root, screenshot_raw)
            page_errors = list(payload.get("pageErrors", []))
            console_errors = [
                item for item in list(payload.get("consoleMessages", []))
                if isinstance(item, dict) and str(item.get("type", "")) == "error"
            ]
            box = payload.get("box")
            status = "PASS" if not page_errors and not console_errors and box is not None else "FAIL"
            route = str(payload.get("route", ""))
            screenshot_hash = _sha256(screenshot)
            records.append(
                EvidenceRecord(
                    id=f"browser_{hashlib.sha256((path.name + screenshot_hash).encode()).hexdigest()[:16]}",
                    type="browser_render",
                    stage_id=stage_id,
                    tool="playwright",
                    status=status,
                    summary=f"Playwright rendered {route or path.stem}: {status}",
                    data={
                        "route": route,
                        "url": str(payload.get("url", "")),
                        "title": str(payload.get("title", "")),
                        "viewport": dict(payload.get("viewport", {})),
                        "box": box,
                        "screenshot": screenshot.name,
                        "screenshot_sha256": screenshot_hash,
                        "evidence_json": path.name,
                        "evidence_sha256": _sha256(path),
                        "aria_snapshot": str(payload.get("ariaSnapshot", ""))[:20000],
                        "page_errors": page_errors,
                        "console_errors": console_errors,
                    },
                )
            )
        return records
