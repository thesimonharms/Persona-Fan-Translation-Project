#!/usr/bin/env python3
"""
tools/script_parser.py - Script & Bytecode Decompiler for Megami Ibunroku Persona (PSX)
Extracts and decompiles dialogue scripts, demon negotiation conversation trees,
and name databases into structured JSON files with pointer metadata.
"""

import os
import sys
import json
import glob
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.font_tool import PersonaFontTool


class PersonaScriptParser:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def decompile_talk_file(self, bin_path: str) -> Dict[str, Any]:
        """Decompiles a TALK binary (e.g. TALK/SINSI.BIN) into structured script data."""
        path = Path(bin_path)
        data = path.read_bytes()
        if len(data) < 0x14:
            return {"file": path.name, "entries": []}

        # Pointer table starts at offset 0x14
        str0_ptr = struct.unpack("<I", data[0x14:0x18])[0]
        if str0_ptr <= 0x14 or str0_ptr >= len(data):
            return {"file": path.name, "entries": []}

        num_ptrs = (str0_ptr - 0x14) // 4
        ptrs = []
        for i in range(num_ptrs):
            off = struct.unpack("<I", data[0x14 + i * 4 : 0x18 + i * 4])[0]
            if str0_ptr <= off < len(data):
                ptrs.append((i, off))
            else:
                break

        entries = []
        for idx, (p_id, p_off) in enumerate(ptrs):
            next_off = ptrs[idx + 1][1] if idx + 1 < len(ptrs) else len(data)
            raw_chunk = data[p_off:next_off].lstrip(b"\xff").rstrip(b"\x00")
            if raw_chunk:
                text_jp = self.font_tool.decode_bytes(raw_chunk)
                entries.append({
                    "id": p_id,
                    "pointer_offset": 0x14 + p_id * 4,
                    "target_offset": p_off,
                    "length_bytes": len(raw_chunk),
                    "raw_hex": raw_chunk.hex(),
                    "text_jp": text_jp,
                    "translation_en": ""  # To be populated by Gemini translation agent
                })

        return {
            "file": path.name,
            "type": "TALK_DEMON_NEGOTIATION",
            "total_strings": len(entries),
            "entries": entries
        }

    def decompile_all_talk(self, talk_dir: str = "extracted/TALK", out_dir: str = "scripts/original/talk"):
        """Decompiles all 29 TALK/*.BIN demon negotiation files."""
        t_dir = Path(talk_dir)
        o_dir = Path(out_dir)
        o_dir.mkdir(parents=True, exist_ok=True)

        talk_files = sorted(t_dir.glob("*.BIN"))
        print(f"[*] Decompiling {len(talk_files)} demon negotiation files from '{t_dir}'...")

        total_strings = 0
        for tf in talk_files:
            result = self.decompile_talk_file(str(tf))
            out_file = o_dir / f"{tf.stem}.json"
            out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            total_strings += result["total_strings"]
            print(f"    [+] {tf.name:<16}: {result['total_strings']:3d} strings -> {out_file.name}")

        print(f"[+] Successfully decompiled {total_strings} total dialogue lines across {len(talk_files)} TALK files.")


def main():
    parser = argparse.ArgumentParser(description="Megami Ibunroku Persona Script Parser")
    parser.add_argument("--talk-dir", default="extracted/TALK", help="Path to extracted TALK directory")
    parser.add_argument("--out-dir", default="scripts/original/talk", help="Output directory for JSON scripts")

    args = parser.parse_args()

    parser_tool = PersonaScriptParser()
    parser_tool.decompile_all_talk(talk_dir=args.talk_dir, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
