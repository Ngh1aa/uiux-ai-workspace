"""Kiểm tra cấu trúc PNG không cần thư viện ngoài (tách từ uiux-factory evidence)."""
from __future__ import annotations

import struct
import zlib


def _valid_png(raw: bytes) -> bool:
    """Check PNG structure, CRCs, decoded size and row filters without optional dependencies."""
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset = 8
    kinds: list[bytes] = []
    compressed = bytearray()
    expected_bytes = 0
    row_sizes = []
    while offset + 12 <= len(raw):
        size = struct.unpack(">I", raw[offset:offset + 4])[0]
        end = offset + size + 12
        if end > len(raw):
            return False
        kind = raw[offset + 4:offset + 8]
        payload = raw[offset + 8:offset + 8 + size]
        checksum = struct.unpack(">I", raw[end - 4:end])[0]
        if checksum != zlib.crc32(kind + payload):
            return False
        if not kinds:
            if kind != b"IHDR" or size != 13:
                return False
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if (not width or not height or depth not in depths.get(color, set())
                    or compression or filtering or interlace not in {0, 1}):
                return False
            channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
            passes = ((0, 0, 1, 1),) if not interlace else (
                (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
                (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2),
            )
            for x, y, dx, dy in passes:
                columns = max(0, (width - x + dx - 1) // dx)
                rows = max(0, (height - y + dy - 1) // dy)
                if columns and rows:
                    row_size = 1 + (columns * channels * depth + 7) // 8
                    row_sizes.append((row_size, rows))
                    expected_bytes += row_size * rows
        kinds.append(kind)
        if kind == b"IDAT":
            compressed.extend(payload)
        if kind == b"IEND":
            if size or end != len(raw) or not compressed:
                return False
            # Stream output in bounded chunks; full-page captures may be tall.
            decoder = zlib.decompressobj()
            remaining = bytes(compressed)
            decoded_bytes = 0
            lengths = (size for size, rows in row_sizes for _ in range(rows))
            next_filter = 0
            try:
                while remaining:
                    block = decoder.decompress(remaining, 1024 * 1024)
                    end_bytes = decoded_bytes + len(block)
                    if end_bytes > expected_bytes:
                        return False
                    while next_filter < end_bytes:
                        if block[next_filter - decoded_bytes] > 4:
                            return False
                        next_filter += next(lengths)
                    decoded_bytes = end_bytes
                    remaining = decoder.unconsumed_tail
            except zlib.error:
                return False
            return decoder.eof and not decoder.unused_data and decoded_bytes == expected_bytes
        offset = end
    return False
