#!/usr/bin/env python3
"""
tools/font_tool.py - Persona Font Engine & Lowercase ASCII Injector
Reverse-engineers FONT.BIN (16x16 1-bpp monochrome bitmaps) and injects crisp
lowercase English glyphs at safe 1-byte high offsets (Glyph 218..243 / 0x80DA..0x80F3)
and 2-byte space at Glyph 217 (0x80D9) to prevent premature null string termination.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

GLYPH_SIZE_BYTES = 32
TOTAL_GLYPHS = 2048

# Safe glyph ID mapping for lowercase English letters (Glyph 218 to 243)
LOWERCASE_BASE_GLYPH_ID = 218
SPACE_GLYPH_ID = 217  # 0x80D9 (Blank 16x16 space)

LOWERCASE_GLYPH_BITMAPS = {
    'a': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1E00, 0x0300, 0x1F00, 0x3300, 0x3300, 0x1F80, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'b': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x3E00, 0x2300, 0x2300, 0x2300, 0x2300, 0x3E00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'c': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1E00, 0x2100, 0x2000, 0x2000, 0x2100, 0x1E00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'd': [0x0000, 0x0300, 0x0300, 0x0300, 0x0300, 0x1F00, 0x3300, 0x3300, 0x3300, 0x3300, 0x1F80, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'e': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1E00, 0x2100, 0x3F00, 0x2000, 0x2100, 0x1E00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'f': [0x0000, 0x0C00, 0x1200, 0x1000, 0x1000, 0x3C00, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'g': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1F00, 0x3300, 0x3300, 0x3300, 0x1F00, 0x0300, 0x3300, 0x1E00, 0x0000, 0x0000, 0x0000],
    'h': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x3E00, 0x2300, 0x2300, 0x2300, 0x2300, 0x2300, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'i': [0x0000, 0x1000, 0x0000, 0x0000, 0x0000, 0x3000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3800, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'j': [0x0000, 0x0800, 0x0000, 0x0000, 0x0000, 0x1800, 0x0800, 0x0800, 0x0800, 0x0800, 0x0800, 0x8800, 0x7000, 0x0000, 0x0000, 0x0000],
    'k': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x2600, 0x2C00, 0x3800, 0x2C00, 0x2600, 0x2300, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'l': [0x0000, 0x3000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3800, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'm': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3700, 0x4980, 0x4980, 0x4980, 0x4980, 0x4980, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'n': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3E00, 0x2300, 0x2300, 0x2300, 0x2300, 0x2300, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'o': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1E00, 0x2100, 0x2100, 0x2100, 0x2100, 0x1E00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'p': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3E00, 0x2300, 0x2300, 0x2300, 0x3E00, 0x2000, 0x2000, 0x2000, 0x0000, 0x0000, 0x0000],
    'q': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1F00, 0x3300, 0x3300, 0x3300, 0x1F00, 0x0300, 0x0300, 0x0300, 0x0000, 0x0000, 0x0000],
    'r': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2F00, 0x3180, 0x2000, 0x2000, 0x2000, 0x2000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    's': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1E00, 0x2100, 0x1800, 0x0600, 0x2100, 0x1E00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    't': [0x0000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3C00, 0x1000, 0x1000, 0x1000, 0x1200, 0x0C00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'u': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2300, 0x2300, 0x2300, 0x2300, 0x2300, 0x1E80, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'v': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2200, 0x2200, 0x1400, 0x1400, 0x0800, 0x0800, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'w': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x4480, 0x4480, 0x4480, 0x2A80, 0x2A80, 0x1100, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'x': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2200, 0x1400, 0x0800, 0x0800, 0x1400, 0x2200, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
    'y': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2300, 0x2300, 0x2300, 0x1F00, 0x0300, 0x3300, 0x1E00, 0x0000, 0x0000, 0x0000, 0x0000],
    'z': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3F00, 0x0600, 0x0C00, 0x1800, 0x3000, 0x3F00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]
}


class PersonaFontTool:
    def __init__(self, font_bin_path: str = "extracted/FONT.BIN", tbl_path: Optional[str] = None):
        self.font_path = Path(font_bin_path)
        self.font_data = bytearray(self.font_path.read_bytes()) if self.font_path.is_file() else bytearray(TOTAL_GLYPHS * GLYPH_SIZE_BYTES)
        self.char_map: Dict[int, str] = {}
        self.reverse_map: Dict[str, int] = {}
        self._load_table_mapping(tbl_path)

    def _load_table_mapping(self, tbl_path: Optional[str] = None):
        base_tbl = Path("docs/tbl/persona_font.json")
        if base_tbl.is_file():
            raw = json.loads(base_tbl.read_text(encoding="utf-8"))
            for gid_str, char in raw.items():
                if gid_str.isdigit():
                    gid = int(gid_str)
                    self.char_map[gid] = char
                    self.reverse_map[char] = gid

        # 2-byte Space at safe Glyph 217 (0x80D9)
        self.char_map[SPACE_GLYPH_ID] = " "
        self.reverse_map[" "] = SPACE_GLYPH_ID

        # Lowercase letters at safe offsets 218..243
        for idx, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            gid = LOWERCASE_BASE_GLYPH_ID + idx
            self.char_map[gid] = letter
            self.reverse_map[letter] = gid

        # Uppercase letters
        for idx, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            gid = 166 + idx
            self.char_map[gid] = letter
            self.reverse_map[letter] = gid

        # Numbers
        for idx, num in enumerate("0123456789"):
            gid = 192 + idx
            self.char_map[gid] = num
            self.reverse_map[num] = gid

        # Punctuation
        self.char_map[208] = "?"
        self.reverse_map["?"] = 208
        self.char_map[209] = "!"
        self.reverse_map["!"] = 209
        self.char_map[198] = "."
        self.reverse_map["."] = 198
        self.char_map[199] = ","
        self.reverse_map[","] = 199
        self.char_map[205] = "-"
        self.reverse_map["-"] = 205
        self.char_map[200] = "'"
        self.reverse_map["'"] = 200

    def patch_font_with_lowercase(self, out_path: str = "build/extracted/FONT.BIN"):
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        patched_data = bytearray(self.font_data)

        # Clear space glyph
        space_offset = SPACE_GLYPH_ID * GLYPH_SIZE_BYTES
        patched_data[space_offset : space_offset + GLYPH_SIZE_BYTES] = b"\x00" * GLYPH_SIZE_BYTES

        # Inject lowercase bitmaps
        for letter, rows in LOWERCASE_GLYPH_BITMAPS.items():
            gid = self.reverse_map[letter]
            glyph_offset = gid * GLYPH_SIZE_BYTES
            glyph_bytes = bytearray()
            for row in rows:
                glyph_bytes.append((row >> 8) & 0xFF)
                glyph_bytes.append(row & 0xFF)
            patched_data[glyph_offset : glyph_offset + GLYPH_SIZE_BYTES] = glyph_bytes

        out_p.write_bytes(patched_data)
        print(f"[+] Patched FONT.BIN (Safe lowercase 218..243, Safe 2-byte space 217) -> {out_p}")

    def encode_text(self, text: str) -> bytes:
        out = bytearray()
        i = 0
        while i < len(text):
            if text[i] == "<":
                end_tag = text.find(">", i)
                if end_tag != -1:
                    tag = text[i : end_tag + 1]
                    if tag == "<PAGE>":
                        out.extend(b"\xff\xf6")
                    elif tag == "<LINE>":
                        out.extend(b"\xff\xf5")
                    elif tag == "<CLOSE>":
                        out.extend(b"\xff\xfc")
                    elif tag == "<END>":
                        out.extend(b"\xff\xfe")
                    elif tag.startswith("<CHOICE"):
                        out.extend(b"\xff\xf3\x00")
                    elif tag.startswith("<CMD_"):
                        hex_code = tag[5:-1]
                        try:
                            val = int(hex_code, 16)
                            out.extend(bytes([0xFF, val]))
                        except ValueError:
                            pass
                    i = end_tag + 1
                    continue

            c = text[i]
            gid = self.reverse_map.get(c)
            if gid is None:
                gid = self.reverse_map.get(c.upper(), SPACE_GLYPH_ID)

            hi = 0x80 | ((gid >> 8) & 0x07)
            lo = gid & 0xFF
            out.extend(bytes([hi, lo]))
            i += 1
        return bytes(out)

    def decode_bytes(self, data: bytes) -> str:
        chars = []
        i = 0
        while i < len(data):
            b1 = data[i]
            if b1 == 0x00:
                chars.append(" ")
                i += 1
            elif b1 == 0xFF and i + 1 < len(data):
                b2 = data[i + 1]
                if b2 == 0xF6:
                    chars.append("<PAGE>")
                elif b2 == 0xF5:
                    chars.append("<LINE>")
                elif b2 == 0xFC:
                    chars.append("<CLOSE>")
                elif b2 == 0xFE:
                    chars.append("<END>")
                elif b2 == 0xF3:
                    chars.append("<CHOICE>")
                    if i + 2 < len(data):
                        i += 1
                else:
                    chars.append(f"<CMD_{b2:02x}>")
                i += 2
            elif 0x80 <= b1 <= 0x87 and i + 1 < len(data):
                b2 = data[i + 1]
                gid = ((b1 - 0x80) << 8) | b2
                chars.append(self.char_map.get(gid, f"[G:{gid}]"))
                i += 2
            elif b1 < 128:
                chars.append(self.char_map.get(b1, chr(b1) if 32 <= b1 <= 126 else f"\\x{b1:02x}"))
                i += 1
            else:
                i += 1
        return "".join(chars)


if __name__ == "__main__":
    ft = PersonaFontTool()
    ft.patch_font_with_lowercase()
