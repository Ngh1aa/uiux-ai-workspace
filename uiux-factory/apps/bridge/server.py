from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from apps.bridge.job_runtime import (
    BoundedJobExecutor,
    JobStore,
    QueueFullError,
    run_process_streaming,
    validate_job_id,
)
from core.contracts.design_context_schema import DesignContext


GENERATED = ROOT / "generated"
RUNS = ROOT / "runs"

HOST = os.environ.get("UIUX_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("UIUX_BRIDGE_PORT", "8788"))
MAX_WORKERS = max(1, int(os.environ.get("UIUX_BRIDGE_MAX_WORKERS", "1")))
MAX_QUEUE = max(0, int(os.environ.get("UIUX_BRIDGE_MAX_QUEUE", "8")))
JOB_TIMEOUT_SECONDS = max(
    1.0,
    float(os.environ.get("UIUX_JOB_TIMEOUT_SECONDS", "7200")),
)

ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}
if os.environ.get("UIUX_WORKBENCH_ORIGIN"):
    ALLOWED_ORIGINS.add(os.environ["UIUX_WORKBENCH_ORIGIN"])

STORE = JobStore(RUNS)
EXECUTOR = BoundedJobExecutor(max_workers=MAX_WORKERS, max_queue=MAX_QUEUE)

ARTIFACT_NAMES = {
    "design-system.json",
    "reference-dna.json",
    "DESIGN.md",
    "tokens.css",
    "quality-loop.json",
    "browser-report.json",
}
REFERENCE_ARTIFACT_RE = re.compile(
    r"references/reference-[a-f0-9]{12}-(desktop|mobile)\.png"
)


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def read_run_summary(run_dir: Path | None) -> dict:
    if not run_dir:
        return {}
    run_json = run_dir / "run.json"
    if not run_json.is_file():
        return {}
    try:
        payload = json.loads(run_json.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def latest_run() -> Path | None:
    if not RUNS.is_dir():
        return None
    candidates = [
        path.resolve()
        for path in RUNS.iterdir()
        if path.is_dir() and (path / "run.json").is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def project_slug_from_run(run_dir: Path | None) -> str | None:
    if not run_dir:
        return None

    summary = read_run_summary(run_dir)
    implementation = (summary.get("artifacts") or {}).get("implementation")
    if not implementation:
        return None

    path = Path(implementation)
    if not path.is_file():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None

    project_slug = payload.get("project_slug")
    if project_slug:
        return str(project_slug)

    project_dir = payload.get("project_dir")
    if project_dir:
        return Path(project_dir).name

    return None


def format_research(results: list[dict]) -> str:
    if not results:
        return ""

    lines = [
        "",
        "",
        "WEB RESEARCH EVIDENCE PROVIDED BY THE DESIGN WORKBENCH:",
        (
            "Treat these as external reference evidence only. "
            "Do not claim facts beyond the supplied snippets/URLs. "
            "Use them to understand current market patterns, visual references "
            "and competitor conventions; do not copy a competitor."
        ),
        "",
    ]

    for index, item in enumerate(results[:8], start=1):
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        description = str(item.get("description", "")).strip()
        lines.extend(
            [
                f"[{index}] {title}",
                f"URL: {url}",
                f"Snippet: {description}",
                "",
            ]
        )

    return "\n".join(lines)


def is_allowed_artifact_name(filename: str) -> bool:
    return filename in ARTIFACT_NAMES or bool(REFERENCE_ARTIFACT_RE.fullmatch(filename))


def available_artifacts(job_id: str, summary: dict) -> list[str]:
    run_dir = RUNS / job_id
    names: list[str] = []

    known = {
        "design_system": "design-system.json",
        "reference_analysis": "reference-dna.json",
    }
    for artifact_key, filename in known.items():
        if artifact_key in (summary.get("artifacts") or {}) and (run_dir / filename).is_file():
            names.append(filename)

    for filename in ARTIFACT_NAMES - set(known.values()):
        if (run_dir / filename).is_file():
            names.append(filename)

    references_dir = run_dir / "references"
    if references_dir.is_dir():
        for path in sorted(references_dir.glob("reference-*.png")):
            relative = path.relative_to(run_dir).as_posix()
            if REFERENCE_ARTIFACT_RE.fullmatch(relative):
                names.append(relative)

    return sorted(set(names))


def _job_error_from_summary(summary: dict, return_code: int) -> str:
    errors = summary.get("errors") or []
    if isinstance(errors, list) and errors:
        return "; ".join(str(item) for item in errors)
    return f"Factory exited with code {return_code}"


def run_factory_job(
    job_id: str,
    prompt: str,
    search_results: list[dict],
    design_context: DesignContext | None = None,
    mode: str = "build",
    engine: str = "template",
) -> None:
    run_dir = RUNS / job_id
    enriched_prompt = prompt.strip() + format_research(search_results)

    STORE.update(job_id, status="running", started_at=time.time())

    try:
        run_dir.mkdir(parents=True, exist_ok=True)

        context_path = run_dir / "design-context.json"
        context_path.write_text(
            (design_context or DesignContext()).model_dump_json(indent=2),
            encoding="utf-8",
        )

        goal_path = run_dir / "goal.txt"
        goal_path.write_text(enriched_prompt, encoding="utf-8")

        command = [
            sys.executable,
            str(ROOT / "run.py"),
            "--goal-file",
            str(goal_path),
            "--run-id",
            job_id,
            "--engine",
            engine,
            "--context",
            str(context_path),
        ]
        if mode == "intelligence":
            command.append("--intelligence-only")

        result = run_process_streaming(
            command,
            cwd=ROOT,
            env={
                **os.environ,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
            },
            timeout_seconds=JOB_TIMEOUT_SECONDS,
            on_output=lambda line: STORE.append_output(job_id, line),
        )

        summary = read_run_summary(run_dir)
        project_slug = (
            project_slug_from_run(run_dir)
            if mode == "build" and (summary.get("artifacts") or {}).get("implementation")
            else None
        )

        common = {
            "return_code": result.return_code,
            "completed_at": time.time(),
            "run_id": run_dir.name,
            "project_slug": project_slug,
        }

        if result.timed_out:
            STORE.update(
                job_id,
                status="failed",
                error=f"Factory exceeded the {JOB_TIMEOUT_SECONDS:g}s job timeout.",
                **common,
            )
            return

        if result.return_code == 0 and summary.get("status") == "completed":
            STORE.update(job_id, status="completed", **common)
            return

        STORE.update(
            job_id,
            status="failed",
            error=_job_error_from_summary(summary, result.return_code),
            **common,
        )

    except Exception as error:
        STORE.update(
            job_id,
            status="failed",
            completed_at=time.time(),
            error=f"{type(error).__name__}: {error}",
        )


def reconcile_interrupted_jobs() -> None:
    """Make persisted bridge state truthful after a bridge restart."""

    for job in STORE.iter_jobs():
        if job.get("status") not in {"queued", "running"}:
            continue

        job_id = str(job.get("id", ""))
        try:
            validate_job_id(job_id)
        except ValueError:
            continue

        run_dir = RUNS / job_id
        summary = read_run_summary(run_dir)
        project_slug = project_slug_from_run(run_dir)

        if summary.get("status") == "completed":
            STORE.update(
                job_id,
                status="completed",
                completed_at=time.time(),
                run_id=job_id,
                project_slug=project_slug,
                recovered_after_restart=True,
            )
        elif summary.get("status") == "failed":
            STORE.update(
                job_id,
                status="failed",
                completed_at=time.time(),
                run_id=job_id,
                project_slug=project_slug,
                error="; ".join(str(item) for item in summary.get("errors", []))
                or "Factory run failed before the bridge restarted.",
                recovered_after_restart=True,
            )
        else:
            STORE.update(
                job_id,
                status="failed",
                completed_at=time.time(),
                run_id=job_id if run_dir.exists() else None,
                project_slug=project_slug,
                error=(
                    "Bridge restarted while this job was queued or running. "
                    "Partial run artifacts, if any, remain under runs/<job-id>."
                ),
                recovered_after_restart=True,
            )


class Handler(BaseHTTPRequestHandler):
    server_version = "UIUXFactoryBridge/1.1"

    def log_message(self, fmt, *args):  # noqa: A003
        sys.stdout.write("[bridge] " + fmt % args + "\n")

    def cors(self) -> None:
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.cors()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        origin = self.headers.get("Origin")
        if origin and origin not in ALLOWED_ORIGINS:
            self.send_json(
                {"error": "This origin is not allowed to start local Factory jobs."},
                status=403,
            )
            return

        parsed = urlparse(self.path)
        if parsed.path not in {"/run", "/intelligence"}:
            self.send_json({"error": "Not found"}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 12_000_000:
                self.send_json(
                    {"error": "Request must contain JSON and be at most 12 MB."},
                    status=413,
                )
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")
        except Exception:
            self.send_json({"error": "Invalid JSON body"}, status=400)
            return

        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            self.send_json({"error": "Prompt is required"}, status=400)
            return

        search_results = payload.get("search_results") or []
        if not isinstance(search_results, list):
            search_results = []
        search_results = [
            item for item in search_results[:8] if isinstance(item, dict)
        ]

        try:
            design_context = DesignContext.model_validate(
                payload.get("design_context", {})
            )
        except ValidationError as error:
            message = "; ".join(
                f"{'.'.join(map(str, item['loc']))}: {item['msg']}"
                for item in error.errors(include_input=False)
            )
            self.send_json({"error": message}, status=400)
            return

        mode = "intelligence" if parsed.path == "/intelligence" else "build"
        engine = payload.get("engine", "template")
        if engine not in {"template", "ai"}:
            self.send_json({"error": "Unknown generation engine"}, status=400)
            return

        if mode == "build" and engine == "ai":
            from core.runtime.free_provider import FreeProvider, ProviderError

            try:
                FreeProvider.from_env(ROOT)
            except ProviderError as error:
                self.send_json({"error": str(error)}, status=400)
                return

        job_id = uuid.uuid4().hex[:12]
        job = {
            "id": job_id,
            "status": "queued",
            "prompt": prompt,
            "created_at": time.time(),
            "mode": mode,
            "engine": engine,
        }

        try:
            response_job = STORE.create(job)
            EXECUTOR.submit(
                run_factory_job,
                job_id,
                prompt,
                search_results,
                design_context,
                mode,
                engine,
            )
        except QueueFullError as error:
            STORE.update(
                job_id,
                status="failed",
                completed_at=time.time(),
                error=str(error),
            )
            self.send_json(
                {"error": str(error), "job_id": job_id},
                status=429,
            )
            return
        except Exception as error:
            STORE.update(
                job_id,
                status="failed",
                completed_at=time.time(),
                error=f"{type(error).__name__}: {error}",
            )
            self.send_json({"error": str(error)}, status=500)
            return

        self.send_json(response_job or job, status=202)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            from core.runtime.free_provider import FreeProvider, ProviderError

            try:
                provider = FreeProvider.from_env(ROOT)
                ai = {
                    "configured": True,
                    "providers": [config.name for config in provider.configs],
                }
            except ProviderError:
                ai = {"configured": False, "providers": []}

            self.send_json(
                {
                    "status": "ok",
                    "ai": ai,
                    "root": str(ROOT),
                    "python": sys.executable,
                    "generated": str(GENERATED),
                    "jobs": {
                        "max_workers": MAX_WORKERS,
                        "max_queue": MAX_QUEUE,
                        "timeout_seconds": JOB_TIMEOUT_SECONDS,
                        "persistent": True,
                    },
                }
            )
            return

        if parsed.path.startswith("/jobs/"):
            if self._serve_job_request(parsed.path):
                return

        if parsed.path == "/latest":
            run_dir = latest_run()
            self.send_json(
                {
                    "run_id": run_dir.name if run_dir else None,
                    "run": read_run_summary(run_dir),
                    "project_slug": project_slug_from_run(run_dir),
                }
            )
            return

        if parsed.path.startswith("/preview/"):
            self.serve_preview(parsed.path)
            return

        self.send_json({"error": "Not found"}, status=404)

    def _serve_job_request(self, path: str) -> bool:
        artifact_match = re.fullmatch(
            r"/jobs/([a-f0-9]{12})/artifacts/(.+)",
            path,
        )
        if artifact_match:
            job_id, filename = artifact_match.groups()
            self.serve_artifact(job_id, filename)
            return True

        job_match = re.fullmatch(r"/jobs/([a-f0-9]{12})", path)
        if not job_match:
            return False

        job_id = job_match.group(1)
        payload = STORE.snapshot(job_id)
        if not payload:
            self.send_json({"error": "Unknown job"}, status=404)
            return True

        summary = read_run_summary(RUNS / job_id)
        payload["active_stage"] = summary.get("active_stage")
        payload["completed_stages"] = summary.get("completed_stages", [])
        payload["artifacts"] = available_artifacts(job_id, summary)
        self.send_json(payload)
        return True

    def serve_artifact(self, job_id: str, filename: str) -> None:
        if not is_allowed_artifact_name(filename):
            self.send_json({"error": "Unknown artifact"}, status=404)
            return

        run_root = (RUNS / job_id).resolve()
        target = (run_root / filename).resolve()
        if not target.is_relative_to(run_root) or not target.is_file():
            self.send_json({"error": "Artifact is not available yet"}, status=404)
            return

        body = target.read_bytes()
        content_type = {
            ".png": "image/png",
            ".md": "text/plain; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }.get(target.suffix.lower(), "application/json; charset=utf-8")

        self.send_response(200)
        self.cors()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def serve_preview(self, request_path: str) -> None:
        relative = unquote(request_path[len("/preview/") :])
        parts = [part for part in relative.split("/") if part]
        if not parts:
            self.send_error(404)
            return

        project_slug = parts[0]
        project_root = (GENERATED / project_slug).resolve()
        if not (
            GENERATED.exists()
            and project_root.is_relative_to(GENERATED.resolve())
            and project_root.exists()
        ):
            self.send_error(404)
            return

        rest = parts[1:]
        target = (
            project_root / (Path(*rest) if rest else Path("index.html"))
        ).resolve()
        if target.is_dir():
            target = target / "index.html"

        if not target.is_relative_to(project_root):
            self.send_error(403)
            return

        if not target.exists():
            clean_candidate = (
                project_root / Path(*rest) / "index.html"
                if rest
                else project_root / "index.html"
            ).resolve()
            if clean_candidate.is_relative_to(project_root) and clean_candidate.exists():
                target = clean_candidate
            else:
                self.send_error(404)
                return

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        body = target.read_bytes()

        self.send_response(200)
        self.cors()
        if (project_root / ".uiux-ai.json").is_file():
            from core.actions.generate_ai_frontend import AI_PREVIEW_CSP

            self.send_header("Content-Security-Policy", AI_PREVIEW_CSP)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    reconcile_interrupted_jobs()
    server = ThreadingHTTPServer((HOST, PORT), Handler)

    print()
    print("=" * 72)
    print("UIUX FACTORY - DESIGN WORKBENCH BRIDGE")
    print("=" * 72)
    print(f"[Factory] {ROOT}")
    print(f"[Python] {sys.executable}")
    print(f"[Bridge] http://{HOST}:{PORT}")
    print(
        f"[Jobs] workers={MAX_WORKERS} queue={MAX_QUEUE} "
        f"timeout={JOB_TIMEOUT_SECONDS:g}s persistent=yes"
    )
    print(
        "[Endpoints] /health /run /intelligence /jobs/<id> "
        "/jobs/<id>/artifacts/<file> /latest /preview/<project>/"
    )
    print("=" * 72)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        EXECUTOR.shutdown()


if __name__ == "__main__":
    main()
