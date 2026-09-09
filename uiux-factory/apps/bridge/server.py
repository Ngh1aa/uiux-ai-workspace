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

from apps.bridge.creative_review import build_review_pack
from apps.bridge.job_runtime import (
    BoundedJobExecutor,
    JobStore,
    QueueFullError,
    run_process_streaming,
    validate_job_id,
)
from core.contracts.creative_review_schema import CreativeDirective
from core.contracts.design_context_schema import DesignContext
from core.runtime.harness_runtime import HarnessInspiredRuntime


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
RUNTIME = HarnessInspiredRuntime(ROOT)

ARTIFACT_NAMES = {
    "design-contract.json",
    "design-system.json",
    "implementation-plan.json",
    "visual-composition.json",
    "visual-brain.json",
    "reference-dna.json",
    "DESIGN.md",
    "tokens.css",
    "quality-loop.json",
    "browser-report.json",
    "creative-directive.json",
    "creative-revision.json",
    "runtime-composition.json",
    "flow-plan.json",
    "events.jsonl",
}
REFERENCE_ARTIFACT_RE = re.compile(
    r"references/reference-[a-f0-9]{12}-(desktop|mobile)\.png"
)


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def runtime_preset_inventory() -> list[dict]:
    return [
        {
            "id": preset.preset_id,
            "name": preset.name,
            "description": preset.description,
            "trust": preset.trust,
        }
        for preset in RUNTIME.catalog.list()
    ]


def validate_runtime_preset(value: object) -> str:
    preset_id = str(value or "standard").strip() or "standard"
    active = RUNTIME.compose(preset_id)
    try:
        return active.preset.preset_id
    finally:
        active.registry.unmount_all()


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

    for filename in ARTIFACT_NAMES:
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


def _run_command(job_id: str, command: list[str], mode: str = "build") -> None:
    run_dir = RUNS / job_id
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
        if mode != "intelligence" and (summary.get("artifacts") or {}).get("implementation")
        else None
    )
    common = {
        "return_code": result.return_code,
        "completed_at": time.time(),
        "run_id": run_dir.name,
        "project_slug": project_slug,
        "runtime_preset": summary.get("runtime_preset"),
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


def run_factory_job(
    job_id: str,
    prompt: str,
    search_results: list[dict],
    design_context: DesignContext | None = None,
    mode: str = "build",
    engine: str = "template",
    runtime_preset: str = "standard",
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
            "--runtime-preset",
            runtime_preset,
            "--context",
            str(context_path),
        ]
        if mode == "intelligence":
            command.append("--intelligence-only")

        _run_command(job_id, command, mode)
    except Exception as error:
        STORE.update(
            job_id,
            status="failed",
            completed_at=time.time(),
            error=f"{type(error).__name__}: {error}",
        )


def run_creative_revision_job(
    job_id: str,
    source_run_id: str,
    directive: CreativeDirective,
    engine: str,
) -> None:
    run_dir = RUNS / job_id
    STORE.update(job_id, status="running", started_at=time.time())

    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        directive_path = run_dir / "creative-directive-input.json"
        directive_path.write_text(directive.model_dump_json(indent=2), encoding="utf-8")
        command = [
            sys.executable,
            str(ROOT / "run.py"),
            "--run-id",
            job_id,
            "--engine",
            engine,
            "--source-run-id",
            source_run_id,
            "--creative-directive",
            str(directive_path),
        ]
        _run_command(job_id, command, "creative_revision")
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
                runtime_preset=summary.get("runtime_preset"),
                recovered_after_restart=True,
            )
        elif summary.get("status") == "failed":
            STORE.update(
                job_id,
                status="failed",
                completed_at=time.time(),
                run_id=job_id,
                project_slug=project_slug,
                runtime_preset=summary.get("runtime_preset"),
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
                runtime_preset=summary.get("runtime_preset"),
                error=(
                    "Bridge restarted while this job was queued or running. "
                    "Partial run artifacts, if any, remain under runs/<job-id>."
                ),
                recovered_after_restart=True,
            )


class Handler(BaseHTTPRequestHandler):
    server_version = "UIUXFactoryBridge/1.3"

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

    def send_file(self, path: Path, content_type: str, download_name: str | None = None) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.cors()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if download_name:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self, max_bytes: int = 12_000_000) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > max_bytes:
                self.send_json(
                    {"error": f"Request must contain JSON and be at most {max_bytes} bytes."},
                    status=413,
                )
                return None
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")
            return payload
        except Exception:
            self.send_json({"error": "Invalid JSON body"}, status=400)
            return None

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
        creative_match = re.fullmatch(
            r"/jobs/([a-f0-9]{12})/creative-directive",
            parsed.path,
        )
        if creative_match:
            self.start_creative_revision(creative_match.group(1))
            return

        if parsed.path not in {"/run", "/intelligence"}:
            self.send_json({"error": "Not found"}, status=404)
            return

        payload = self.read_json_body()
        if payload is None:
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

        try:
            runtime_preset = validate_runtime_preset(payload.get("runtime_preset", "standard"))
        except (KeyError, ValueError, RuntimeError, FileNotFoundError) as error:
            self.send_json({"error": f"Invalid runtime preset: {error}"}, status=400)
            return

        if mode == "build" and engine == "ai" and not self.ai_ready():
            return

        job_id = uuid.uuid4().hex[:12]
        job = {
            "id": job_id,
            "status": "queued",
            "prompt": prompt,
            "created_at": time.time(),
            "mode": mode,
            "engine": engine,
            "runtime_preset": runtime_preset,
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
                runtime_preset,
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

    def ai_ready(self) -> bool:
        from core.runtime.free_provider import FreeProvider, ProviderError

        try:
            FreeProvider.from_env(ROOT)
            return True
        except ProviderError as error:
            self.send_json({"error": str(error)}, status=400)
            return False

    def start_creative_revision(self, source_run_id: str) -> None:
        source_job = STORE.snapshot(source_run_id)
        source_summary = read_run_summary(RUNS / source_run_id)
        if not source_job or source_summary.get("status") != "completed":
            self.send_json(
                {"error": "Creative review can only revise a completed source run."},
                status=409,
            )
            return

        payload = self.read_json_body(max_bytes=2_000_000)
        if payload is None:
            return

        try:
            directive = CreativeDirective.model_validate(payload)
        except ValidationError as error:
            message = "; ".join(
                f"{'.'.join(map(str, item['loc']))}: {item['msg']}"
                for item in error.errors(include_input=False)
            )
            self.send_json({"error": message}, status=400)
            return

        if directive.source_run_id != source_run_id:
            self.send_json({"error": "Directive source_run_id does not match this run."}, status=400)
            return
        if directive.status != "revise" or not directive.revise:
            self.send_json(
                {"error": "This directive contains no revision work. Approved reviews need no rebuild."},
                status=409,
            )
            return

        engine = str(source_job.get("engine", "template"))
        if engine == "ai" and not self.ai_ready():
            return

        job_id = uuid.uuid4().hex[:12]
        target = directive.earliest_owner()
        runtime_preset = str(source_summary.get("runtime_preset") or source_job.get("runtime_preset") or "standard")
        job = {
            "id": job_id,
            "status": "queued",
            "prompt": f"Creative revision of {source_run_id} from {target}",
            "created_at": time.time(),
            "mode": "creative_revision",
            "engine": engine,
            "runtime_preset": runtime_preset,
            "source_run_id": source_run_id,
            "revision_target": target,
        }

        try:
            response_job = STORE.create(job)
            EXECUTOR.submit(
                run_creative_revision_job,
                job_id,
                source_run_id,
                directive,
                engine,
            )
        except QueueFullError as error:
            STORE.update(job_id, status="failed", completed_at=time.time(), error=str(error))
            self.send_json({"error": str(error), "job_id": job_id}, status=429)
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
                    "runtime_presets": runtime_preset_inventory(),
                    "creative_review": {
                        "review_pack": True,
                        "stage_aware_revision": True,
                    },
                    "jobs": {
                        "max_workers": MAX_WORKERS,
                        "max_queue": MAX_QUEUE,
                        "timeout_seconds": JOB_TIMEOUT_SECONDS,
                        "persistent": True,
                    },
                }
            )
            return

        if parsed.path in {"/inspiration", "/api/inspiration"}:
            self.send_json(
                {
                    "patterns": [
                        {
                            "id": "bento-grid",
                            "name": "Bento Grid Showcase",
                            "category": "Layout & Composition",
                            "description": "Linear / Apple-style asymmetric modular tiles with rounded borders and subtle glows.",
                            "keywords": ["bento", "card grid", "modular", "feature showcase"],
                            "preview_accent": "#6366f1"
                        },
                        {
                            "id": "aurora-gradient",
                            "name": "Aurora & Mesh Glow",
                            "category": "Visual Craft",
                            "description": "Deep obsidian canvas blended with organic, diffuse color meshes (violet, cyan, amber).",
                            "keywords": ["mesh gradient", "glow", "dark luxury", "fintech"],
                            "preview_accent": "#ec4899"
                        },
                        {
                            "id": "glassmorphism",
                            "name": "Frosted Glass & Depth",
                            "category": "Surface & Depth",
                            "description": "Layered cards with backdrop-blur, semi-transparent borders, and multi-elevation soft shadows.",
                            "keywords": ["glassmorphism", "backdrop-blur", "translucent", "depth"],
                            "preview_accent": "#06b6d4"
                        },
                        {
                            "id": "micro-motion",
                            "name": "Signature Micro-Interactions",
                            "category": "Motion & Delight",
                            "description": "Magnetic buttons, pill badges with hover shine, fluid accordion toggles, and state transitions.",
                            "keywords": ["microinteractions", "smooth transitions", "hover shine", "interactive"],
                            "preview_accent": "#10b981"
                        },
                        {
                            "id": "fluid-typography",
                            "name": "Editorial Fluid Typography",
                            "category": "Typography",
                            "description": "Dynamic clamp-scaled titles paired with clean high-contrast sans-serif body fonts.",
                            "keywords": ["fluid typography", "clamp()", "editorial hierarchy", "contrast"],
                            "preview_accent": "#f59e0b"
                        }
                    ]
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
        review_match = re.fullmatch(r"/jobs/([a-f0-9]{12})/review-pack", path)
        if review_match:
            self.serve_review_pack(review_match.group(1))
            return True

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
        payload["runtime_preset"] = summary.get("runtime_preset") or payload.get("runtime_preset") or "standard"
        payload["artifacts"] = available_artifacts(job_id, summary)
        payload["creative_review_ready"] = (
            payload.get("status") == "completed"
            and payload.get("mode") != "intelligence"
            and bool(payload.get("project_slug"))
        )
        self.send_json(payload)
        return True

    def serve_review_pack(self, job_id: str) -> None:
        job = STORE.snapshot(job_id)
        summary = read_run_summary(RUNS / job_id)
        if not job or job.get("status") != "completed" or summary.get("status") != "completed":
            self.send_json({"error": "Review pack is available after a completed build."}, status=409)
            return
        try:
            pack = build_review_pack(
                RUNS / job_id,
                job,
                project_slug_from_run(RUNS / job_id),
            )
        except Exception as error:
            self.send_json({"error": f"Could not build review pack: {error}"}, status=500)
            return
        self.send_file(pack, "application/zip", f"uiux-review-pack-{job_id}.zip")

    def serve_artifact(self, job_id: str, filename: str) -> None:
        if not is_allowed_artifact_name(filename):
            self.send_json({"error": "Unknown artifact"}, status=404)
            return

        run_root = (RUNS / job_id).resolve()
        target = (run_root / filename).resolve()
        if not target.is_relative_to(run_root) or not target.is_file():
            self.send_json({"error": "Artifact is not available yet"}, status=404)
            return

        content_type = {
            ".png": "image/png",
            ".md": "text/plain; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".jsonl": "application/x-ndjson; charset=utf-8",
        }.get(target.suffix.lower(), "application/json; charset=utf-8")
        self.send_file(target, content_type)

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
        "/jobs/<id>/review-pack /jobs/<id>/creative-directive "
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
