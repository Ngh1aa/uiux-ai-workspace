#!/usr/bin/env python3
"""Verify exact optional font files/licenses and Vietnamese cmap; tooling only."""
import hashlib
import json
from pathlib import Path
import sys
import struct


def has_glyph(data, codepoint):
    """Read Unicode cmap formats 4/12 in these original TrueType assets (not a shaper)."""
    u16 = lambda offset: struct.unpack_from(">H", data, offset)[0]
    i16 = lambda offset: struct.unpack_from(">h", data, offset)[0]
    u32 = lambda offset: struct.unpack_from(">I", data, offset)[0]
    count = u16(4)
    cmap = next(u32(12 + index * 16 + 8) for index in range(count)
                if data[12 + index * 16:16 + index * 16] == b"cmap")
    for index in range(u16(cmap + 2)):
        record = cmap + 4 + index * 8
        platform, encoding = u16(record), u16(record + 2)
        if platform != 0 and not (platform == 3 and encoding in (1, 10)):
            continue
        table = cmap + u32(record + 4)
        format_ = u16(table)
        if format_ == 12:
            for group in range(u32(table + 12)):
                position = table + 16 + group * 12
                first, last, glyph = struct.unpack_from(">III", data, position)
                if first <= codepoint <= last and glyph + codepoint - first:
                    return True
        if format_ == 4 and codepoint <= 0xffff:
            segments = u16(table + 6) // 2
            ends = table + 14
            starts = ends + segments * 2 + 2
            deltas = starts + segments * 2
            ranges = deltas + segments * 2
            for segment in range(segments):
                first, last = u16(starts + segment * 2), u16(ends + segment * 2)
                if first <= codepoint <= last:
                    delta, span = i16(deltas + segment * 2), u16(ranges + segment * 2)
                    glyph = (codepoint + delta) & 0xffff if not span else u16(ranges + segment * 2 + span + (codepoint - first) * 2)
                    if span and glyph:
                        glyph = (glyph + delta) & 0xffff
                    if glyph:
                        return True
    return False


def check(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1] / "fonts"
    rows = []
    for item in json.loads((root / "manifest.json").read_text(encoding="utf-8"))["fonts"]:
        file = root / item["file"]
        license_file = root / item["license"]
        data = file.read_bytes()
        missing = sorted({c for c in item["glyph_probe"] if not c.isspace() and not has_glyph(data, ord(c))})
        valid_hash = hashlib.sha256(file.read_bytes()).hexdigest() == item["sha256"]
        valid_license = (hashlib.sha256(license_file.read_bytes()).hexdigest() == item["license_sha256"]
                         and "SIL OPEN FONT LICENSE" in license_file.read_text(encoding="utf-8").upper())
        rows.append({"family": item["family"], "status": "PASS" if not missing and valid_hash and valid_license else "FAIL",
                     "missing_glyphs": missing, "binary_hash": valid_hash, "license": valid_license})
    return {"status": "PASS" if rows and all(row["status"] == "PASS" for row in rows) else "FAIL", "fonts": rows}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit({"PASS": 0, "FAIL": 1, "UNKNOWN": 2}[result["status"]])
