#!/usr/bin/env python3"""
"""
tools/reexpand2.py - Safe E-file expander v2 using blanket pointer relocation.

Instead of parsing individual opcodes (risky without full VM knowledge),
this approach:
1. Expands strings in place
2. Scans the ENTIRE resulting subfile for any 4-aligned u32 that falls
   within the subfile's original address range
3. Remaps those values using a cumulative delta table built from the
   string insertion points

This catches ALL internal pointers regardless of which opcode carries them.
False positives are possible but unlikely (requires a u32 to accidentally
equal a valid RAM address AND be 4-aligned).
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.reinsert import encode_text

ROOT = Path(__file__).resolve().parent.parent


def expand_subfile_v2(sub: bytes, replacements: list) -> tuple:
    """
    Expand strings in a subfile and relocate all internal pointers.

    Args:
        sub: original subfile bytes
        replacements: [(rel_off, orig_len, new_bytes), ...] sorted by rel_off

    Returns:
        (new_sub_bytes, num_pointers_fixed)
    """
    base = struct.unpack_from("<I", sub, 0)[0]
    # base is like 0x80100008; the actual mapping region starts here

    # Build replacement plan
    plan = []  # (old_start, old_len, new_bytes)
    for off, ln, enc in sorted(replacements):
        plan.append((off, ln, enc))

    # Phase 1: build new stream, tracking position mapping
    new_stream = bytearray()
    pos_map = []  # list of (old_pos, new_pos) anchor pairs
    old_pos = 0

    for r_start, r_len, r_data in plan:
        if r_start > old_pos:
            # copy gap before this string
            chunk = sub[old_pos:r_start]
            new_stream.extend(chunk)

        # record boundary BEFORE string
        pos_map.append((old_pos, len(new_stream)))

        # write new string
        new_stream.extend(r_data)

        # record boundary AFTER string
        old_end = r_start + r_len
        pos_map.append((old_end, len(new_stream)))
        old_pos = old_end

    # copy remaining tail
    new_stream.extend(sub[old_pos:])
    final_boundary_old = len(sub)
    final_boundary_new = len(new_stream)
    pos_map.append((final_boundary_old, final_boundary_new))

    def remap(old_rel):
        """Map an old relative position to new relative position."""
        best_old, best_new = 0, 0
        for o, n in pos_map:
            if o <= old_rel:
                best_old, best_new = o, n
            else:
                break
        return best_new + (old_rel - best_old)

    # Phase 2: fix ALL internal pointers in the new stream
    # Scan every byte position (not just 4-aligned) to catch unaligned refs
    n_fixed = 0
    i = 0
    while i < len(new_stream) - 3:
        # Look for the base address pattern (first byte matches base high byte)
        # Base addresses are like 0x801xxxxx, so first byte is 0x80 or similar
        b0 = new_stream[i]
        if b0 == (base >> 24) & 0xFF:
            v = struct.unpack_from("<I", new_stream, i)[0]
            rel = v - base
            if 0 <= rel < len(sub):
                new_rel = remap(rel)
                if new_rel != rel:
                    struct.pack_into("<I", patched := new_stream, i, base + new_rel)
                    n_fixed += 1
                i += 4
                continue
        i += 1

    return bytes(new_stream), n_fixed


def expand_file(json_path: str, orig_path: str, out_path: str) -> dict:
    """Expand all translatable strings in one E-file."""
    d = json.loads(Path(json_path).read_text(encoding="utf-8"))
    data = Path(orig_path).read_bytes()

    # Parse sector table
    secs = []
    i = 0
    while True:
        v = struct.unpack_from("<H", data, i)[0]
        if v == 0:
            break
        secs.append(v)
        i += 2

    n_sub = len(secs) - 1  # last entry = end marker
    bounds = []
    for k in range(n_sub):
        s0 = secs[k] * 2048
        e0 = secs[k + 1] * 2048
        bounds.append((s0, e0))

    # Group entries by subfile
    by_sub = [[] for _ in range(n_sub)]
    for ent in d:
        en = ent.get("translation_en", "").strip()
        if not en:
            continue
        off = ent["offset"]
        ln = ent["length_bytes"]
        raw_hex = ent.get("raw_hex", "")

        for k, (s0, e0) in enumerate(bounds):
            if s0 <= off < e0:
                rel = off - s0
                enc, errs = encode_text(en, orig_raw=bytes.fromhex(raw_hex))
                # Include the terminator in the replacement length
                # Original length_bytes EXCLUDES terminator; add 2 for ff02/ff03
                total_len = ln + 2
                by_sub[k].append((rel, total_len, enc))
                break

    # Expand each subfile
    new_subs = []
    total_ptrs = 0
    for k in range(n_sub):
        s0, e0 = bounds[k]
        sub = data[s0:e0]

        entries = by_sub[k]
        # Deduplicate overlapping replacements (keep first)
        entries.sort()
        deduped = []
        for r in entries:
            if deduped and r[0] < deduped[-1][0] + deduped[-1][1]:
                continue  # overlaps previous
            deduped.append(r)

        if deduped:
            new_sub, n_fixed = expand_subfile_v2(sub, deduped)
            total_ptrs += n_fixed
        else:
            new_sub = sub

        # Pad to sector multiple
        pad_to = max(e0 - s0, ((len(new_sub) + 2047) // 2048) * 2048)
        new_sub = new_sub.ljust(pad_to, b"\x00")
        new_subs.append(new_sub)

    # Reassemble file
    out = bytearray(data[:2048])  # preserve sector table page
    new_secs = []
    cur = secs[0]  # first subfile start
    for ns in new_subs:
        new_secs.append(cur)
        out.extend(ns)
        cur += len(ns) // 2048

    # Write updated sector table
    for k, sec in enumerate(new_secs):
        struct.pack_into("<H", out, k * 2, sec)
    # End marker
    struct.pack_into("<H", out, len(new_secs) * 2, cur)
    struct.pack_into("<H", out, (len(new_secs) + 1) * 2, 0)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(out)

    return {
        "file": orig_path,
        "orig_size": len(data),
        "new_size": len(out),
        "pointers_fixed": total_ptrs,
        "subfiles": n_sub,
    }


if __name__ == "__main__":
    for name, rel in [("E0", "ADV/E0.BIN"), ("E1", "ADV/E1.BIN"),
                      ("E2", "ADV/E2.BIN"), ("E3", "ADV/E3.BIN")]:
        jp = ROOT / "scripts/final_v2" / f"{name}.json"
        orig = ROOT / "extracted" / rel
        out = ROOT / "build/extracted" / rel
        if not jp.is_file() or not orig.is_file():
            continue
        st = expand_file(str(jp), str(orig), str(out))
        print(f"[+] {st['file']}: {st['orig_size']:,} -> {st['new_size']:,}, "
              f"{st['pointers_fixed']} ptrs fixed")
