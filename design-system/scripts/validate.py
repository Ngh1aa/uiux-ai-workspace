#!/usr/bin/env python3
"""Validate the design system: token format, architecture rules, contrast and CSS hygiene.

    python3 design-system/scripts/validate.py [--report]

Checks (each failure names the token or file):
  1. DTCG 2025.10 shape per $type (color components/hex agree, dimension units, cubicBezier range...).
  2. Every alias resolves, no cycles, every token has a determinable $type.
  3. Mode parity: every mode defines exactly the same semantic paths.
  4. Layering: semantic colors alias primitives (no literals); component tokens never alias
     primitive colors directly; nothing outside the primitive layer holds a raw color literal.
  5. Contrast: every pair in contrast-pairs.json meets its minimum in every mode.
  6. CSS hygiene: component CSS has no color literals, no primitive palette vars, and only
     references custom properties that exist in generated/tokens.css.
  7. Generated files are up to date (same check as build.py --check).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dslib import (ROOT, TYPES, TokenError, alias_target, color_hex, contrast,  # noqa: E402
                   css_name, load_config, mode_tokens, resolve)

HEX = re.compile(r"^#[0-9a-f]{6}$")
COLOR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\(", re.I)
VAR_USE = re.compile(r"var\((--[a-z0-9-]+)")


def check_shape(path: str, ttype: str, v, errors: list[str]) -> None:
    if alias_target(v):
        return
    def err(msg):
        errors.append(f"{path}: {msg}")
    if ttype not in TYPES:
        return err(f"unknown $type '{ttype}'")
    if ttype == "color":
        if not isinstance(v, dict) or v.get("colorSpace") != "srgb":
            return err("color must be an object with colorSpace 'srgb'")
        comps = v.get("components")
        if not (isinstance(comps, list) and len(comps) == 3 and all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in comps)):
            return err("srgb components must be three numbers in [0, 1]")
        if "alpha" in v and not (0 <= v["alpha"] <= 1):
            err("alpha must be in [0, 1]")
        if "hex" in v:
            if not HEX.match(v["hex"]):
                err("hex must be #rrggbb lowercase")
            elif any(abs(round(c * 255) - int(v["hex"][i:i + 2], 16)) > 1 for c, i in zip(comps, (1, 3, 5))):
                err(f"hex {v['hex']} disagrees with components {comps}")
    elif ttype == "dimension":
        if not (isinstance(v, dict) and set(v) == {"value", "unit"} and v["unit"] in {"px", "rem"}
                and isinstance(v["value"], (int, float))):
            err("dimension must be {value:number, unit:'px'|'rem'}")
    elif ttype == "duration":
        if not (isinstance(v, dict) and set(v) == {"value", "unit"} and v["unit"] in {"ms", "s"} and v["value"] >= 0):
            err("duration must be {value:>=0, unit:'ms'|'s'}")
    elif ttype == "cubicBezier":
        if not (isinstance(v, list) and len(v) == 4 and 0 <= v[0] <= 1 and 0 <= v[2] <= 1):
            err("cubicBezier must be [x1,y1,x2,y2] with x in [0,1]")
    elif ttype == "fontWeight":
        if not (isinstance(v, (int, float)) and 1 <= v <= 1000):
            err("fontWeight must be a number in [1, 1000]")
    elif ttype == "fontFamily":
        if not (isinstance(v, str) or (isinstance(v, list) and v and all(isinstance(x, str) for x in v))):
            err("fontFamily must be a string or non-empty string array")
    elif ttype == "number":
        if not isinstance(v, (int, float)):
            err("number must be numeric")
    elif ttype == "typography":
        need = {"fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing"}
        if not (isinstance(v, dict) and need <= set(v)):
            err(f"typography needs {sorted(need)}")
    elif ttype == "shadow":
        items = v if isinstance(v, list) else [v]
        for s in items:
            if not (isinstance(s, dict) and {"color", "offsetX", "offsetY", "blur", "spread"} <= set(s)):
                err("shadow layers need color, offsetX, offsetY, blur, spread")


def layer_of(path: str, layers: dict) -> str:
    head = path.split(".")[0]
    for name, heads in layers.items():
        if head in heads:
            return name
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print every contrast pair with its ratio")
    args = ap.parse_args()
    cfg = load_config()
    layers = cfg["layers"]
    errors: list[str] = []
    warnings: list[str] = []
    resolved_by_mode = {}
    tokens_by_mode = {}

    for mode in cfg["modes"]:
        try:
            toks = mode_tokens(mode)
            res = resolve(toks)
        except TokenError as exc:
            errors.append(f"[{mode}] {exc}")
            continue
        tokens_by_mode[mode], resolved_by_mode[mode] = toks, res
        for path, tok in toks.items():
            ttype = res[path][0]
            check_shape(path, ttype, tok.value, errors)
            layer = layer_of(path, layers)
            if layer == "unknown":
                errors.append(f"{path}: top-level group '{path.split('.')[0]}' is not assigned to a layer in build.config.json")
            target = alias_target(tok.value)
            if ttype == "color" and layer != "primitive" and target is None:
                errors.append(f"{path}: {layer} color holds a literal; alias a primitive instead")
            if layer == "component" and target and target.startswith("color."):
                errors.append(f"{path}: component token aliases primitive '{target}'; alias a semantic role")
            if layer == "semantic" and ttype == "color" and target and layer_of(target, layers) != "primitive":
                errors.append(f"{path}: semantic color must alias a primitive, not '{target}'")
            if target and tokens_by_mode[mode].get(target) and tokens_by_mode[mode][target].deprecated:
                warnings.append(f"{path}: references deprecated token '{target}'")

    # 3. mode parity
    mode_sets = {m: {p for p, t in tokens_by_mode[m].items() if t.source in cfg["modes"][m]} for m in tokens_by_mode}
    if mode_sets:
        ref_mode = cfg["default_mode"]
        for m, paths in mode_sets.items():
            missing = mode_sets[ref_mode] - paths
            extra = paths - mode_sets[ref_mode]
            for p in sorted(missing):
                errors.append(f"[{m}] missing mode token '{p}' (defined in {ref_mode})")
            for p in sorted(extra):
                errors.append(f"[{m}] extra mode token '{p}' (absent in {ref_mode})")

    # 5. contrast
    pairs = json.loads((ROOT / "contrast-pairs.json").read_text(encoding="utf-8"))["pairs"]
    rows = []
    for mode, res in resolved_by_mode.items():
        for pair in pairs:
            fg, bg = res.get(pair["fg"]), res.get(pair["bg"])
            if not fg or not bg:
                errors.append(f"contrast pair {pair['fg']} on {pair['bg']}: unknown token")
                continue
            ratio = contrast(color_hex(fg[1]), color_hex(bg[1]))
            ok = ratio + 1e-9 >= pair["min"]
            rows.append((mode, pair["fg"], pair["bg"], ratio, pair["min"], ok))
            if not ok:
                errors.append(f"[{mode}] contrast {pair['fg']} on {pair['bg']} = {ratio:.2f}:1 < {pair['min']}:1 ({pair['why']})")

    # 6. CSS hygiene
    generated_css = (ROOT / cfg["outputs"]["css"]).read_text(encoding="utf-8") if (ROOT / cfg["outputs"]["css"]).exists() else ""
    defined = set(re.findall(r"(--[a-z0-9-]+):", generated_css))
    for rel in cfg.get("lint_css", []):
        text = (ROOT / rel).read_text(encoding="utf-8")
        local_defs = set(re.findall(r"(--[a-z0-9-]+):", text))
        for lineno, line in enumerate(text.splitlines(), 1):
            code = re.sub(r"/\*.*?\*/", "", line)
            if COLOR_LITERAL.search(code):
                errors.append(f"{rel}:{lineno}: color literal; use a semantic token")
            for var in VAR_USE.findall(code):
                if var.startswith(f"--{cfg['prefix']}-color-"):
                    errors.append(f"{rel}:{lineno}: uses primitive palette {var}; use a semantic role")
                elif var.startswith(f"--{cfg['prefix']}-") and var not in defined:
                    errors.append(f"{rel}:{lineno}: {var} is not defined in {cfg['outputs']['css']}")
                elif not var.startswith(f"--{cfg['prefix']}-") and var not in local_defs:
                    errors.append(f"{rel}:{lineno}: {var} is neither a token nor defined locally")

    # 7. generated up to date
    import subprocess
    build = subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--check"], capture_output=True, text=True)
    if build.returncode != 0:
        errors.append(build.stderr.strip() or "generated files are stale")

    if args.report:
        for mode, fg, bg, ratio, need, ok in rows:
            print(f"{'PASS' if ok else 'FAIL'}  {mode:5}  {ratio:5.2f}:1 (min {need})  {fg}  on  {bg}")
    for w in warnings:
        print(f"WARNING: {w}")
    n_tokens = len(next(iter(tokens_by_mode.values()), {}))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"design system validation FAILED with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"design system valid: {n_tokens} tokens per mode, {len(cfg['modes'])} modes, "
          f"{len(rows)} contrast checks, {len(cfg.get('lint_css', []))} CSS file(s) linted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
