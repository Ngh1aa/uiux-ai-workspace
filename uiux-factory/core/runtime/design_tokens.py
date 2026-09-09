"""The same canonical token output is consumed by static and Next frontends."""

import re

from core.contracts.design_system_schema import DesignSystemContract


def token_css(system: DesignSystemContract) -> str:
    declarations = []
    for group in ("colors", "typography", "spacing", "radius", "border", "elevation", "motion", "layout"):
        for name, token in getattr(system.foundations, group).items():
            if token.value is None or name == "color.brand.family":
                continue
            value = str(token.value)
            if not re.fullmatch(r"[a-z][a-z0-9.-]+", name) or re.search(r"[;{}<>\\\r\n]|url\s*\(|/\*", value, re.I):
                raise ValueError(f"Unsafe CSS token: {name}")
            declarations.append(f"  --{name.replace('.', '-')}: {value};")
    for role, name in system.foundations.semantic_colors.items():
        if not re.fullmatch(r"[a-z][a-z0-9.-]+", role) or not re.fullmatch(r"[a-z][a-z0-9.-]+", name):
            raise ValueError("Invalid semantic token reference")
        declarations.append(f"  --{role.replace('.', '-')}: var(--{name.replace('.', '-')});")
    return ":root {\n" + "\n".join(declarations) + "\n}\n"


def system_styles(system: DesignSystemContract) -> str:
    rules = [token_css(system)]
    if "color.brand.deep" in system.foundations.colors:
        rules.append(":root { --brand-900: var(--color-brand-deep); --brand-100: var(--color-brand-subtle); }")
        rules.append(".button--primary { color: var(--text-on-brand); }")
    if system.foundations.typography.get("font.family.body", None) and system.foundations.typography["font.family.body"].value:
        rules.append("body { font-family: var(--font-family-body), system-ui, sans-serif; }")
    if system.foundations.typography.get("font.family.display", None) and system.foundations.typography["font.family.display"].value:
        rules.append("h1, h2, h3 { font-family: var(--font-family-display), system-ui, sans-serif; }")
    rules.append(".product-card { border-radius: var(--radius-lg); }")
    rules.append(".button { border-radius: var(--radius-md); transition-duration: var(--motion-duration-base); }")
    rules.append("@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; } }")
    return "\n".join(rules) + "\n"
