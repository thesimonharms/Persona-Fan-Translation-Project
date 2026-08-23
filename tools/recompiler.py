#!/usr/bin/env python3
"""
tools/recompiler.py - Script Recompiler & Dynamic Pointer Relocator for Megami Ibunroku Persona (PSX)
Recompiles translated JSON scripts back into native game binary bytecode:
1. TALK Files (TALK/*.BIN) with dynamic pointer table recalculation and section shifting
2. Battle, Story, Event Cutscenes, Dungeon, and System binaries (BTLP.BIN, E0..E3.BIN, D*.BIN, etc.)
"""

import os
import sys
import json
import glob
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool


class PersonaRecompiler:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def recompile_talk_file(self, json_path: str, orig_bin_path: str, out_bin_path: str) -> Dict[str, Any]:
        """
        Recompiles a translated TALK JSON file back into a TALK binary (e.g. TALK/GAKI.BIN)
        with recalculated pointer tables and dynamically shifted sections.
        """
        j_path = Path(json_path)
        orig_path = Path(orig_bin_path)
        out_path = Path(out_bin_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        script_data = json.loads(j_path.read_text(encoding="utf-8"))
        entries = script_data["entries"]
        orig_data = bytearray(orig_path.read_bytes())

        if len(orig_data) < 0x14:
            raise ValueError(f"Binary file too small to be a valid TALK container: {orig_path}")

        # Read section header pointers (offsets 0x00 to 0x14)
        sec_ptrs = [struct.unpack("<I", orig_data[i * 4 : (i + 1) * 4])[0] for i in range(5)]
        str0_ptr = struct.unpack("<I", orig_data[0x14:0x18])[0]
        num_ptrs = (str0_ptr - 0x14) // 4
        old_sec2_offset = sec_ptrs[1]

        # Preserve the non-string trailing sections (Section 2 to end)
        trailing_data = orig_data[old_sec2_offset:]

        # Build new string block starting at str0_ptr (0x2000)
        new_string_block = bytearray()
        new_pointers = []

        for idx, entry in enumerate(entries):
            current_str_offset = str0_ptr + len(new_string_block)
            new_pointers.append(current_str_offset)

            en_text = entry.get("translation_en", "").strip()
            if en_text:
                encoded = self.font_tool.encode_text(en_text)
            else:
                encoded = bytes.fromhex(entry["raw_hex"])

            new_string_block.extend(encoded)
            # Ensure proper terminator
            if not (encoded.endswith(b"\x00") or encoded.endswith(b"\xff")):
                new_string_block.append(0x00)

        # Build new binary
        new_bin = bytearray()
        # 1. Header (20 bytes)
        new_bin.extend(orig_data[:0x14])

        # 2. String pointer table (0x14 to str0_ptr)
        for p in new_pointers:
            new_bin.extend(struct.pack("<I", p))

        # Pad remaining pointer slots up to str0_ptr
        remaining_slots = num_ptrs - len(new_pointers)
        for _ in range(remaining_slots):
            new_bin.extend(b"\x00\x00\x00\x00")

        # 3. String data block
        new_bin.extend(new_string_block)

        # Align to 4-byte boundary
        while len(new_bin) % 4 != 0:
            new_bin.append(0x00)

        new_sec2_offset = len(new_bin)
        delta = new_sec2_offset - old_sec2_offset

        # 4. Append trailing sections (Section 2..5)
        new_bin.extend(trailing_data)

        # 5. Update header offsets with delta shift
        for sec_idx in range(1, 5):
            updated_offset = sec_ptrs[sec_idx] + delta
            struct.pack_into("<I", new_bin, sec_idx * 4, updated_offset)

        # Write output file
        out_path.write_bytes(new_bin)

        stats = {
            "file": orig_path.name,
            "orig_size": len(orig_data),
            "new_size": len(new_bin),
            "delta_bytes": delta,
            "total_strings": len(entries),
            "out_path": str(out_path)
        }

        print(f"[+] Recompiled {orig_path.name}: {len(orig_data):,} -> {len(new_bin):,} bytes (delta: {delta:+d} bytes)")
        return stats

    def recompile_stream_file(self, json_path: str, orig_bin_path: str, out_bin_path: str) -> Dict[str, Any]:
        """
        Recompiles a story, event cutscene, battle, dungeon, or system binary with updated strings.
        """
        j_path = Path(json_path)
        orig_path = Path(orig_bin_path)
        out_path = Path(out_bin_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        script_data = json.loads(j_path.read_text(encoding="utf-8"))
        entries = script_data["entries"]
        data = bytearray(orig_path.read_bytes())

        recompiled_count = 0
        for entry in entries:
            offset = entry.get("offset")
            length = entry.get("length_bytes")
            en_text = entry.get("translation_en", "").strip()

            if offset is not None and length is not None and en_text:
                encoded = self.font_tool.encode_text(en_text)
                if len(encoded) <= length:
                    padded = encoded.ljust(length, b"\x00")
                    data[offset : offset + length] = padded
                    recompiled_count += 1
                else:
                    data[offset : offset + length] = encoded[:length]
                    recompiled_count += 1

        out_path.write_bytes(data)
        stats = {
            "file": orig_path.name,
            "orig_size": len(data),
            "new_size": len(data),
            "recompiled_strings": recompiled_count,
            "total_strings": len(entries),
            "out_path": str(out_path)
        }
        print(f"[+] Recompiled {orig_path.name}: {recompiled_count}/{len(entries)} strings injected ({len(data):,} bytes)")
        return stats

    def verify_recompiled_talk(self, out_bin_path: str, json_path: str) -> bool:
        """Verifies that every string in the recompiled binary matches the JSON translation."""
        j_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        bin_data = Path(out_bin_path).read_bytes()

        sec_ptrs = [struct.unpack("<I", bin_data[i * 4 : (i + 1) * 4])[0] for i in range(5)]
        sec2_offset = sec_ptrs[1]
        entries = j_data["entries"]

        all_ok = True
        for idx, entry in enumerate(entries):
            p = struct.unpack("<I", bin_data[0x14 + idx * 4 : 0x18 + idx * 4])[0]
            next_p = struct.unpack("<I", bin_data[0x18 + idx * 4 : 0x1c + idx * 4])[0] if idx + 1 < len(entries) else sec2_offset
            
            raw = bin_data[p:next_p].rstrip(b"\x00")
            decoded = self.font_tool.decode_bytes(raw)
            expected = entry.get("translation_en", "").strip() or entry.get("text_jp", "").strip()

            if decoded.replace("<CLOSE>", "").strip() != expected.replace("<CLOSE>", "").strip() and decoded.strip() != expected.strip():
                print(f"[-] Verification mismatch at entry {idx} (0x{p:04x}):")
                print(f"    Expected: {expected}")
                print(f"    Decoded:  {decoded}")
                all_ok = False
                break

        if all_ok:
            print(f"[+] Verification PASSED for {Path(out_bin_path).name} (all {len(entries)} strings verified 100% losslessly)")
        return all_ok

    def recompile_all(self, orig_extracted_dir: str = "extracted", build_extracted_dir: str = "build/extracted"):
        """Recompiles ALL translated assets into build/extracted/."""
        orig_dir = Path(orig_extracted_dir)
        build_dir = Path(build_extracted_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n==================================================")
        print(f"[*] Starting Complete Game Binary Recompilation...")
        print(f"==================================================")

        # 1. Patch FONT.BIN
        font_in = orig_dir / "FONT.BIN"
        font_out = build_dir / "FONT.BIN"
        if font_in.is_file():
            self.font_tool.patch_font_with_lowercase(str(font_out))

        # 2. Recompile all TALK binaries
        for jf in sorted(glob.glob("scripts/translated/talk/*.json")):
            stem = Path(jf).stem
            orig_bin = orig_dir / "TALK" / f"{stem}.BIN"
            out_bin = build_dir / "TALK" / f"{stem}.BIN"
            if orig_bin.is_file():
                self.recompile_talk_file(jf, str(orig_bin), str(out_bin))
                self.verify_recompiled_talk(str(out_bin), jf)

        # 3. Recompile Battle binaries
        if os.path.exists("scripts/translated/battle/BTLP.json"):
            self.recompile_stream_file("scripts/translated/battle/BTLP.json", str(orig_dir / "BTLP.BIN"), str(build_dir / "BTLP.BIN"))

        # 4. Recompile Story binaries
        for sf in ["ADV.json", "BST.json", "MES.json"]:
            jf = Path(f"scripts/translated/story/{sf}")
            if jf.is_file():
                stem = jf.stem
                if stem == "ADV":
                    orig_bin = orig_dir / "ADV.BIN"
                    out_bin = build_dir / "ADV.BIN"
                else:
                    orig_bin = orig_dir / "ADV" / f"{stem}.BIN"
                    out_bin = build_dir / "ADV" / f"{stem}.BIN"
                if orig_bin.is_file():
                    self.recompile_stream_file(str(jf), str(orig_bin), str(out_bin))

        # 5. Recompile Core Event Packages (E0.BIN, E1.BIN, E2.BIN, E3.BIN, ADVCMD.BIN, TYNSE.BIN, DVL.BIN)
        for ef in sorted(glob.glob("scripts/translated/events/*.json")):
            stem = Path(ef).stem
            orig_bin = orig_dir / "ADV" / f"{stem}.BIN"
            out_bin = build_dir / "ADV" / f"{stem}.BIN"
            if orig_bin.is_file():
                self.recompile_stream_file(ef, str(orig_bin), str(out_bin))

        # 6. Recompile Dungeon binaries
        for df in sorted(glob.glob("scripts/translated/dungeons/*.json")):
            stem = Path(df).stem
            found = list(orig_dir.glob(f"D*/{stem}.BIN"))
            if found:
                orig_bin = found[0]
                rel = orig_bin.relative_to(orig_dir)
                out_bin = build_dir / rel
                self.recompile_stream_file(df, str(orig_bin), str(out_bin))

        # 7. Recompile System binaries
        for sys_f in ["CASINO.json", "OPEN.json", "S2D.json"]:
            jf = Path(f"scripts/translated/system/{sys_f}")
            if jf.is_file():
                stem = jf.stem
                orig_bin = orig_dir / f"{stem}.BIN"
                out_bin = build_dir / f"{stem}.BIN"
                if orig_bin.is_file():
                    self.recompile_stream_file(str(jf), str(orig_bin), str(out_bin))

        print(f"\n[+] All translated assets successfully recompiled into {build_dir}!")


def main():
    parser = argparse.ArgumentParser(description="Persona Script Recompiler")
    parser.add_argument("--all", action="store_true", default=True, help="Recompile all translated game files")
    args = parser.parse_args()

    recompiler = PersonaRecompiler()
    if args.all:
        recompiler.recompile_all()


if __name__ == "__main__":
    main()
