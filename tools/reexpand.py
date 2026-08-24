#!/usr/bin/env python3
"""
tools/reexpand.py - Event subfile string EXPANSION recompiler for ADV/E*.BIN.

Container layout (verified on E0-E3):
  File: u16 sector-index table at 0 (0-terminated), subfiles at 2048-byte LBAs.
  Subfile: custom bytecode VM overlay:
    [0:4]   u32 RAM base pointer (e.g. 0x80100000)
    [4:8]   u32 end-of-code pointer (code+data size = value - base)
    ...     bytecode stream with INLINE text (ff 21 00 00 <text> ff 02/03 ...)
    ...     internal 4-aligned u32 pointers (header table + inline operands)
            ALL pointers live before the text they reference.
  Strings terminate with ff 02 or ff 03 (2 bytes) - shared with our extraction.

Expansion algorithm per subfile:
  1. Locate every text run (from scripts/final/<E>.json offsets).
  2. Re-encode with English; strings may grow.
  3. Rebuild stream: copy bytes, substituting expanded strings.
  4. Collect ALL internal pointers (u32 in [base, base+len)) BEFORE patching;
     remap each pointer target: new = old + (cumulative delta at old).
  5. Pad subfile to 2048 multiple; rebuild the sector table; enlarge file.

Sector table constraint: subfile starts must stay 2048-aligned; growth shifts
every subsequent subfile, so the whole sector table is rewritten. Subfiles load
at fixed RAM bases (base differs per subfile) - we do NOT touch bases, only
in-file layout.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.reinsert import encode_text

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "extracted"
OUT = ROOT / "build/extracted"


def find_internal_pointers(sub: bytes, base: int):
    """All 4-aligned u32 values pointing into [base, base+len(sub))."""
    out = []
    for j in range(0, len(sub) - 3, 4):
        v = struct.unpack_from("<I", sub, j)[0]
        if base <= v < base + len(sub):
            out.append((j, v - base))
    return out


def expand_subfile(sub: bytes, entries: list) -> tuple:
    """entries: [{offset (file-relative), length_bytes, translation_en, raw_hex}]
    offset is FILE-relative; subfile-relative = offset - subfile_start."""
    base = struct.unpack_from("<I", sub, 0)[0] & 0xFFFF0000
    # remap: old_rel -> new_rel built from string replacements
    # strings sorted by subfile offset
    subs = []
    for e in entries:
        en = e.get("translation_en", "").strip()
        if not en:
            continue
        enc, errs = encode_text(en, orig_raw=bytes.fromhex(e.get("raw_hex", "")))
        if errs:
            pass  # fallbacks applied inside encode_text
        if not enc:
            continue
        subs.append((e["_rel_off"], e["length_bytes"], enc))

    if not subs:
        return sub, 0

    subs.sort()
    # verify non-overlap
    for a, b in zip(subs, subs[1:]):
        assert a[0] + a[1] <= b[0], f"overlap {a[0]:#x}+{a[1]} > {b[0]:#x}"

    new = bytearray()
    deltas = []  # (old_pos, new_pos) boundary pairs for pointer remap
    pos_old = 0
    for off, ln, enc in subs:
        new.extend(sub[pos_old:off])
        deltas.append((off, len(new)))          # string start
        new.extend(enc)
        new.extend(b"\xff\x03")                 # keep terminator
        pos_old = off + ln
        deltas.append((pos_old, len(new)))      # after string
    new.extend(sub[pos_old:])
    new_sub = bytes(new)

    # pointer remap: pointers exist at 4-aligned positions in the NEW stream,
    # values point at OLD positions. Build old->new mapping from deltas.
    def remap(old_rel):
        # binary search: last boundary <= old_rel; new = boundary_new + (old - boundary_old)
        lo, hi = 0, len(deltas) - 1
        best = (0, 0)
        for o, n in deltas:
            if o <= old_rel:
                best = (o, n)
            else:
                break
        return best[1] + (old_rel - best[0])

    # find pointers in new stream (same positions as old, since pointer bytes
    # are before any text we changed... NOT true: pointers can sit between
    # strings. But pointer SLOTS (file positions) may shift too. We track
    # pointer positions via remap of their old positions.
    # Simpler: pointers in the ORIGINAL at 4-aligned j (rel) -> new position
    # remap(j) (4-alignment can break!). So instead: recompute pointers by
    # scanning the NEW stream for base-relative values and remapping targets,
    # which is valid because all pointer VALUES still hold old targets.
    patched = bytearray(new_sub)
    n_fixed = 0
    for j in range(0, len(patched) - 3, 4):
        v = struct.unpack_from("<I", patched, j)[0]
        if base <= v < base + len(sub):
            old_rel = v - base
            new_rel = remap(old_rel)
            if new_rel != old_rel:
                struct.pack_into("<I", patched, j, base + new_rel)
                n_fixed += 1
    return bytes(patched), n_fixed


def expand_efile(json_path: Path, orig_path: Path, out_path: Path) -> dict:
    d = json.loads(json_path.read_text(encoding="utf-8"))
    data = orig_path.read_bytes()

    # sector table
    secs = []
    i = 0
    while True:
        v = struct.unpack_from("<H", data, i)[0]
        if v == 0:
            break
        secs.append(v)
        i += 2

    # subfile k spans secs[k]..secs[k+1]; the last table entry is the end
    # marker (= file end), so there are len(secs)-1 real subfiles.
    n_sub = len(secs) - 1
    bounds = []
    for k in range(n_sub):
        s0 = secs[k] * 2048
        e0 = secs[k + 1] * 2048
        bounds.append((s0, e0))

    by_sub = [[] for _ in range(n_sub)]
    for ent in d["entries"]:
        for k, (s0, e0) in enumerate(bounds):
            if s0 <= ent["offset"] < e0:
                ent["_rel_off"] = ent["offset"] - s0
                by_sub[k].append(ent)
                break

    # rebuild subfiles
    new_subs = []
    total_fixed = 0
    for k, (s0, e0) in enumerate(bounds):
        sub = data[s0:e0]
        raw_len = e0 - s0
        ents = [x for x in by_sub[k] if x["_rel_off"] + x["length_bytes"] <= raw_len]
        new_sub, fixed = expand_subfile(sub, ents)
        total_fixed += fixed
        pad_to = max(raw_len, ((len(new_sub) + 2047) // 2048) * 2048)
        new_sub = new_sub.ljust(pad_to, b"\x00")
        new_subs.append(new_sub)
    out = bytearray(data[:2048])
    new_secs = []
    cur = 1  # subfiles start at sector 1
    for ns in new_subs:
        new_secs.append(cur)
        out.extend(ns)
        cur += len(ns) // 2048
    # rewrite sector table: starts + end marker
    assert len(new_secs) == n_sub
    for k, sec in enumerate(new_secs):
        struct.pack_into("<H", out, k * 2, sec)
    struct.pack_into("<H", out, n_sub * 2, cur)  # end marker
    struct.pack_into("<H", out, (n_sub + 1) * 2, 0)  # terminator

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    return {
        "file": orig_path.name,
        "orig_size": len(data),
        "new_size": len(out),
        "pointers_fixed": total_fixed,
        "subfiles": n_sub,
    }


def main():
    files = [("E0", "ADV/E0.BIN"), ("E1", "ADV/E1.BIN"),
             ("E2", "ADV/E2.BIN"), ("E3", "ADV/E3.BIN")]
    for name, rel in files:
        st = expand_efile(ROOT / "scripts/final" / f"{name}.json",
                          SRC / rel, OUT / rel)
        print(f"[+] {st['file']}: {st['orig_size']:,} -> {st['new_size']:,} bytes, "
              f"{st['pointers_fixed']} pointers fixed, {st['subfiles']} subfiles")


if __name__ == "__main__":
    main()
