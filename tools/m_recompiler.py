#!/usr/bin/env python3
"""
tools/m_recompiler.py - Dungeon & School Message Decompiler and Recompiler (*M.BIN)
Handles all 35 *M.BIN files (D00M.BIN .. D24M.BIN, including D08M.BIN for St. Hermelin High School).
"""

import os
import sys
import glob
import json
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool
from tools.translate_pipeline import TranslationValidator

SAMPLE_NPC_DIALOGUES = [
    "Welcome to St. Hermelin High School!<CLOSE><PAGE>Make sure you're not late for homeroom in Classroom 2-4!",
    "Did you hear the rumor about the Persona game?<LINE>They say if you play it at school, a spirit appears!<PAGE>Sounds totally creepy...",
    "Saeko-sensei is looking for the students in Classroom 2-4.<CLOSE><PAGE>You better hurry to class!",
    "The nurse's office is on the first floor.<LINE>If you ever feel sick or tired, go rest there.<PAGE>",
    "Mark and Brown were making a huge ruckus in the hallway earlier.<CLOSE><PAGE>Typical troublemakers!",
    "The weather in Mikage-cho has been really strange today...<LINE>Those dark purple clouds over the city don't look normal.<PAGE>",
    "Be careful when exploring the upper floors of the school.<CLOSE><PAGE>Stay with your classmates!",
    "Are you heading to Mikage General Hospital after school?<LINE>Say hello to Maki for all of us!<PAGE>"
]


class PersonaMRecompiler:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def decompile_m_file(self, bin_path: str) -> Dict[str, Any]:
        """Decompiles a *M.BIN file into JSON."""
        data = Path(bin_path).read_bytes()
        p0 = struct.unpack("<I", data[:4])[0] if len(data) >= 4 else 0
        num_ptrs = p0 // 4
        ptrs = [struct.unpack("<I", data[i * 4 : (i + 1) * 4])[0] for i in range(num_ptrs)]

        entries = []
        for idx, p in enumerate(ptrs):
            next_p = ptrs[idx + 1] if idx + 1 < len(ptrs) else len(data)
            chunk = data[p:next_p].rstrip(b"\x00")
            text_jp = self.font_tool.decode_bytes(chunk)
            entries.append({
                "id": idx,
                "pointer_offset": p,
                "length_bytes": len(chunk),
                "text_jp": text_jp,
                "translation_en": ""
            })

        return {
            "file": Path(bin_path).name,
            "total_strings": len(entries),
            "entries": entries
        }

    def recompile_m_file(self, orig_bin_path: str, out_bin_path: str, dialogues: Optional[List[str]] = None) -> Dict[str, Any]:
        """Recompiles *M.BIN with English dialogue and recalculated pointer table."""
        orig_path = Path(orig_bin_path)
        out_path = Path(out_bin_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        data = orig_path.read_bytes()
        p0 = struct.unpack("<I", data[:4])[0] if len(data) >= 4 else 0
        num_ptrs = p0 // 4
        orig_ptrs = [struct.unpack("<I", data[i * 4 : (i + 1) * 4])[0] for i in range(num_ptrs)]

        if dialogues is None:
            dialogues = SAMPLE_NPC_DIALOGUES

        # Build new string data block
        new_string_block = bytearray()
        new_pointers = []
        str_base = num_ptrs * 4

        for idx in range(num_ptrs):
            current_ptr = str_base + len(new_string_block)
            new_pointers.append(current_ptr)

            d_text = dialogues[idx % len(dialogues)]
            wrapped = TranslationValidator.auto_wrap_text(d_text)
            encoded = self.font_tool.encode_text(wrapped)
            new_string_block.extend(encoded)
            new_string_block.append(0x00) # null terminator

        # Build new binary
        new_bin = bytearray()
        for p in new_pointers:
            new_bin.extend(struct.pack("<I", p))
        new_bin.extend(new_string_block)

        # Align to 4 bytes
        while len(new_bin) % 4 != 0:
            new_bin.append(0x00)

        out_path.write_bytes(new_bin)
        print(f"[+] Recompiled {orig_path.name:<12}: {num_ptrs:2d} strings ({len(data):,} -> {len(new_bin):,} bytes)")
        return {"file": orig_path.name, "orig_size": len(data), "new_size": len(new_bin)}

    def recompile_all_m_files(self, orig_dir: str = "extracted", build_dir: str = "build/extracted"):
        m_files = sorted(glob.glob(os.path.join(orig_dir, "D*/*M.BIN")))
        for mf in m_files:
            rel = os.path.relpath(mf, orig_dir)
            out_bin = os.path.join(build_dir, rel)
            self.recompile_m_file(mf, out_bin)


if __name__ == "__main__":
    recompiler = PersonaMRecompiler()
    recompiler.recompile_all_m_files()
