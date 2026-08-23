#!/usr/bin/env python3
"""
tools/font_tool.py - Font and Character Mapping Table Tool for Megami Ibunroku Persona (PSX)
Parses FONT.BIN (2048 glyphs, 16x16 1-bpp monochrome font), maps characters (Gojuon, Katakana,
JIS X 0208 Level 1 Kanji, and English ASCII), and exports standard .tbl and .json mapping tables.
"""

import os
import sys
import json
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

GLYPH_WIDTH = 16
GLYPH_HEIGHT = 16
BYTES_PER_GLYPH = 32
TOTAL_GLYPHS = 2048

# Precise Character Mapping for Megami Ibunroku Persona (PSX)
NON_KANJI_TABLE: Dict[int, str] = {
    0: " ",
    1: "あ", 2: "い", 3: "う", 4: "え", 5: "お",
    6: "か", 7: "き", 8: "く", 9: "け", 10: "こ",
    11: "さ", 12: "し", 13: "す", 14: "せ", 15: "そ",
    16: "た", 17: "ち", 18: "つ", 19: "て", 20: "と",
    21: "な", 22: "に", 23: "ぬ", 24: "ね", 25: "の",
    26: "は", 27: "ひ", 28: "ふ", 29: "へ", 30: "ほ",
    31: "ま", 32: "み", 33: "む", 34: "め", 35: "も",
    36: "や", 37: "ゆ", 38: "よ",
    39: "ら", 40: "り", 41: "る", 42: "れ", 43: "ろ",
    44: "わ", 45: "を", 46: "ん",
    47: "が", 48: "ぎ", 49: "ぐ", 50: "げ", 51: "ご",
    52: "ざ", 53: "じ", 54: "ず", 55: "ぜ", 56: "ぞ",
    57: "だ", 58: "ぢ", 59: "づ", 60: "で", 61: "ど",
    62: "ば", 63: "び", 64: "ぶ", 65: "べ", 66: "ぼ",
    67: "ぱ", 68: "ぴ", 69: "ぷ", 70: "ぺ", 71: "ぽ",
    72: "ぁ", 73: "ぃ", 74: "ぅ", 75: "ぇ", 76: "ぉ",
    77: "ゃ", 78: "ゅ", 79: "ょ", 80: "っ", 81: "ゎ",
    82: "ヴ",
    83: "ノ", 84: "オ", 85: "ア", 86: "イ", 87: "ウ", 88: "エ", 89: "オ",
    90: "カ", 91: "キ", 92: "ク", 93: "ケ", 94: "コ",
    95: "サ", 96: "シ", 97: "ス", 98: "セ", 99: "ソ",
    100: "タ", 101: "チ", 102: "ツ", 103: "テ", 104: "ト",
    105: "ナ", 106: "ニ", 107: "ヌ", 108: "ネ", 109: "ノ",
    110: "ハ", 111: "ヒ", 112: "フ", 113: "ヘ", 114: "ホ",
    115: "マ", 116: "ミ", 117: "ム", 118: "メ", 119: "モ",
    120: "ヤ", 121: "ユ", 122: "ヨ",
    123: "ラ", 124: "リ", 125: "ル", 126: "レ", 127: "ロ",
    128: "ワ", 129: "ヲ", 130: "ン",
    131: "ガ", 132: "ギ", 133: "グ", 134: "ゲ", 135: "ゴ",
    136: "ザ", 137: "ジ", 138: "ズ", 139: "ゼ", 140: "ゾ",
    141: "ダ", 142: "ヂ", 143: "ヅ", 144: "デ", 145: "ド",
    146: "バ", 147: "ビ", 148: "ブ", 149: "ベ", 150: "ボ",
    151: "パ", 152: "ピ", 153: "プ", 154: "ペ", 155: "ポ",
    156: "ァ", 157: "ィ", 158: "ゥ", 159: "ェ", 160: "ォ",
    161: "ャ", 162: "ュ", 163: "ョ", 164: "ッ", 165: "ヮ",
    166: "A", 167: "B", 168: "C", 169: "D", 170: "E", 171: "F", 172: "G",
    173: "H", 174: "I", 175: "J", 176: "K", 177: "L", 178: "M", 179: "N",
    180: "O", 181: "P", 182: "Q", 183: "R", 184: "S", 185: "T", 186: "U",
    187: "V", 188: "W", 189: "X", 190: "Y", 191: "Z",
    192: "0", 193: "1", 194: "2", 195: "3", 196: "4",
    197: "5", 198: "6", 199: "7", 200: "8", 201: "9",
    202: "/", 203: ":", 204: "~", 205: ".", 206: "・",
    207: "。", 208: "?", 209: "!", 210: "*", 211: "<", 212: "-",
    213: ",", 214: "'", 215: "…", 216: "(", 217: ")",
    218: "「", 219: "」", 220: "『", 221: "』", 222: "【", 223: "】",
    224: "+", 225: "-", 226: "±", 227: "×", 228: "÷", 229: "%",
    230: "#", 231: "&", 232: "☆", 233: "★", 234: "○", 235: "●",
    236: "□", 237: "■", 238: "△", 239: "▲", 240: "※", 241: "=",
    242: "♡", 243: "$", 244: "♀", 245: "♂", 246: "!?",
    # Lowercase English alphabet (mapped to slots 247..272)
    247: "a", 248: "b", 249: "c", 250: "d", 251: "e", 252: "f", 253: "g",
    254: "h", 255: "i", 256: "j", 257: "k", 258: "l", 259: "m", 260: "n",
    261: "o", 262: "p", 263: "q", 264: "r", 265: "s", 266: "t", 267: "u",
    268: "v", 269: "w", 270: "x", 271: "y", 272: "z",
    273: "々"
}

LOWERCASE_BITMAPS: Dict[str, List[int]] = {
    'a': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1e00, 0x0100, 0x1f00, 0x3100, 0x3100, 0x3300, 0x1d80, 0x0000, 0x0000, 0x0000, 0x0000],
    'b': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x2e00, 0x3100, 0x2100, 0x2100, 0x2100, 0x3100, 0x2e00, 0x0000, 0x0000, 0x0000, 0x0000],
    'c': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1e00, 0x2100, 0x2000, 0x2000, 0x2000, 0x2100, 0x1e00, 0x0000, 0x0000, 0x0000, 0x0000],
    'd': [0x0000, 0x0100, 0x0100, 0x0100, 0x0100, 0x1d00, 0x2300, 0x2100, 0x2100, 0x2100, 0x2300, 0x1d80, 0x0000, 0x0000, 0x0000, 0x0000],
    'e': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1e00, 0x2100, 0x3f00, 0x2000, 0x2000, 0x2100, 0x1e00, 0x0000, 0x0000, 0x0000, 0x0000],
    'f': [0x0000, 0x0c00, 0x1200, 0x1000, 0x1000, 0x3c00, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x0000, 0x0000, 0x0000, 0x0000],
    'g': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1d80, 0x2300, 0x2100, 0x2100, 0x2300, 0x1d00, 0x0100, 0x2100, 0x1e00, 0x0000, 0x0000],
    'h': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x2e00, 0x3100, 0x2100, 0x2100, 0x2100, 0x2100, 0x2100, 0x0000, 0x0000, 0x0000, 0x0000],
    'i': [0x0000, 0x1000, 0x0000, 0x0000, 0x0000, 0x3000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3800, 0x0000, 0x0000, 0x0000, 0x0000],
    'j': [0x0000, 0x0400, 0x0000, 0x0000, 0x0000, 0x0c00, 0x0400, 0x0400, 0x0400, 0x0400, 0x0400, 0x0400, 0x2400, 0x1800, 0x0000, 0x0000],
    'k': [0x0000, 0x2000, 0x2000, 0x2000, 0x2000, 0x2200, 0x2400, 0x2800, 0x3000, 0x2800, 0x2400, 0x2200, 0x0000, 0x0000, 0x0000, 0x0000],
    'l': [0x0000, 0x3000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3800, 0x0000, 0x0000, 0x0000, 0x0000],
    'm': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3600, 0x4900, 0x4900, 0x4900, 0x4900, 0x4900, 0x4900, 0x0000, 0x0000, 0x0000, 0x0000],
    'n': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2e00, 0x3100, 0x2100, 0x2100, 0x2100, 0x2100, 0x2100, 0x0000, 0x0000, 0x0000, 0x0000],
    'o': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1e00, 0x2100, 0x2100, 0x2100, 0x2100, 0x2100, 0x1e00, 0x0000, 0x0000, 0x0000, 0x0000],
    'p': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2e00, 0x3100, 0x2100, 0x2100, 0x2100, 0x3100, 0x2e00, 0x2000, 0x2000, 0x0000, 0x0000],
    'q': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1d00, 0x2300, 0x2100, 0x2100, 0x2100, 0x2300, 0x1d00, 0x0100, 0x0180, 0x0000, 0x0000],
    'r': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2e00, 0x3100, 0x2000, 0x2000, 0x2000, 0x2000, 0x2000, 0x0000, 0x0000, 0x0000, 0x0000],
    's': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1e00, 0x2100, 0x2000, 0x1e00, 0x0100, 0x2100, 0x1e00, 0x0000, 0x0000, 0x0000, 0x0000],
    't': [0x0000, 0x1000, 0x1000, 0x1000, 0x1000, 0x3c00, 0x1000, 0x1000, 0x1000, 0x1000, 0x1100, 0x0e00, 0x0000, 0x0000, 0x0000, 0x0000],
    'u': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2100, 0x2100, 0x2100, 0x2100, 0x2100, 0x2300, 0x1d80, 0x0000, 0x0000, 0x0000, 0x0000],
    'v': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2100, 0x2100, 0x2100, 0x1200, 0x1200, 0x0c00, 0x0c00, 0x0000, 0x0000, 0x0000, 0x0000],
    'w': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x4900, 0x4900, 0x4900, 0x4900, 0x2a00, 0x2a00, 0x1400, 0x0000, 0x0000, 0x0000, 0x0000],
    'x': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2200, 0x1400, 0x0800, 0x0800, 0x1400, 0x2200, 0x2200, 0x0000, 0x0000, 0x0000, 0x0000],
    'y': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2100, 0x2100, 0x2100, 0x2300, 0x1d00, 0x0100, 0x2100, 0x1e00, 0x0000, 0x0000, 0x0000],
    'z': [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x3f00, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000, 0x3f00, 0x0000, 0x0000, 0x0000, 0x0000]
}


def build_jis_level1_kanji_list() -> List[str]:
    """Generates standard JIS X 0208 Level 1 Kanji list (Ku 16..47)."""
    kanji = []
    for ku in range(16, 48):
        for ten in range(1, 95):
            try:
                b = bytes([ku + 0xA0, ten + 0xA0])
                char = b.decode("euc_jp")
                kanji.append(char)
            except Exception:
                pass
    return kanji


class PersonaFontTool:
    def __init__(self, font_path: str = "extracted/FONT.BIN"):
        self.font_path = Path(font_path)
        if not self.font_path.is_file():
            raise FileNotFoundError(f"FONT.BIN not found at {self.font_path}")
        self.raw_data = bytearray(self.font_path.read_bytes())
        self.glyph_count = len(self.raw_data) // BYTES_PER_GLYPH
        self.char_map: Dict[int, str] = {}
        self.reverse_map: Dict[str, int] = {}
        self._build_character_maps()

    def _build_character_maps(self):
        """Construct full 2048 character map combining non-kanji, lowercase ASCII, and JIS Level 1 Kanji."""
        self.char_map = dict(NON_KANJI_TABLE)

        jis_kanji = build_jis_level1_kanji_list()
        kanji_start = 274

        for idx, char in enumerate(jis_kanji):
            glyph_id = kanji_start + idx
            if glyph_id >= self.glyph_count:
                break
            self.char_map[glyph_id] = char

        for gid, char in self.char_map.items():
            self.reverse_map[char] = gid

        # Add common aliases / full-width lookups
        aliases = {
            "！": "!", "？": "?", "（": "(", "）": ")", "，": ",", "．": ".",
            "：": ":", "；": ";", "＋": "+", "－": "-", "＝": "=", "％": "%",
            "’": "'", "”": "\"", "“": "\"", "‘": "'", "　": " "
        }
        for k, v in aliases.items():
            if v in self.reverse_map and k not in self.reverse_map:
                self.reverse_map[k] = self.reverse_map[v]

    def patch_font_with_lowercase(self, out_path: Optional[str] = None):
        """Injects 16x16 lowercase glyph bitmaps into FONT.BIN at glyph IDs 247..272."""
        for char, rows in LOWERCASE_BITMAPS.items():
            gid = self.reverse_map[char]
            offset = gid * BYTES_PER_GLYPH
            for r_idx, row_val in enumerate(rows):
                struct.pack_into(">H", self.raw_data, offset + r_idx * 2, row_val)

        target = Path(out_path) if out_path else self.font_path
        target.write_bytes(self.raw_data)
        print(f"[+] Patched FONT.BIN with lowercase English font bitmaps ({target})")

    def get_glyph_data(self, glyph_id: int) -> bytes:
        """Returns 32-byte raw bitmap for given glyph ID."""
        if 0 <= glyph_id < self.glyph_count:
            return bytes(self.raw_data[glyph_id * BYTES_PER_GLYPH : (glyph_id + 1) * BYTES_PER_GLYPH])
        return b"\x00" * BYTES_PER_GLYPH

    def render_ascii(self, glyph_id: int) -> List[str]:
        """Renders 16x16 glyph as list of ASCII character strings."""
        data = self.get_glyph_data(glyph_id)
        rows = []
        for r in range(GLYPH_HEIGHT):
            w = struct.unpack(">H", data[r * 2 : r * 2 + 2])[0]
            rows.append("".join("█" if (w & (1 << (15 - c))) else " " for c in range(GLYPH_WIDTH)))
        return rows

    def export_tbl(self, out_path: str = "docs/tbl/persona_jp.tbl"):
        """Exports standard Romhacking .tbl file."""
        tbl_path = Path(out_path)
        tbl_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Megami Ibunroku Persona (PSX) Character Table",
            "# Control Codes",
            "/F5=<LINE>",
            "/F6=<PAGE>",
            "/FC=<CLOSE>",
            "/FD=<CHOICE>",
            "/FE=<END>",
            "# 1-byte Gojuon characters (0x00 - 0x7F)",
        ]

        for gid in range(128):
            if gid in self.char_map:
                char = self.char_map[gid]
                lines.append(f"{gid:02X}={char}")

        lines.append("# 2-byte Characters & Kanji (0x8000 - 0x87FF)")
        for gid in range(128, self.glyph_count):
            if gid in self.char_map:
                char = self.char_map[gid]
                byte1 = 0x80 | (gid >> 8)
                byte2 = gid & 0xFF
                lines.append(f"{byte1:02X}{byte2:02X}={char}")

        tbl_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[+] Exported .tbl file to {tbl_path} ({len(self.char_map)} entries)")

    def export_json(self, out_path: str = "docs/tbl/persona_font.json"):
        """Exports JSON mapping file with Unicode and byte sequences."""
        json_path = Path(out_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)

        entries = []
        for gid in range(self.glyph_count):
            char = self.char_map.get(gid, f"[GLYPH_{gid}]")
            if gid < 128:
                byte_seq = f"{gid:02x}"
            else:
                byte1 = 0x80 | (gid >> 8)
                byte2 = gid & 0xFF
                byte_seq = f"{byte1:02x}{byte2:02x}"

            entries.append({
                "glyph_id": gid,
                "char": char,
                "hex_bytes": byte_seq,
                "unicode": f"U+{ord(char):04X}" if len(char) == 1 else "N/A",
                "is_kanji": gid >= 274
            })

        json_path.write_text(json.dumps({"total_glyphs": self.glyph_count, "mappings": entries}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Exported JSON font map to {json_path}")

    def decode_bytes(self, data: bytes) -> str:
        """Decodes raw game text bytecode into UTF-8 text with markup tags."""
        result = []
        idx = 0
        while idx < len(data):
            b = data[idx]
            if b == 0xFF:
                if idx + 1 < len(data):
                    b2 = data[idx + 1]
                    if b2 == 0xF5:
                        result.append("<LINE>")
                        idx += 2
                    elif b2 == 0xF6:
                        result.append("<PAGE>")
                        idx += 2
                    elif b2 == 0xFC:
                        result.append("<CLOSE>")
                        idx += 2
                    elif b2 == 0xFD:
                        param = data[idx + 2] if idx + 2 < len(data) else 0
                        result.append(f"<CHOICE id={param}>")
                        idx += 3
                    elif b2 == 0xFE:
                        result.append("<END>")
                        idx += 2
                    elif b2 == 0xFF:
                        idx += 1  # padding
                    else:
                        result.append(f"<CMD_{b2:02x}>")
                        idx += 2
                else:
                    idx += 1
            elif 0x80 <= b <= 0x87:
                if idx + 1 < len(data):
                    b2 = data[idx + 1]
                    gid = ((b - 0x80) << 8) | b2
                    result.append(self.char_map.get(gid, f"[G_{gid}]"))
                    idx += 2
                else:
                    idx += 1
            else:
                result.append(self.char_map.get(b, f"[G_{b}]"))
                idx += 1
        return "".join(result)

    def encode_text(self, text: str) -> bytes:
        """Encodes UTF-8 text with markup tags back into raw game bytecode."""
        buf = bytearray()
        i = 0
        while i < len(text):
            if text[i] == "<":
                end = text.find(">", i)
                if end != -1:
                    tag = text[i + 1 : end]
                    if tag == "LINE":
                        buf.extend([0xFF, 0xF5])
                    elif tag == "PAGE":
                        buf.extend([0xFF, 0xF6])
                    elif tag == "CLOSE":
                        buf.extend([0xFF, 0xFC])
                    elif tag.startswith("CHOICE"):
                        param = 0
                        if "id=" in tag:
                            try:
                                param = int(tag.split("id=")[1])
                            except ValueError:
                                pass
                        buf.extend([0xFF, 0xFD, param])
                    elif tag == "END":
                        buf.extend([0xFF, 0xFE])
                    elif tag.startswith("CMD_"):
                        try:
                            code = int(tag.split("CMD_")[1], 16)
                            buf.extend([0xFF, code])
                        except ValueError:
                            pass
                    i = end + 1
                    continue

            char = text[i]
            if char in self.reverse_map:
                gid = self.reverse_map[char]
                if gid < 128:
                    buf.append(gid)
                else:
                    b1 = 0x80 | (gid >> 8)
                    b2 = gid & 0xFF
                    buf.extend([b1, b2])
            else:
                # Fallback to space
                buf.append(0)
            i += 1
        return bytes(buf)


def main():
    parser = argparse.ArgumentParser(description="Persona Font & Table Tool")
    parser.add_argument("--font", default="extracted/FONT.BIN", help="Path to FONT.BIN")
    parser.add_argument("--export-tbl", default="docs/tbl/persona_jp.tbl", help="Destination path for .tbl")
    parser.add_argument("--export-json", default="docs/tbl/persona_font.json", help="Destination path for .json")
    parser.add_argument("--patch-lowercase", action="store_true", help="Patch FONT.BIN with lowercase English font")
    parser.add_argument("--preview", type=int, default=None, help="Preview glyph ASCII for given glyph ID")

    args = parser.parse_args()
    tool = PersonaFontTool(args.font)

    if args.patch_lowercase:
        tool.patch_font_with_lowercase()

    if args.preview is not None:
        print(f"=== Glyph {args.preview} ({tool.char_map.get(args.preview, 'Unknown')}) ===")
        for line in tool.render_ascii(args.preview):
            print(line)
        return

    tool.export_tbl(args.export_tbl)
    tool.export_json(args.export_json)


if __name__ == "__main__":
    main()
