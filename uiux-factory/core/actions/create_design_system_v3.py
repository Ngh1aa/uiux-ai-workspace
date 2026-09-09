"""Enrich the existing system contract; keep V2 consumers and gates intact."""

import base64
import hashlib
import io
import json
import re
from collections import Counter

from PIL import Image

from core.actions.create_design_system import CreateDesignSystem
from core.contracts.design_context_schema import BrandDNA, DesignContext, DesignObservation, ReferenceBoard
from core.contracts.design_system_schema import DesignSystemContract, PatternContract, TokenValue


# Explicit role mappings; an arbitrary color occurrence is never a brand primary.
TOKEN_ROLES = {
    "colors": {"primary": "color.brand.primary", "accent": "color.brand.accent"},
    "typography": {"heading": "font.family.display", "body": "font.family.body"},
    "radius": {"card": "radius.lg", "button": "radius.md"},
    "motion": {"style": "motion.style", "duration": "motion.duration.base"},
}
CSS_ROLES = {
    "brand-primary": ("colors", "color.brand.primary"),
    "color-primary": ("colors", "color.brand.primary"),
    "color-brand-primary": ("colors", "color.brand.primary"),
    "brand-accent": ("colors", "color.brand.accent"),
    "color-accent": ("colors", "color.brand.accent"),
    "font-heading": ("typography", "font.family.display"),
    "font-body": ("typography", "font.family.body"),
    "font-family-display": ("typography", "font.family.display"),
    "font-family-body": ("typography", "font.family.body"),
    "radius-card": ("radius", "radius.lg"),
    "radius-button": ("radius", "radius.md"),
    "motion-duration": ("motion", "motion.duration.base"),
}


def safe_token(group: str, name: str, value: object) -> str:
    text = str(value).strip()
    if not text or len(text) > 250 or re.search(r"[;{}<>\\\r\n]|url\s*\(|/\*", text, re.I):
        raise ValueError(f"Unsafe or empty token: {name}")
    if group == "colors" and not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", text):
        raise ValueError(f"{name} requires an opaque HEX color (#RGB or #RRGGBB).")
    if group == "typography" and "family" in name and not re.fullmatch(r"[\w\s,'\".-]+", text):
        raise ValueError(f"{name} requires a font-family name or stack.")
    if group in {"radius", "spacing", "layout"} and not re.fullmatch(r"(?:0|\d+(?:\.\d+)?(?:px|rem|em|%|vw))", text):
        raise ValueError(f"{name} requires a non-negative CSS length.")
    if group == "motion" and "duration" in name and not re.fullmatch(r"\d+(?:\.\d+)?m?s", text):
        raise ValueError(f"{name} requires a duration such as 180ms.")
    return text


def color_hex(value: str) -> str | None:
    if re.fullmatch(r"#[0-9a-fA-F]{3}", value):
        return "#" + "".join(char * 2 for char in value[1:]).upper()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.upper()
    match = re.fullmatch(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", value)
    if match and all(int(part) <= 255 for part in match.groups()):
        return "#" + "".join(f"{int(part):02X}" for part in match.groups())
    return None


def companion_color(value: str, target: int, amount: float) -> str:
    value = color_hex(value)
    return "#" + "".join(f"{round(int(value[index:index + 2], 16) * (1 - amount) + target * amount):02X}" for index in (1, 3, 5))


def luminance(value: str) -> float:
    value = color_hex(value)
    channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= .04045 else ((channel + .055) / 1.055) ** 2.4 for channel in channels]
    return sum(channel * weight for channel, weight in zip(linear, (.2126, .7152, .0722)))


class CreateDesignSystemV3(CreateDesignSystem):
    name: str = "CreateDesignSystemV3"

    @staticmethod
    def enrich(system: DesignSystemContract, context: DesignContext, board: ReferenceBoard) -> DesignSystemContract:
        brand = BrandDNA(
            name=context.brand_name,
            personality=context.personality,
            avoid=context.avoid,
            source_context_sha256=hashlib.sha256(context.model_dump_json().encode()).hexdigest(),
            source_status=("supplied_guideline" if context.guideline or context.tokens else
                           "partial_assets" if context.assets or context.existing_code or context.existing_website else
                           "no_brand_evidence"),
        )
        system.schema_version = "0.3.0"
        system.generated_by = "DesignSystemArchitect"
        system.brand = brand
        if context.assets and all(asset.kind == "logo" for asset in context.assets) and not any((context.guideline, context.tokens, context.existing_code, context.existing_website)):
            system.unresolved_items.append("PROPOSED BRAND GUIDELINE — LOGO-DERIVED. Sampled logo colors are evidence only; visual rules still require brand review.")
        assigned: dict[str, TokenValue] = {}

        def assign(group: str, name: str, raw: object, source: str, status: str = "derived"):
            value = safe_token(group, name, raw)
            previous = assigned.get(name)
            if previous and previous.value != value:
                brand.conflicts.append(f"{name}: {previous.value} ({previous.source}) replaced by {value} ({source}).")
            token = TokenValue(value=value, status=status, source=source)
            getattr(system.foundations, group)[name] = token
            assigned[name] = token

        # Existing site can establish observed digital values, never official brand status.
        for reference in board.references:
            brand.reference_patterns.extend(f"{reference.url}: {pattern}" for pattern in reference.patterns)
            if reference.role != "existing_website":
                continue
            for observation in reference.observations:
                if "@ 1440x1000" not in observation.source:
                    continue
                mapping = {
                    "body[0].font-family": ("typography", "font.family.body"),
                    "h1[0].font-family": ("typography", "font.family.display"),
                }.get(observation.subject)
                if mapping:
                    try:
                        assign(*mapping, observation.value, observation.source)
                    except ValueError as error:
                        system.unresolved_items.append(str(error))
                if observation.subject == "body[0].background-color":
                    value = color_hex(observation.value)
                    if value:
                        brand.evidence.append(observation)

        css = re.sub(r"/\*.*?\*/", "", context.existing_code, flags=re.S)
        for match in re.finditer(r"--([\w-]+)\s*:\s*([^;{}]+)", css):
            mapping = CSS_ROLES.get(match[1])
            if mapping:
                try:
                    assign(*mapping, match[2], f"existing_code: --{match[1]}")
                except ValueError as error:
                    system.unresolved_items.append(str(error))

        # A deliberately bounded parser: labels are authoritative; unlabeled prose stays context.
        labels = {
            "primary": ("colors", "color.brand.primary"), "accent": ("colors", "color.brand.accent"),
            "heading font": ("typography", "font.family.display"), "body font": ("typography", "font.family.body"),
            "card radius": ("radius", "radius.lg"), "motion": ("motion", "motion.style"),
        }
        for line in context.guideline.splitlines():
            key, separator, value = line.partition(":")
            if separator and key.strip().lower() in labels:
                assign(*labels[key.strip().lower()], value, f"guideline: {key.strip()}", "confirmed")
        if context.guideline:
            system.unresolved_items.append("Guideline prose is retained as context; only supported labeled values were extracted. Verify remaining rules manually.")

        imported = context.tokens
        foundations = imported.get("foundations", {})
        if not isinstance(foundations, dict):
            raise ValueError("tokens.foundations must be an object.")
        for group in ("colors", "typography", "radius", "motion", "spacing", "layout"):
            values = foundations.get(group, {})
            if not isinstance(values, dict):
                raise ValueError(f"tokens.foundations.{group} must be an object.")
            for name, raw in values.items():
                if name == "color.brand.family":
                    continue
                if not re.fullmatch(r"[a-z][a-z0-9.-]{0,100}", name):
                    raise ValueError(f"Invalid token name: {name}")
                value = raw.get("value") if isinstance(raw, dict) else raw
                if value is not None:
                    status = raw.get("status", "confirmed") if isinstance(raw, dict) else "confirmed"
                    assign(group, name, value, f"imported foundations.{group}.{name}", status)
        for group, mapping in TOKEN_ROLES.items():
            values = imported.get(group, {})
            if not isinstance(values, dict):
                raise ValueError(f"tokens.{group} must be an object.")
            for label, name in mapping.items():
                if label in values:
                    raw = values[label]
                    assign(group, name, raw.get("value") if isinstance(raw, dict) else raw,
                           f"explicit tokens.{group}.{label}", "confirmed")
        imported_brand = imported.get("brand", {})
        if isinstance(imported_brand, dict) and not brand.personality:
            personality = imported_brand.get("personality", [])
            if not isinstance(personality, list) or any(not isinstance(item, str) for item in personality):
                raise ValueError("tokens.brand.personality must be a list of strings.")
            brand.personality = DesignContext(personality=personality).personality

        # Raster palette evidence is useful, but does not determine a semantic primary or exact font.
        for asset in context.assets:
            raw = base64.b64decode(asset.data_url.split(",", 1)[1])
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    if image.width * image.height > 20_000_000:
                        raise ValueError("Image exceeds 20 megapixels.")
                    image.load()
                    sample = image.convert("RGBA")
                    sample.thumbnail((128, 128))
                    pixels = sample.load()
                    opaque = [pixels[x, y][:3] for y in range(sample.height) for x in range(sample.width) if pixels[x, y][3] >= 240]
                    colors = ["#%02X%02X%02X" % rgb for rgb, _count in Counter(opaque).most_common(5)]
                    brand.evidence.append(DesignObservation(
                        category="asset", subject=f"{asset.kind}: {asset.name}",
                        value=f"{image.width}x{image.height}; sampled colors: {', '.join(colors)}",
                        source=f"uploaded asset sha256:{hashlib.sha256(raw).hexdigest()}",
                    ))
            except (OSError, Image.DecompressionBombError) as error:
                raise ValueError(f"Cannot decode image {asset.name}.") from error
            system.unresolved_items.append(f"{asset.name}: sampled palette only; logo geometry, font identity and screenshot layout require visual review.")

        if "color.brand.accent" in assigned:
            system.foundations.semantic_colors["brand.accent"] = "color.brand.accent"
        if "color.brand.primary" in assigned:
            system.unresolved_items = [item for item in system.unresolved_items if item != "Exact primary brand color token / HEX."]
            primary = str(assigned["color.brand.primary"].value)
            for name, value in {"color.brand.deep": companion_color(primary, 0, .75),
                                "color.brand.subtle": companion_color(primary, 255, .92)}.items():
                if name not in assigned:
                    assign("colors", name, value, "Proposed digital companion derived from supplied primary")
            foreground = "#FFFFFF" if 1.05 / (luminance(primary) + .05) >= (luminance(primary) + .05) / .05 else "#000000"
            assign("colors", "color.text.on-brand", foreground, "Derived foreground with the stronger sRGB contrast against supplied primary")
            system.foundations.semantic_colors["text.on-brand"] = "color.text.on-brand"
            if 1.05 / (luminance(primary) + .05) < 4.5:
                system.unresolved_items.append("Primary color has insufficient contrast for normal text on white. Review link/text roles separately from the brand asset.")
        if "font.family.body" in assigned:
            system.unresolved_items = [item for item in system.unresolved_items
                                       if item != "Final body typography family with Vietnamese coverage verification."]
            system.unresolved_items.append("Verify supplied font availability, licensing and Vietnamese glyph coverage in the rendered site.")
        system.patterns.append(PatternContract(
            name="BrandDNA", purpose="Preserve brand constraints through composition and implementation.",
            rules=[f"Personality: {', '.join(brand.personality) or 'UNKNOWN'}", *[f"Avoid: {item}" for item in brand.avoid]],
        ))
        if brand.reference_patterns:
            system.patterns.append(PatternContract(name="ReferenceDNA", purpose="Measured reference principles for calibration.",
                                                  rules=brand.reference_patterns))
        system.unresolved_items = list(dict.fromkeys(system.unresolved_items))
        # Importing evidence is never an approval or rendered accessibility verification.
        system.gates.final_visual_lock = False
        return system

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        baseline = DesignSystemContract.model_validate_json(await super().run(instruction))
        context = DesignContext.model_validate(payload.get("design_context", {}))
        board = ReferenceBoard.model_validate(payload.get("reference_board", {}))
        return self.enrich(baseline, context, board).model_dump_json(indent=2)
