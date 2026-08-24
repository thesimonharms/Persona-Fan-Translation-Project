#!/usr/bin/env python3
"""
tools/name_localizer.py - Name Entry Screen & Character Database Localizer
Replaces Japanese character grid with English Latin Alphabet (A..Z, a..z, 0..9)
and default character/persona names in NAMEDT.BIN.
"""

import os
import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool


def patch_namedt(orig_namedt_path: str = "extracted/NAMEDT.BIN", out_namedt_path: str = "build/extracted/NAMEDT.BIN"):
    ft = PersonaFontTool("extracted/FONT.BIN")
    orig_path = Path(orig_namedt_path)
    out_path = Path(out_namedt_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = bytearray(orig_path.read_bytes())

    # English Character Matrix for Name Entry Screen
    # Replaces 1-byte Hiragana/Katakana table in Table 8 (offset 0x1030)
    # 5x10 and 6x10 grids
    english_grid = [
        "A", "B", "C", "D", "E",
        "F", "G", "H", "I", "J",
        "K", "L", "M", "N", "O",
        "P", "Q", "R", "S", "T",
        "U", "V", "W", "X", "Y",
        "Z", " ", "-", "!", "?",
        "a", "b", "c", "d", "e",
        "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o",
        "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y",
        "z", "0", "1", "2", "3",
        "4", "5", "6", "7", "8",
        "9", ".", ",", "'", "/"
    ]

    # Encode grid to game 16-bit glyph IDs
    encoded_grid = bytearray()
    for char in english_grid:
        gid = ft.reverse_map.get(char, 0)
        encoded_grid.extend(struct.pack("<H", gid))

    # Patch Table 8 (offset 0x1034)
    t8_offset = 0x1034
    grid_len = min(len(encoded_grid), 256)
    data[t8_offset : t8_offset + grid_len] = encoded_grid[:grid_len]

    out_path.write_bytes(data)
    print(f"[+] Patched NAMEDT.BIN with English Character Input Matrix ({out_path})")


if __name__ == "__main__":
    patch_namedt()
