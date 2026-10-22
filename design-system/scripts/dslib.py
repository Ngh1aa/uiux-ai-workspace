"""Shared loader/resolver for DTCG 2025.10 token files. Standard library only.

Terminology follows the Design Tokens Format Module 2025.10: a token is an object with
`$value`; groups may set `$type`, inherited by nested tokens; `{a.b}` aliases a whole token.
Modes are not part of the format, so each mode is a separate file set with identical paths.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALIAS = re.compile(r"^\{([^{}]+)\}$")
TYPES = {"color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier",
         "number", "shadow", "typography", "strokeStyle", "border", "transition", "gradient"}


class TokenError(Exception):
    pass


@dataclass
class Token:
    path: str
    type: str | None
    value: object
    source: str
    description: str = ""
    deprecated: object = False
    extra: dict = field(default_factory=dict)


def load_config(root: Path = ROOT) -> dict:
    return json.loads((root / "build.config.json").read_text(encoding="utf-8"))


def _merge(into: dict, new: dict, where: str, prefix: str = "") -> None:
    for key, val in new.items():
        if key.startswith("$"):
            if prefix and key in into and into[key] != val and key not in {"$description"}:
                raise TokenError(f"{where}: conflicting {key} on group '{prefix}'")
            into.setdefault(key, val)
            continue
        path = f"{prefix}.{key}" if prefix else key
        if key in into:
            if isinstance(into[key], dict) and "$value" not in into[key] and isinstance(val, dict) and "$value" not in val:
                _merge(into[key], val, where, path)
            else:
                raise TokenError(f"{where}: token '{path}' is defined twice")
        else:
            into[key] = val


def load_tree(files: list[str], root: Path = ROOT) -> tuple[dict, dict[str, str]]:
    tree: dict = {}
    origin: dict[str, str] = {}
    for rel in files:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
        data = {k: v for k, v in data.items() if not (k == "$description")}
        _merge(tree, data, rel)
        for path in _walk_paths(data):
            origin[path] = rel
    return tree, origin


def _walk_paths(node: dict, prefix: str = ""):
    for key, val in node.items():
        if key.startswith("$") or not isinstance(val, dict):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if "$value" in val:
            yield path
        else:
            yield from _walk_paths(val, path)


def flatten(tree: dict, origin: dict[str, str]) -> dict[str, Token]:
    out: dict[str, Token] = {}

    def walk(node: dict, prefix: str, inherited: str | None):
        group_type = node.get("$type", inherited)
        for key, val in node.items():
            if key.startswith("$"):
                continue
            if not isinstance(val, dict):
                raise TokenError(f"'{prefix}.{key}' is neither a token nor a group")
            if key.startswith("$") or any(c in key for c in "{}."):
                raise TokenError(f"invalid token/group name '{key}'")
            path = f"{prefix}.{key}" if prefix else key
            if "$value" in val:
                out[path] = Token(path, val.get("$type", group_type), val["$value"], origin.get(path, "?"),
                                  val.get("$description", ""), val.get("$deprecated", False),
                                  {k: v for k, v in val.items() if k == "$extensions"})
            else:
                walk(val, path, group_type)

    walk(tree, "", None)
    return out


def alias_target(value) -> str | None:
    if isinstance(value, str):
        m = ALIAS.match(value)
        return m.group(1) if m else None
    return None


def resolve(tokens: dict[str, Token]) -> dict[str, tuple[str, object]]:
    """Return path -> (type, fully resolved value). Raises on missing refs or cycles."""
    done: dict[str, tuple[str, object]] = {}

    def res_value(val, stack: tuple[str, ...]):
        target = alias_target(val)
        if target is not None:
            return res_token(target, stack)[1]
        if isinstance(val, dict):
            return {k: res_value(v, stack) for k, v in val.items()}
        if isinstance(val, list):
            return [res_value(v, stack) for v in val]
        return val

    def res_token(path: str, stack: tuple[str, ...]):
        if path in done:
            return done[path]
        if path in stack:
            raise TokenError("circular reference: " + " -> ".join(stack + (path,)))
        if path not in tokens:
            raise TokenError(f"unresolved reference '{{{path}}}' from '{stack[-1] if stack else '?'}'")
        tok = tokens[path]
        target = alias_target(tok.value)
        ttype = tok.type
        if ttype is None and target is not None:
            ttype = res_token(target, stack + (path,))[0]
        if ttype is None:
            raise TokenError(f"'{path}' has no $type and none can be inherited or resolved")
        value = res_value(tok.value, stack + (path,))
        done[path] = (ttype, value)
        return done[path]

    for p in tokens:
        res_token(p, ())
    return {p: done[p] for p in tokens}  # keep source declaration order


def mode_tokens(mode: str, root: Path = ROOT) -> dict[str, Token]:
    cfg = load_config(root)
    tree, origin = load_tree(cfg["base"] + cfg["modes"][mode], root)
    return flatten(tree, origin)


def css_name(path: str, prefix: str) -> str:
    return f"--{prefix}-" + path.replace(".", "-")


# ---------- color math (WCAG 2.x relative luminance) ----------

def hex_to_rgb(hx: str) -> tuple[float, float, float]:
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(rgb) -> float:
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a_hex: str, b_hex: str) -> float:
    la, lb = luminance(hex_to_rgb(a_hex)), luminance(hex_to_rgb(b_hex))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def color_hex(value: dict) -> str:
    if value.get("hex"):
        return value["hex"].lower()
    comps = value["components"]
    return "#" + "".join(f"{round(c * 255):02x}" for c in comps)
