#!/usr/bin/env python3
"""Generate an 11-step colour scale (50..950) in OKLCH and print it as sRGB hex or DTCG JSON.

Each step keeps the hue fixed and takes its lightness from a fixed ladder, so steps look evenly spaced.
Chroma follows a gentle arc (lower at both ends) and is reduced step by step until the colour fits sRGB.

    python3 design-system/scripts/oklch-scale.py --hue 165 --chroma 0.14
    python3 design-system/scripts/oklch-scale.py --hue 300 --chroma 0.12 --json teal

Python standard library only.
"""
from __future__ import annotations

import argparse
import json
import math

STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
LIGHTNESS = [0.975, 0.95, 0.9, 0.83, 0.74, 0.65, 0.555, 0.47, 0.39, 0.31, 0.22]
CHROMA_SHAPE = [0.12, 0.22, 0.42, 0.65, 0.88, 1.0, 1.0, 0.92, 0.8, 0.66, 0.5]


def oklch_to_linear_srgb(l: float, c: float, h: float) -> tuple[float, float, float]:
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (l - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )


def encode(v: float) -> float:
    v = min(1.0, max(0.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def in_gamut(rgb: tuple[float, float, float]) -> bool:
    return all(-1e-4 <= v <= 1 + 1e-4 for v in rgb)


def step_colour(l: float, c: float, h: float) -> tuple[float, tuple[float, float, float]]:
    """Return the chroma actually used and the gamma-encoded sRGB components."""
    while c > 0 and not in_gamut(oklch_to_linear_srgb(l, c, h)):
        c = round(c - 0.002, 4)
    rgb = oklch_to_linear_srgb(l, max(c, 0), h)
    return max(c, 0), tuple(round(encode(v), 4) for v in rgb)


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(v * 255):02x}" for v in rgb)


def scale(hue: float, chroma: float) -> list[dict]:
    out = []
    for step, l, k in zip(STEPS, LIGHTNESS, CHROMA_SHAPE):
        used, rgb = step_colour(l, chroma * k, hue)
        out.append({"step": step, "l": l, "c": used, "h": hue, "rgb": rgb, "hex": to_hex(rgb)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hue", type=float, required=True, help="OKLCH hue in degrees (0-360)")
    ap.add_argument("--chroma", type=float, default=0.14, help="peak chroma, 0.04 muted to 0.2 vivid")
    ap.add_argument("--json", metavar="NAME", help="print a DTCG colour group named NAME")
    args = ap.parse_args()

    rows = scale(args.hue % 360, args.chroma)
    if args.json:
        group = {"$type": "color"}
        group |= {
            str(r["step"]): {"$value": {"colorSpace": "srgb", "components": list(r["rgb"]), "hex": r["hex"]}}
            for r in rows
        }
        print(json.dumps({args.json: group}, indent=2))
    else:
        for r in rows:
            print(f"{r['step']:>4}  {r['hex']}  oklch({r['l']:.3f} {r['c']:.3f} {r['h']:.0f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
