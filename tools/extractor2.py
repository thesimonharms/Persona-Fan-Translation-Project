#!/usr/bin/env python3
"""
tools/extractor2.py - Verified text extractor for Megami Ibunroku Persona (PSX)

Encoding (verified against FONT.BIN glyphs):
  - 1-byte codes 0x00-0xFF map to glyph ids 0-255 (except 0x80-0x87 leads)
  - 2-byte codes: lead 0x80-0x87 + index -> glyph id ((lead & 0x7F) << 8) | index
  - 0xFF xx pairs are dialogue control codes
Control codes (verified in context):
  FF F3 <name tag argument>, FF F5 <LINE>, FF F6 <PAGE>, FF FC <CLOSE>,
  FF FD <choice>, FF FE <END>, FF FB/F7 paired (TALK menu), FF 02/03 = string
  terminators in event scripts, FF 21 = text-display opcode (event scripts).
Char table: docs/tbl/persona_char_table_v2.json (glyph id -> unicode).
"""
import json
import struct
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
TBL = {int(k): v for k, v in json.loads(
    (ROOT / "docs/tbl/persona_char_table_v2.json").read_text(encoding="utf-8")).items()}

CTRL_NAMES = {
    0xF1: "PAUSE", 0xF3: "NAME?", 0xF5: "LINE", 0xF6: "PAGE", 0xFC: "CLOSE",
    0xFD: "CHOICE", 0xFE: "END", 0xFB: "MENU_A", 0xF7: "MENU_B",
    0xEF: "VOICE?", 0xEE: "VOICE?", 0xED: "VOICE?", 0xEB: "VOICE?",
}
KNOWN_CTRL = set(CTRL_NAMES) | {0x02, 0x03, 0x21, 0x20, 0x26, 0x27, 0x55, 0x60, 0x61, 0x64, 0x67, 0x68, 0x7c}


def decode(data: bytes) -> tuple:
    """Decode raw script bytes to (text, unresolved_count). Controls become [XX] tags."""
    out = []
    bad = 0
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        if b == 0xFF:
            if i + 1 < n:
                c = data[i + 1]
                name = CTRL_NAMES.get(c)
                out.append(f"<{name}>" if name else f"[{c:02x}]")
                i += 2
            else:
                out.append("[FF]"); i += 1
        elif b == 0x00:
            out.append(" "); i += 1
        elif 0x80 <= b <= 0x87:
            if i + 1 >= n:
                bad += 1; break
            gid = ((b & 0x7F) << 8) | data[i + 1]
            ch = TBL.get(gid)
            if ch is None:
                out.append(f"<{gid:03x}>"); bad += 1
            else:
                out.append(ch)
            i += 2
        else:
            ch = TBL.get(b)
            if ch is None:
                out.append(f"<{b:02x}>"); bad += 1
            else:
                out.append(ch)
            i += 1
    return "".join(out), bad


def find_tims(data: bytes):
    """Locate TIM images; returns list of (start, end) byte ranges."""
    tims = []
    i = 0
    n = len(data)
    while i < n - 8:
        if data[i:i+4] == b"\x10\x00\x00\x00":
            flags = int.from_bytes(data[i+4:i+8], "little")
            if flags <= 0x0F:
                off = i + 8
                end = i + 8
                if flags & 1:
                    if off + 4 > n: i += 4; continue
                    clen = int.from_bytes(data[off:off+4], "little")
                    if clen < 12 or off + clen > n: i += 4; continue
                    off += clen; end = off
                if off + 4 <= n:
                    ilen = int.from_bytes(data[off:off+4], "little")
                    if ilen >= 12 and off + ilen <= n:
                        end = off + ilen
                        tims.append((i, end))
                        i = max(end, i + 4)
                        continue
            i += 4
        else:
            i += 1
    return tims


# ---------------------------------------------------------------- TALK files
def extract_talk(path: Path):
    """TALK/*.BIN: header 5x u32 section ptrs, string pointer table @0x14.
    String i spans (ptr_i, ptr_{i+1}] inclusive; boundary bytes are shared."""
    d = path.read_bytes()
    if len(d) < 0x18:
        return []
    sec = [struct.unpack_from("<I", d, i * 4)[0] for i in range(5)]
    str0 = struct.unpack_from("<I", d, 0x14)[0]
    n = (str0 - 0x14) // 4
    ptrs = [struct.unpack_from("<I", d, 0x14 + i * 4)[0] for i in range(n)]
    valid = [p for p in ptrs if p != 0xFFFFFFFF and p < len(d)]
    out = []
    prev = valid[0]
    for p in valid[1:]:
        if p <= prev or p >= len(d):
            continue
        raw = d[prev + 1 : p + 1]
        if prev == valid[0]:
            i = 0
            while i < len(raw) and raw[i] == 0xFF:
                i += 1
            raw = raw[i:]
        # restore control split across boundary
        if raw and d[prev] == 0xFF and raw[0] in (0xF3, 0xF5, 0xF6, 0xFB, 0xF7, 0xFC, 0xFD, 0xFE):
            raw = b"\xff" + raw
        if len(raw) >= 2 and raw[-1] == 0xFF and raw[-2] != 0xFF and p + 1 < len(d) \
                and d[p + 1] in (0xF3, 0xF5, 0xF6, 0xFB, 0xF7, 0xFC, 0xFD, 0xFE):
            raw = raw[:-1]
        if raw.strip(b"\x00\xff"):
            out.append((prev + 1, raw))
        prev = p
    if valid and sec[1] > valid[-1] + 1:
        raw = d[valid[-1] + 1 : sec[1]].rstrip(b"\xff")
        if raw.strip(b"\x00"):
            out.append((valid[-1] + 1, raw))
    return out


# ------------------------------------------------------------ event scripts
def scan_event_strings(data: bytes, tims):
    """Event containers (E0-E3, D*.BIN, ADV.BIN, S2D.BIN):
    text runs framed by ff-controls; real strings end at FF 02/03."""
    out = []
    n = len(data)
    i = 0
    start = None
    while i < n:
        b = data[i]
        if b == 0xFF:
            if start is not None and i + 1 < n and data[i + 1] in (0x02, 0x03):
                raw = data[start:i]
                if 3 <= len(raw) <= 120 and not any(ts <= start < te for ts, te in tims):
                    txt, bad = decode(raw)
                    kana = sum(1 for c in txt if "\u3040" <= c <= "\u309f")
                    cc = Counter(txt)
                    if kana >= 2 and cc.most_common(1)[0][1] / max(len(txt), 1) <= 0.4:
                        if len(txt) >= 10 or bad == 0:
                            out.append((start, i, raw, txt))
            start = None
            i += 2
        elif b == 0x00:
            # 0x00 = space glyph: part of a run
            if start is None:
                start = i
            i += 1
        elif 0x01 <= b <= 0x7F:
            if start is None:
                start = i
            i += 1
        elif 0x80 <= b <= 0x87 and i + 1 < n:
            if start is None:
                start = i
            i += 2
        else:
            start = None
            i += 1
    return out


if __name__ == "__main__":
    for p in sorted((ROOT / "extracted/TALK").glob("*.BIN")):
        for off, raw in extract_talk(p)[:2]:
            print(p.name, hex(off), decode(raw)[0][:60])
