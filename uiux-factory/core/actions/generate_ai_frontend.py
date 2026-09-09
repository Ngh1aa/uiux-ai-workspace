"""Validated static file bundles from the configured coder, without a layout template."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.runtime.workspace_writer import WorkspaceWriter


AI_PREVIEW_CSP = (
    "default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; script-src 'self'; connect-src 'none'; base-uri 'none'; "
    "form-action 'none'; frame-src 'none'; sandbox allow-scripts"
)


class DesignPage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    title: str = Field(min_length=1, max_length=160)
    purpose: str = Field(min_length=1, max_length=600)
    sections: list[str] = Field(min_length=1, max_length=14)

    @field_validator("path")
    @classmethod
    def valid_path(cls, value: str) -> str:
        if not re.fullmatch(r"(?:[a-z0-9][a-z0-9-]{0,35}/){0,2}index\.html", value):
            raise ValueError("Page path must be index.html or a safe route/index.html")
        return value


class DesignBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")
    direction: str = Field(min_length=1, max_length=3000)
    pages: list[DesignPage] = Field(min_length=1, max_length=10)
    unknowns: list[str] = Field(default_factory=list, max_length=30)
    proposed_tokens: dict[str, str] = Field(default_factory=dict, max_length=3)


class FileBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    files: dict[str, str] = Field(min_length=2, max_length=13)


class HTMLContract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.counts: dict[str, int] = {}
        self.viewport = False
        self.language = False

    def handle_starttag(self, tag, attrs):
        self.counts[tag] = self.counts.get(tag, 0) + 1
        values = dict(attrs)
        if tag in {"iframe", "frame", "object", "embed", "base", "foreignobject"}:
            raise ValueError(f"Unsupported embedded element: {tag}")
        if any(key.lower().startswith("on") for key, _ in attrs):
            raise ValueError("Inline event handlers are not supported; use app.js")
        if tag == "script" and not re.fullmatch(r"(?:\.\./){0,2}app\.js", values.get("src") or ""):
            raise ValueError("Only the local app.js script is supported")
        if tag == "meta" and values.get("http-equiv"):
            raise ValueError("Model-generated HTTP metadata is not supported")
        if tag == "html":
            self.language = bool(values.get("lang"))
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.viewport = "width=device-width" in values.get("content", "")
        for key in ("href", "src", "action", "formaction", "xlink:href"):
            value = (values.get(key) or "").strip().lower()
            if re.match(r"(?:javascript|vbscript):", value) or (value.startswith("data:") and not value.startswith("data:image/")):
                raise ValueError("Unsafe URL in generated HTML")

    handle_startendtag = handle_starttag


def validate_bundle(raw: str, brief: DesignBrief) -> FileBundle:
    bundle = FileBundle.model_validate_json(raw)
    pages = {page.path for page in brief.pages}
    if "index.html" not in pages or len(pages) != len(brief.pages):
        raise ValueError("Plan requires a unique home page and unique routes")
    allowed = pages | {"styles.css", "app.js"}
    if set(bundle.files) - allowed or not pages.issubset(bundle.files) or "styles.css" not in bundle.files:
        raise ValueError("Generated files do not match the approved route plan")
    if sum(len(value) for value in bundle.files.values()) > 650_000:
        raise ValueError("Generated file bundle exceeds 650 KB")
    for path in pages:
        document = HTMLContract()
        document.feed(bundle.files[path])
        if not document.language or not document.viewport or any(document.counts.get(tag) != 1 for tag in ("html", "head", "title", "body", "main", "h1")):
            raise ValueError(f"{path}: requires lang, viewport and exactly one html/head/title/body/main/h1")
        if "</head>" not in bundle.files[path].lower():
            raise ValueError(f"{path}: missing closing head")
    css = bundle.files["styles.css"]
    if "@import" in css.lower() or re.search(r"--color-brand-primary\s*:", css):
        raise ValueError("CSS must preserve brand tokens and use local assets")
    if "var(--color-brand-primary" not in css or ":focus-visible" not in css or "@media" not in css:
        raise ValueError("CSS requires the brand primary token, keyboard focus and responsive rules")
    return bundle


def write_bundle(root: Path, slug: str, bundle: FileBundle, tokens: str) -> Path:
    canonical = set(re.findall(r"(--[a-z0-9-]+)\s*:", tokens))
    overridden = canonical.intersection(re.findall(r"(--[a-z0-9-]+)\s*:", bundle.files["styles.css"]))
    if overridden:
        raise ValueError("Generated CSS overrides canonical tokens: " + ", ".join(sorted(overridden)))
    writer = WorkspaceWriter(root)
    for name, content in bundle.files.items():
        if name.endswith("index.html"):
            prefix = "../" * (len(PurePosixPath(name).parts) - 1)
            links = f'<link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}tokens.css">'
            content = re.sub(r"</head>", lambda _: links + "</head>", content, count=1, flags=re.I)
        writer.write_text(slug, name, content)
    writer.write_text(slug, "tokens.css", tokens)
    if "app.js" not in bundle.files:
        writer.write_text(slug, "app.js", "// This draft does not require JavaScript.\n")
    writer.write_text(slug, ".uiux-ai.json", json.dumps({"engine": "ai", "quality_loop_required": True}))
    return writer.project_root(slug)


CODER_CONTRACT = """
Generate a distinctive, premium, complete static HTML/CSS/JS website for the supplied approved plan. Do not fall back to a generic commerce/SaaS template.
Return only JSON {"files":{"index.html":"...","styles.css":"...","app.js":"..."}}.
Include every approved plan path exactly. Optional app.js; no other files, build tools or dependencies.
Every page: html lang, meaningful title, viewport width=device-width, exactly one main and one h1. Use semantic landmarks and logical heading order.
Use relative navigation to approved route/index.html paths. No dead # links; section links require real IDs.
No remote assets, embeds, inline event handlers, inline scripts, forms that submit, or network requests. Scripts may load only relative app.js.
The host inserts relative links to styles.css and authoritative tokens.css for every page.
CSS must use var(--color-brand-primary), visible :focus-visible states and substantial responsive @media rules. Respect reduced-motion preferences for non-essential motion.
Do not redefine canonical tokens or use @import. Do not conceal overflow globally to hide layout bugs.
Create page-role-specific compositions: vary hierarchy, density and visual rhythm by purpose instead of repeating one hero/card grid everywhere.
Use editorial whitespace, deliberate typography, responsive grids, restrained motion and a recognizable visual signature appropriate to the supplied brand/personality.
Never invent testimonials, ratings, customer counts, awards, client logos, guarantees, prices, delivery claims, certifications, statistics or business facts. If evidence is unknown, omit it or label neutral placeholder content honestly.
Do not present fake controls or success states as functional backend behavior. Static prototype interactions must be truthful and accessible.
Prioritize mobile hierarchy, keyboard usability, readable contrast, touch target spacing and content clarity over decorative effects.
""".strip()
