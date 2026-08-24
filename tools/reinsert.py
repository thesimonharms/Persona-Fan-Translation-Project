#!/usr/bin/env python3
"""
tools/reinsert.py - Reinsert translated English text into game binaries.

Inputs : scripts/translated/{talk,events,story,system}/*.json (new schema:
         entries with offset/length_bytes/raw_hex/text_jp/translation_en,
         verified to match scripts/original2 extraction)
Outputs: build/extracted/ modified binaries

Strategies:
  TALK/*.BIN  - full pointer-table rebuild. String sizes may grow freely;
                the disc pipeline (table_relocator + rebuilder) relocates
                expanded files to fresh LBAs.
  Event files (E0-E3, ADV.BIN, S2D.BIN) - in-place replacement only:
                these containers have internal sector tables and RAM
                pointers; growing strings would corrupt them. Strings that
                encode longer than the original are SKIPPED (left Japanese)
                and reported.

Encoding (see docs/EXTRACTION_HANDOFF.md and tools/font_remap.py):
  1-byte glyphs 0x00-0x7F only. 0x80-0x87 are 2-byte leads; 0xFF is the
  control lead. Glyphs >= 128 always use 2-byte form 0x80|hi, lo.
  English letters/punct encode through leftover-safe 1-byte kana slots
  (docs/tbl/font_remap_en.json). Translation JSON is never rewritten.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.extractor2 import extract_talk, decode, TBL
from tools.font_remap import (
    encode_gid, encode_text as remap_encode_text, fit_event_text, patch_font,
)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "extracted"
OUT = ROOT / "build/extracted"

REV = {}
for _gid, _ch in TBL.items():
    REV.setdefault(_ch, _gid)


def encode_text(text: str, orig_raw: bytes = None):
    """Encode tagged English/JP text to game bytes. Returns (bytes, errors)."""
    return remap_encode_text(text, orig_raw=orig_raw, rev=REV)


# ------------------------------------------------------------- TALK rebuild
def rebuild_talk(json_path: Path, orig_bin: Path, out_bin: Path) -> dict:
    d = json.loads(json_path.read_text(encoding="utf-8"))
    data = orig_bin.read_bytes()
    if len(data) < 0x18:
        raise ValueError(f"{orig_bin}: too small")

    sec = [struct.unpack_from("<I", data, i * 4)[0] for i in range(5)]
    str0 = struct.unpack_from("<I", data, 0x14)[0]  # first pointer = string region base
    n_slots = (str0 - 0x14) // 4
    ptrs = [struct.unpack_from("<I", data, 0x14 + i * 4)[0] for i in range(n_slots)]

    # Original strings via proven rule: string k = (v_k, v_{k+1}]; last string
    # runs to sec[1]. Recompute exactly like extract_talk.
    orig_strings = {}  # offset -> raw
    for off, raw in extract_talk(orig_bin):
        orig_strings[off] = raw

    trans = {}
    for e in d["entries"]:
        if e.get("translation_en", "").strip():
            trans[e["offset"]] = e["translation_en"]

    # Build new string sequence in pointer order.
    valid = [p for p in ptrs if p != 0xFFFFFFFF and p < len(data)]
    new_strings = []          # list of (orig_offset, new_raw)
    enc_errors = []
    for k in range(len(valid)):
        off = valid[k] + 1
        raw = orig_strings.get(off)
        if raw is None:
            continue
        if off in trans:
            enc, errs = encode_text(trans[off], orig_raw=raw)
            if errs:
                enc_errors.append((off, errs))
            if enc:
                new_strings.append((off, enc))
                continue
        new_strings.append((off, raw))


    # Pointer math: v_0 = str0; v_{k+1} = v_k + len(s_k).
    # First original pointer already == str0; padding between str0+1 and first
    # content is part of the first string's raw (extractor kept it stripped, so
    # re-add FF padding for the first string).
    first_off = new_strings[0][0]
    pad = data[str0 + 1:first_off]  # original gap bytes (usually FF)
    if pad and set(pad) <= {0xFF}:
        new_strings[0] = (first_off, pad + new_strings[0][1])

    new_block = bytearray()
    new_ptrs = []
    v = str0
    for off, raw in new_strings:
        # pointer for this string = v (points one byte before its content)
        new_ptrs.append(v)
        new_block.extend(raw)
        v += len(raw)

    # Assemble binary
    out = bytearray(data[:0x14])
    # pointer table: preserve slot layout (invalid slots stay 0xFFFFFFFF)
    vi = 0
    for slot in ptrs:
        if slot == 0xFFFFFFFF or slot >= len(data):
            out.extend(struct.pack("<I", 0xFFFFFFFF))
        else:
            if vi < len(new_ptrs):
                out.extend(struct.pack("<I", new_ptrs[vi]))
                vi += 1
            else:
                out.extend(struct.pack("<I", 0xFFFFFFFF))
    # pad table to str0
    while len(out) < str0:
        out.append(0x00)
    # anchor byte at str0: pointer v_0 points here; string content
    # begins at v_0+1 (matches original layout)
    out.append(data[str0])
    # string block
    out.extend(new_block)
    # pad to 4
    while len(out) % 4:
        out.append(0x00)
    new_sec1 = len(out)
    delta = new_sec1 - sec[1]
    # trailing sections
    out.extend(data[sec[1]:])
    # update header section offsets
    for idx in range(1, 5):
        old = sec[idx]
        struct.pack_into("<I", out, idx * 4, old + delta)

    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(out)

    translated = sum(1 for off, raw in new_strings if off in trans)
    return {
        "file": orig_bin.name, "orig_size": len(data), "new_size": len(out),
        "delta": delta, "translated": translated,
        "kept_jp": len(new_strings) - translated, "encode_errors": enc_errors,
    }


# --------------------------------------------------------- event in-place
def patch_event_file(json_path: Path, orig_bin: Path, out_bin: Path) -> dict:
    d = json.loads(json_path.read_text(encoding="utf-8"))
    data = bytearray(orig_bin.read_bytes())
    stats = {"file": str(orig_bin.relative_to(SRC)), "translated": 0,
             "drop_speaker": 0, "skipped_overflow": [], "skipped_error": [],
             "encode_errors": []}
    for e in d["entries"]:
        en = e.get("translation_en", "").strip()
        if not en:
            continue
        orig_raw = bytes.fromhex(e.get("raw_hex", ""))
        _, errs = encode_text(en, orig_raw=orig_raw)
        if errs:
            stats["encode_errors"].append((e["offset"], errs))
        off, ln = e["offset"], e["length_bytes"]
        enc, method = fit_event_text(en, ln, orig_raw=orig_raw, rev=REV)
        if enc is None:
            full, _ = encode_text(en, orig_raw=orig_raw)
            stats["skipped_overflow"].append(
                {"offset": off, "need": len(full), "have": ln, "en": en[:80]})
            continue
        data[off:off + ln] = enc.ljust(ln, b"\x00")
        stats["translated"] += 1
        if method == "drop_speaker":
            stats["drop_speaker"] += 1
    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(data)
    return stats


# ------------------------------------------------------------------- main
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--translated-dir", default="scripts/translated")
    ap.add_argument("--src", default="extracted")
    ap.add_argument("--out", default="build/extracted")
    args = ap.parse_args()
    global SRC, OUT
    SRC = ROOT / args.src
    OUT = ROOT / args.out

    report = {"talk": [], "events": []}

    n_glyphs = patch_font(SRC / "FONT.BIN", OUT / "FONT.BIN")
    print(f"[FONT] patched {n_glyphs} 1-byte Latin slots -> {OUT / 'FONT.BIN'}")

    # 1. TALK rebuilds
    for jp in sorted((ROOT / args.translated_dir / "talk").glob("*.json")):
        orig = SRC / "TALK" / f"{jp.stem}.BIN"
        if not orig.is_file():
            continue
        st = rebuild_talk(jp, orig, OUT / "TALK" / f"{jp.stem}.BIN")
        report["talk"].append(st)
        print(f"[TALK] {st['file']}: {st['orig_size']:,} -> {st['new_size']:,} "
              f"(delta {st['delta']:+d}), {st['translated']} EN / {st['kept_jp']} JP"
              + (f", {len(st['encode_errors'])} encode errors" if st["encode_errors"] else ""))

    # 2. Event in-place patches (new-schema files only)
    event_files = [
        ("events/E0.json", "ADV/E0.BIN"), ("events/E1.json", "ADV/E1.BIN"),
        ("events/E2.json", "ADV/E2.BIN"), ("events/E3.json", "ADV/E3.BIN"),
        ("story/ADV.json", "ADV.BIN"), ("system/S2D.json", "S2D.BIN"),
    ]
    for jrel, brel in event_files:
        jp = ROOT / args.translated_dir / jrel
        if not jp.is_file():
            continue
        st = patch_event_file(jp, SRC / brel, OUT / brel)
        report["events"].append(st)
        ov = len(st["skipped_overflow"])
        dropped = st.get("drop_speaker", 0)
        print(f"[EVT ] {st['file']}: {st['translated']} patched"
              + (f", {dropped} speaker-dropped" if dropped else "")
              + (f", {ov} OVERFLOW-SKIPPED" if ov else ""))

    # summary
    tot_t = sum(s["translated"] for s in report["talk"])
    tot_e = sum(s["translated"] for s in report["events"])
    tot_ov = sum(len(s["skipped_overflow"]) for s in report["events"])
    print(f"\n[+] TALK: {tot_t} strings | Events: {tot_e} patched, {tot_ov} overflow-skipped")

    # dump overflow details for follow-up
    ov_path = ROOT / "build/reinsert_report.json"
    ov_path.parent.mkdir(parents=True, exist_ok=True)
    ov_path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"[+] Full report: {ov_path}")


if __name__ == "__main__":
    main()
