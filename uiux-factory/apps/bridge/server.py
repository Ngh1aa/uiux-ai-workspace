from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import threading
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
from core.contracts.design_context_schema import DesignContext
GENERATED = ROOT / "generated"
RUNS = ROOT / "runs"

HOST = os.environ.get("UIUX_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("UIUX_BRIDGE_PORT", "8788"))
ALLOWED_ORIGINS = {"http://localhost:5173", "http://127.0.0.1:5173"}
if os.environ.get("UIUX_WORKBENCH_ORIGIN"):
    ALLOWED_ORIGINS.add(os.environ["UIUX_WORKBENCH_ORIGIN"])

JOBS: dict[str, dict] = {}
LOCK = threading.Lock()


def json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")


def snapshot_runs() -> set[Path]:
    if not RUNS.exists():
        return set()

    return {
        path.resolve()
        for path in RUNS.iterdir()
        if path.is_dir()
    }


def newest_new_run(before: set[Path]) -> Path | None:
    if not RUNS.exists():
        return None

    candidates = [
        path.resolve()
        for path in RUNS.iterdir()
        if (
            path.is_dir()
            and path.resolve() not in before
            and (path / "run.json").exists()
        )
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda path: path.stat().st_mtime,
    )


def latest_run() -> Path | None:
    if not RUNS.exists():
        return None

    candidates = [
        path.resolve()
        for path in RUNS.iterdir()
        if (
            path.is_dir()
            and (path / "run.json").exists()
        )
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda path: path.stat().st_mtime,
    )


def read_run_summary(run_dir: Path | None) -> dict:
    if not run_dir:
        return {}

    run_json = run_dir / "run.json"

    if not run_json.exists():
        return {}

    try:
        return json.loads(
            run_json.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {}


def project_slug_from_run(run_dir: Path | None) -> str | None:
    if not run_dir:
        return None

    summary = read_run_summary(run_dir)
    artifacts = summary.get("artifacts") or {}
    implementation = artifacts.get("implementation")

    if implementation:
        path = Path(implementation)

        if path.exists():
            try:
                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

                project_slug = payload.get(
                    "project_slug"
                )

                if project_slug:
                    return str(project_slug)

                project_dir = payload.get(
                    "project_dir"
                )

                if project_dir:
                    return Path(
                        project_dir
                    ).name

            except Exception:
                pass

    return None


def format_research(
    results: list[dict],
) -> str:
    if not results:
        return ""

    lines = [
        "",
        "",
        "WEB RESEARCH EVIDENCE PROVIDED BY THE DESIGN WORKBENCH:",
        (
            "Treat these as external reference evidence only. "
            "Do not claim facts beyond the supplied snippets/URLs. "
            "Use them to understand current market patterns, "
            "visual references and competitor conventions; "
            "do not copy a competitor."
        ),
        "",
    ]

    for index, item in enumerate(
        results[:8],
        start=1,
    ):
        title = str(
            item.get(
                "title",
                "",
            )
        ).strip()

        url = str(
            item.get(
                "url",
                "",
            )
        ).strip()

        description = str(
            item.get(
                "description",
                "",
            )
        ).strip()

        lines.extend([
            f"[{index}] {title}",
            f"URL: {url}",
            f"Snippet: {description}",
            "",
        ])

    return "\n".join(lines)


def update_job(
    job_id: str,
    **values,
) -> None:
    with LOCK:
        current = JOBS.get(job_id)

        if not current:
            return

        current.update(values)


def append_output(
    job_id: str,
    line: str,
) -> None:
    with LOCK:
        current = JOBS.get(job_id)

        if not current:
            return

        tail = (
            current.get(
                "output_tail",
                ""
            )
            + line
        )

        # Keep UI polling payload bounded.
        current["output_tail"] = (
            tail[-16000:]
        )


def run_factory_job(
    job_id: str,
    prompt: str,
    search_results: list[dict],
    design_context: DesignContext | None = None,
    mode: str = "build",
    engine: str = "template",
) -> None:
    run_dir = RUNS / job_id

    enriched_prompt = (
        prompt.strip()
        + format_research(
            search_results
        )
    )

    update_job(
        job_id,
        status="running",
        started_at=time.time(),
    )

    command = [
        sys.executable,
        str(
            ROOT
            / "run.py"
        ),
        enriched_prompt,
        "--run-id", job_id,
        "--engine", engine,
    ]

    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        context_path = run_dir / "design-context.json"
        context_path.write_text((design_context or DesignContext()).model_dump_json(indent=2), encoding="utf-8")
        command.extend(["--context", str(context_path)])
        if mode == "intelligence":
            command.append("--intelligence-only")
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
        )

        assert process.stdout is not None

        for line in process.stdout:
            append_output(
                job_id,
                line,
            )

        return_code = (
            process.wait()
        )

        summary = read_run_summary(
            run_dir
        )

        project_slug = project_slug_from_run(run_dir) if mode == "build" and summary.get("artifacts", {}).get("implementation") else None

        if (
            return_code == 0
            and summary.get(
                "status"
            ) == "completed"
        ):
            update_job(
                job_id,
                status="completed",
                return_code=return_code,
                completed_at=time.time(),
                run_id=(
                    run_dir.name
                    if run_dir
                    else None
                ),
                project_slug=(
                    project_slug
                ),
            )
            return

        error_message = (
            summary.get(
                "errors"
            )
            or (
                f"Factory exited with "
                f"code {return_code}"
            )
        )

        update_job(
            job_id,
            status="failed",
            return_code=return_code,
            completed_at=time.time(),
            run_id=(
                run_dir.name
                if run_dir
                else None
            ),
            project_slug=(
                project_slug
            ),
            error=str(
                error_message
            ),
        )

    except Exception as error:
        update_job(
            job_id,
            status="failed",
            completed_at=time.time(),
            error=(
                f"{type(error).__name__}: "
                f"{error}"
            ),
        )


class Handler(
    BaseHTTPRequestHandler
):
    server_version = (
        "UIUXFactoryBridge/1.0"
    )

    def log_message(
        self,
        format,
        *args,
    ):
        sys.stdout.write(
            "[bridge] "
            + format % args
            + "\n"
        )

    def cors(
        self,
    ):
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

    def send_json(
        self,
        payload: dict,
        status=200,
    ):
        body = json_bytes(
            payload
        )

        self.send_response(
            status
        )
        self.cors()
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(
            body
        )

    def do_OPTIONS(
        self,
    ):
        self.send_response(
            HTTPStatus.NO_CONTENT
        )
        self.cors()
        self.end_headers()

    def do_POST(
        self,
    ):
        origin = self.headers.get("Origin")
        if origin and origin not in ALLOWED_ORIGINS:
            self.send_json({"error": "This origin is not allowed to start local Factory jobs."}, status=403)
            return
        parsed = urlparse(
            self.path
        )

        if parsed.path not in {"/run", "/intelligence"}:
            self.send_json(
                {
                    "error": "Not found"
                },
                status=404,
            )
            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            if length <= 0 or length > 12_000_000:
                self.send_json({"error": "Request must contain JSON and be at most 12 MB."}, status=413)
                return

            body = self.rfile.read(
                length
            )

            payload = json.loads(
                body.decode(
                    "utf-8"
                )
            )
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")

        except Exception:
            self.send_json(
                {
                    "error": (
                        "Invalid JSON body"
                    )
                },
                status=400,
            )
            return

        prompt = str(
            payload.get(
                "prompt",
                "",
            )
        ).strip()

        if not prompt:
            self.send_json(
                {
                    "error": (
                        "Prompt is required"
                    )
                },
                status=400,
            )
            return

        search_results = (
            payload.get(
                "search_results"
            )
            or []
        )

        if not isinstance(
            search_results,
            list,
        ):
            search_results = []

        search_results = [item for item in search_results[:8] if isinstance(item, dict)]
        try:
            design_context = DesignContext.model_validate(payload.get("design_context", {}))
        except ValidationError as error:
            self.send_json({"error": "; ".join(f"{'.'.join(map(str, item['loc']))}: {item['msg']}" for item in error.errors(include_input=False))}, status=400)
            return
        mode = "intelligence" if parsed.path == "/intelligence" else "build"
        engine = payload.get("engine", "template")
        if engine not in ("template", "ai"):
            self.send_json({"error": "Unknown generation engine"}, status=400)
            return
        if mode == "build" and engine == "ai":
            from core.runtime.free_provider import FreeProvider, ProviderError
            try:
                FreeProvider.from_env(ROOT)
            except ProviderError as error:
                self.send_json({"error": str(error)}, status=400)
                return

        job_id = (
            uuid.uuid4().hex[:12]
        )

        job = {
            "id": job_id,
            "status": "queued",
            "prompt": prompt,
            "created_at": time.time(),
            "output_tail": "",
            "mode": mode,
            "engine": engine,
        }

        with LOCK:
            JOBS[job_id] = job

        thread = threading.Thread(
            target=run_factory_job,
            args=(
                job_id,
                prompt,
                search_results,
                design_context,
                mode,
                engine,
            ),
            daemon=True,
        )

        response_job = dict(job)
        thread.start()

        self.send_json(
            response_job,
            status=202,
        )

    def do_GET(
        self,
    ):
        parsed = urlparse(
            self.path
        )

        if parsed.path == "/health":
            from core.runtime.free_provider import FreeProvider, ProviderError
            try:
                provider = FreeProvider.from_env(ROOT)
                ai = {"configured": True, "providers": [config.name for config in provider.configs]}
            except ProviderError:
                ai = {"configured": False, "providers": []}
            self.send_json(
                {
                    "status": "ok",
                    "ai": ai,
                    "root": str(ROOT),
                    "python": sys.executable,
                    "generated": str(
                        GENERATED
                    ),
                }
            )
            return

        if parsed.path.startswith(
            "/jobs/"
        ):
            import re
            artifact_match = re.fullmatch(r"/jobs/([a-f0-9]{12})/artifacts/(.+)", parsed.path)
            if artifact_match:
                job_id, filename = artifact_match.groups()
                if filename not in {"design-system.json", "reference-dna.json", "DESIGN.md", "tokens.css", "quality-loop.json", "browser-report.json"} and not re.fullmatch(r"references/reference-[a-f0-9]{12}-(desktop|mobile)\.png", filename):
                    self.send_json({"error": "Unknown artifact"}, status=404)
                    return
                run_root = (RUNS / job_id).resolve()
                target = (run_root / filename).resolve()
                if not target.is_relative_to(run_root) or not target.is_file():
                    self.send_json({"error": "Artifact is not available yet"}, status=404)
                    return
                body = target.read_bytes()
                self.send_response(200)
                self.cors()
                content_type = {".png": "image/png", ".md": "text/plain; charset=utf-8", ".css": "text/css; charset=utf-8"}.get(target.suffix, "application/json; charset=utf-8")
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            job_id = (
                parsed.path
                .split(
                    "/",
                    2,
                )[-1]
            )

            with LOCK:
                job = (
                    JOBS.get(
                        job_id
                    )
                )

                if job:
                    payload = dict(
                        job
                    )
                else:
                    payload = None

            if not payload:
                self.send_json(
                    {
                        "error": (
                            "Unknown job"
                        )
                    },
                    status=404,
                )
                return

            summary = read_run_summary(RUNS / job_id)
            payload["active_stage"] = summary.get("active_stage")
            payload["completed_stages"] = summary.get("completed_stages", [])
            payload["artifacts"] = [Path(path).name for name, path in summary.get("artifacts", {}).items()
                                    if name in {"design_system", "reference_analysis"}]

            self.send_json(
                payload
            )
            return

        if parsed.path == "/latest":
            run_dir = latest_run()

            self.send_json(
                {
                    "run_id": (
                        run_dir.name
                        if run_dir
                        else None
                    ),
                    "run": (
                        read_run_summary(
                            run_dir
                        )
                    ),
                    "project_slug": (
                        project_slug_from_run(
                            run_dir
                        )
                    ),
                }
            )
            return

        if parsed.path.startswith(
            "/preview/"
        ):
            self.serve_preview(
                parsed.path
            )
            return

        self.send_json(
            {
                "error": "Not found"
            },
            status=404,
        )

    def serve_preview(
        self,
        request_path: str,
    ):
        relative = unquote(
            request_path[
                len(
                    "/preview/"
                ):
            ]
        )

        parts = [
            part
            for part in relative.split(
                "/"
            )
            if part
        ]

        if not parts:
            self.send_error(
                404
            )
            return

        project_slug = parts[0]
        project_root = (
            GENERATED
            / project_slug
        ).resolve()

        if not (
            GENERATED.exists()
            and project_root.is_relative_to(
                GENERATED.resolve()
            )
            and project_root.exists()
        ):
            self.send_error(
                404
            )
            return

        rest = parts[
            1:
        ]

        target = (
            project_root
            / (
                Path(
                    *rest
                )
                if rest
                else Path(
                    "index.html"
                )
            )
        ).resolve()

        if (
            target.is_dir()
        ):
            target = (
                target
                / "index.html"
            )

        if not target.is_relative_to(
            project_root
        ):
            self.send_error(
                403
            )
            return

        if not target.exists():
            # Handle clean route URLs.
            clean_candidate = (
                project_root
                / Path(
                    *rest
                )
                / "index.html"
                if rest
                else (
                    project_root
                    / "index.html"
                )
            ).resolve()

            if (
                clean_candidate.is_relative_to(
                    project_root
                )
                and clean_candidate.exists()
            ):
                target = (
                    clean_candidate
                )
            else:
                self.send_error(
                    404
                )
                return

        content_type = (
            mimetypes.guess_type(
                str(target)
            )[0]
            or "application/octet-stream"
        )

        body = target.read_bytes()

        self.send_response(
            200
        )
        self.cors()
        if (project_root / ".uiux-ai.json").is_file():
            from core.actions.generate_ai_frontend import AI_PREVIEW_CSP
            self.send_header("Content-Security-Policy", AI_PREVIEW_CSP)
        self.send_header(
            "Content-Type",
            content_type,
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(
            body
        )


def main():
    server = ThreadingHTTPServer(
        (
            HOST,
            PORT,
        ),
        Handler,
    )

    print()
    print("=" * 72)
    print(
        "UIUX FACTORY - DESIGN WORKBENCH BRIDGE"
    )
    print("=" * 72)
    print(
        f"[Factory] {ROOT}"
    )
    print(
        f"[Python] {sys.executable}"
    )
    print(
        f"[Bridge] http://{HOST}:{PORT}"
    )
    print(
        "[Endpoints] /health /run /intelligence /jobs/<id> /jobs/<id>/artifacts/<file> /latest /preview/<project>/"
    )
    print("=" * 72)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
