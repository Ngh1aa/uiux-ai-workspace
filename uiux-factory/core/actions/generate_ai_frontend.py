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
        self.visible_text: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        self.counts[tag] = self.counts.get(tag, 0) + 1
        values = dict(attrs)
        if tag in {"head", "script", "style"}:
            self.hidden_depth += 1
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

    def handle_endtag(self, tag):
        if tag in {"head", "script", "style"}:
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_data(self, data):
        if not self.hidden_depth:
            self.visible_text.append(data)


def _css_blocks(css: str):
    """Yield balanced blocks, including nested rules; comments are already removed."""
    for match in re.finditer(r"([^{}]+)\{", css):
        depth = 1
        end = match.end()
        while end < len(css) and depth:
            depth += (css[end] == "{") - (css[end] == "}")
            end += 1
        if depth == 0:
            yield match.group(1).strip(), css[match.end():end - 1]


def _resolve_css_vars(value: str, variables: dict[str, str]) -> str:
    """Resolve local custom properties/fallbacks; external color tokens stay symbolic."""
    pattern = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)")
    for _ in range(12):
        resolved = pattern.sub(lambda match: variables.get(match[1], match[2] if match[2] is not None else match[0]), value)
        if resolved == value:
            break
        value = resolved
    # A locally declared reference left unresolved is cyclic, not a visible ring.
    if any(match[1] in variables for match in pattern.finditer(value)):
        return "none"
    return value.strip().lower()


def _focus_properties(body: str, variables: dict[str, str]) -> dict[str, str]:
    pairs = re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", body)
    variables = {**variables, **{key: value.strip() for key, value in pairs if key.startswith("--")}}
    properties: dict[str, str] = {}
    styles = {"none", "auto", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"}
    for key, raw in pairs:
        if key.startswith("--"):
            continue
        key = key.lower()
        value = _resolve_css_vars(re.sub(r"!important", "", raw, flags=re.I).strip(), variables)
        if key == "outline":
            # Shorthand resets all three longhands at this point in declaration order.
            outline = {"outline-width": "medium", "outline-style": "none", "outline-color": "currentcolor"}
            for token in re.findall(r"[a-z][\w-]*\([^)]*\)|[^\s]+", value):
                if token in styles:
                    outline["outline-style"] = token
                elif token in {"thin", "medium", "thick", "0"} or re.fullmatch(r"[\d.]+[a-z]+", token):
                    outline["outline-width"] = token
                else:
                    outline["outline-color"] = token
            properties.update(outline)
        properties[key] = value
    return properties


def _fully_clipped(properties: dict[str, str]) -> bool:
    clip = re.fullmatch(r"rect\(([^)]+)\)", properties.get("clip", ""))
    if clip and properties.get("position") in {"absolute", "fixed"}:
        edges = re.split(r"\s*,\s*|\s+", clip[1].strip())
        edges = ["0" if re.fullmatch(r"0(?:\.0+)?(?:[a-z]+)?", edge) else edge for edge in edges]
        if len(edges) == 4:
            zero_height = edges[0] == edges[2] and edges[0] != "auto"
            zero_width = edges[1] == edges[3] and edges[1] != "auto"
            if zero_height or zero_width:
                return True
    path = properties.get("clip-path", "")
    if re.match(r"(?:circle|ellipse)\(\s*0(?:\.0+)?(?:[a-z%]+)?(?:\s|\))", path):
        return True
    inset = re.fullmatch(r"inset\(([^)]+)\)", path)
    if inset:
        offsets = inset[1].split(" round ")[0].split()
        if 1 <= len(offsets) <= 4 and all(re.fullmatch(r"[\d.]+%", offset) for offset in offsets):
            values = [float(offset[:-1]) for offset in offsets]
            top, right, bottom, left = (values * 4)[:4] if len(values) <= 2 else (values + [values[1]])[:4]
            return top + bottom >= 100 or right + left >= 100
    return False


def bundle_quality_checks(bundle: FileBundle) -> dict[str, bool]:
    """Deterministic source checks, not computed-style or rendered WCAG certification."""
    documents = []
    semantic = True
    for path, source in bundle.files.items():
        if not path.endswith(".html"):
            continue
        document = HTMLContract()
        document.feed(source)
        documents.append(document)
        semantic = semantic and document.language and document.viewport and "</head>" in source.lower()
        semantic = semantic and all(document.counts.get(tag) == 1 for tag in ("html", "head", "title", "body", "main", "h1"))
    css = re.sub(r"/\*.*?\*/", "", bundle.files.get("styles.css", ""), flags=re.S)
    blocks = list(_css_blocks(css))
    responsive = any(selector.lower().startswith("@media") and re.search(r"(?:min|max)-width\s*:|\bwidth\s*[<>=]", selector)
                     and any(value.strip() for _key, value in re.findall(r"[^{]+\{\s*([\w-]+)\s*:\s*([^;{}]+)", body))
                     for selector, body in blocks)
    variables: dict[str, str] = {}
    for selector, body in blocks:
        if any(part.strip() in {":root", "html"} for part in selector.split(",")):
            variables.update((key, value.strip()) for key, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)", body))
    focus_declarations: dict[str, dict[str, str]] = {}
    for selector, body in blocks:
        if ":focus-visible" not in selector or selector.startswith("@") or re.search(r":not\([^)]*:focus-visible", selector):
            continue
        declarations = _focus_properties(body, variables)
        for individual in selector.split(","):
            if ":focus-visible" in individual:
                focus_declarations.setdefault(individual.strip(), {}).update(declarations)
    focus_rules = []
    baseline = {**focus_declarations.get(":focus-visible", {}), **focus_declarations.get("*:focus-visible", {})}
    for declarations in focus_declarations.values():
        declarations = {**baseline, **declarations}
        hidden = declarations.get("visibility") == "hidden" or declarations.get("display") == "none"
        hidden = hidden or bool(re.fullmatch(r"0(?:\.0+)?", declarations.get("opacity", "")))
        hidden = hidden or _fully_clipped(declarations)
        width = declarations.get("outline-width", "medium")
        style = declarations.get("outline-style", "none")
        color = declarations.get("outline-color", "currentcolor")
        shadow = declarations.get("box-shadow", "")
        invisible = r"(?:\bnone\b|\btransparent\b|rgba\([^)]*[,/]\s*0(?:\.0+)?\s*\)|#(?:[0-9a-f]{6}00|[0-9a-f]{3}0)\b)"
        numeric_width = re.fullmatch(r"(\d*\.\d+|\d+)(px|rem|em|pt|pc|in|cm|mm|q|vw|vh|vmin|vmax)", width)
        visible_outline = bool((width in {"thin", "medium", "thick"} or (numeric_width and float(numeric_width[1]) > 0))
                               and style in {"auto", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"}
                               and not re.search(invisible, color))
        visible_shadow = bool(re.search(r"(?:[1-9]\d*(?:\.\d+)?|0\.\d*[1-9]\d*)(?:px|rem|em)\b", shadow)
                              and not re.search(invisible, shadow))
        focus_rules.append(bool(not hidden and (visible_outline or visible_shadow)))
    text = " ".join(" ".join(document.visible_text) for document in documents).lower()
    technical = re.search(r"uiux\s*factory|metagpt|generated by|implemented (?:using|with)|factory placeholder|deterministic placeholder", text)
    return {
        "semantic_html_passed": bool(documents and semantic),
        "responsive_contract_passed": bool(responsive),
        "focus_contract_passed": bool(focus_rules and all(focus_rules)),
        "technical_copy_gate_passed": not bool(technical),
    }


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
    checks = bundle_quality_checks(bundle)
    failed = [name for name, passed in checks.items() if not passed]
    if "var(--color-brand-primary" not in css or failed:
        raise ValueError("Static frontend quality contract failed: " + ", ".join(failed or ["brand_primary_token"]))
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

CSS must use var(--color-brand-primary), :focus-visible and responsive @media rules.
Do not redefine tokens, use @import, conceal overflow globally or invent backend success states.
Use supplied brand fonts, colors and constraints. CSS artwork is acceptable if the brief needs it.

DESIGN QUALITY REQUIREMENTS (mandatory):
- Use fluid typography with clamp() for h1-h6 and body text.
- Add smooth CSS transitions on interactive elements (buttons, cards, links): transform, opacity, box-shadow.
- Use subtle hover effects: scale(1.02), translateY(-2px), shadow elevation changes.
- Implement scroll-margin-top for anchor navigation.
- Use modern CSS: gap in flex/grid, aspect-ratio for media, backdrop-filter for glass effects where appropriate.
- Create visual hierarchy with spacing rhythm (consistent vertical rhythm using multiples of 8px).
- Add :focus-visible outlines that match the brand color scheme.
- Use CSS custom properties for all repeated values (spacing, shadows, radii).
- Include at least one CSS animation (@keyframes) for hero or key section entrance.
- Cards and elevated surfaces should have subtle borders + shadows, not flat colors.
- Navigation should have backdrop-filter blur when sticky/fixed.
""".strip()
