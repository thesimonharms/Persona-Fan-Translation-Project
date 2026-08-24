#!/usr/bin/env python3
"""
Encode-time 1-byte English via leftover-safe kana slots.

Translation JSON is never rewritten. Mixed-case speaker text stays in
scripts/translated/. Insertion may drop a leading "Name: " prefix only
when the full string does not fit the original byte budget.

Glyphs >= 128 are always 2-byte. 0x80-0x87 are 2-byte leads and 0xFF is
the control lead; emitting those as 1-byte text desyncs the VM.

Colon and apostrophe stay on native 2-byte glyphs (203 / 206). A 1-byte
':' (0x7F) does not close the FF 01 nameplate, so later lines keep a red
background. Apostrophe on 0x7C collides with opcode FF 7C.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMAP_PATH = ROOT / "docs/tbl/font_remap_en.json"
GLYPH_SIZE = 32

TAG_BYTES = {
    "<PAUSE>": b"\xff\xf1", "<NAME?>": b"\xff\xf3", "<LINE>": b"\xff\xf5",
    "<PAGE>": b"\xff\xf6", "<MENU_A>": b"\xff\xfb", "<MENU_B>": b"\xff\xf7",
    "<CLOSE>": b"\xff\xfc", "<CHOICE>": b"\xff\xfd", "<END>": b"\xff\xfe",
}
VOICE_CODES = (0xEF, 0xEE, 0xED, 0xEB)
CHAR_FALLBACK = {
    "\u2014": "-", "\u2013": "-", "~": "\u301c",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u3000": " ",
}
SPEAKER_RE = re.compile(r"^[A-Za-z][A-Za-z .\-]{0,20}:\s*")

_REMAP_DOC = json.loads(REMAP_PATH.read_text(encoding="utf-8"))
REMAP: dict[str, int] = {k: int(v) for k, v in _REMAP_DOC["remap"].items()}
BITMAP_SOURCE: dict[str, int] = {
    k: int(v) for k, v in _REMAP_DOC["bitmap_source_glyph"].items()
}


def encode_gid(gid: int) -> bytes:
    """1-byte only for glyphs 0x00-0x7F. Everything else is 2-byte."""
    if gid < 0x80:
        return bytes([gid])
    return bytes([0x80 | (gid >> 8), gid & 0xFF])


def gid_cost(gid: int) -> int:
    return 1 if gid < 0x80 else 2


def encode_text(text: str, orig_raw: bytes | None = None, rev: dict | None = None):
    """Encode tagged text. English letters/punct use 1-byte remap slots."""
    out = bytearray()
    errors = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for tag, b in TAG_BYTES.items():
            if text.startswith(tag, i):
                out.extend(b)
                i += len(tag)
                matched = True
                break
        if matched:
            continue
        if text.startswith("<VOICE?>", i):
            code = 0xEF
            if orig_raw:
                for k in range(len(orig_raw) - 1):
                    if orig_raw[k] == 0xFF and orig_raw[k + 1] in VOICE_CODES:
                        code = orig_raw[k + 1]
                        break
            out.extend(bytes([0xFF, code]))
            i += 8
            continue
        if text.startswith("[FF]", i):
            out.append(0xFF)
            i += 4
            continue
        if text[i] == "[" and i + 3 <= n and text[i + 3] == "]":
            try:
                code = int(text[i + 1:i + 3], 16)
                out.extend(bytes([0xFF, code]))
                i += 4
                continue
            except ValueError:
                pass
        if text[i] == "{" and text.find("}", i) != -1:
            j = text.find("}", i)
            try:
                gid = int(text[i + 1:j])
                out.extend(encode_gid(gid))
                i = j + 1
                continue
            except ValueError:
                pass
        ch = text[i]
        if ch in CHAR_FALLBACK:
            ch = CHAR_FALLBACK[ch]
        gid = REMAP.get(ch)
        if gid is None and rev is not None:
            gid = rev.get(ch)
        if gid is None:
            errors.append(ch)
            i += 1
            continue
        out.extend(encode_gid(gid))
        i += 1
    return bytes(out), errors


def drop_speaker(text: str) -> str:
    dropped = SPEAKER_RE.sub("", text, count=1)
    return dropped if dropped else text


def fit_event_text(text: str, budget: int, orig_raw: bytes | None = None, rev: dict | None = None):
    """
    Try full mixed-case (with speaker), then speaker-drop.
    When the name is dropped, keep a leading native ':' so FF 01
    name-color is closed. Returns (encoded, method) or (None, None).
    Does not mutate the source translation.
    """
    enc, _ = encode_text(text, orig_raw=orig_raw, rev=rev)
    if len(enc) <= budget:
        return enc, "full"
    dropped = drop_speaker(text)
    if dropped != text:
        keep_colon = ":" + dropped.lstrip()
        enc2, _ = encode_text(keep_colon, orig_raw=orig_raw, rev=rev)
        if len(enc2) <= budget:
            return enc2, "drop_speaker"
    return None, None


def patch_font(src_path: Path, dst_path: Path) -> int:
    """Copy native Latin bitmaps onto leftover-safe 1-byte kana slots."""
    src = src_path.read_bytes()
    data = bytearray(src)
    n = 0
    for ch, slot in REMAP.items():
        src_gid = BITMAP_SOURCE[ch]
        src_off = src_gid * GLYPH_SIZE
        dst_off = slot * GLYPH_SIZE
        bitmap = src[src_off:src_off + GLYPH_SIZE]
        if len(bitmap) != GLYPH_SIZE:
            raise ValueError(f"missing source bitmap for {ch!r} gid={src_gid}")
        data[dst_off:dst_off + GLYPH_SIZE] = bitmap
        n += 1
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_bytes(data)
    return n


if __name__ == "__main__":
    src = ROOT / "extracted/FONT.BIN"
    dst = ROOT / "build/extracted/FONT.BIN"
    n = patch_font(src, dst)
    print(f"[+] patched {n} FONT.BIN glyphs -> {dst}")
