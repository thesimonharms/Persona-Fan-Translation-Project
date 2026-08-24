#!/usr/bin/env python3
"""
tools/mes_recompiler.py - Full Cutscene Story Engine Recompiler (ADV/MES.BIN - 257 Cutscenes)
Recompiles all cutscenes in MES.BIN safely using container sector tables and subfile RAM headers.
"""

import os
import sys
import json
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool


class PersonaMESRecompiler:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def recompile_all_cutscenes(
        self,
        orig_mes_path: str = "extracted/ADV/MES.BIN",
        out_mes_path: str = "build/extracted/ADV/MES.BIN",
        json_path: Optional[str] = None
    ):
        orig_path = Path(orig_mes_path)
        out_path = Path(out_mes_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        data = bytearray(orig_path.read_bytes())
        if len(data) < 2048:
            out_path.write_bytes(data)
            return

        # Sector table in Sector 0
        sec_table = []
        for i in range(1024):
            val = struct.unpack("<H", data[i * 2 : (i + 1) * 2])[0]
            if val == 0:
                break
            sec_table.append(val)

        # Load translation entries if available
        j_path = json_path or ("scripts/translated/story/MES.json" if os.path.exists("scripts/translated/story/MES.json") else "scripts/original/story/MES.json")
        j_entries = {}
        if os.path.exists(j_path):
            j_data = json.loads(Path(j_path).read_text(encoding="utf-8"))
            for e in j_data.get("entries", []):
                s_idx = e.get("subfile_index")
                if s_idx is not None:
                    j_entries[s_idx] = e

        print(f"[*] Recompiling {len(sec_table)} cutscenes in MES.BIN ({len(data):,} bytes)...")

        recompiled_cutscenes = 0
        for idx, sec in enumerate(sec_table):
            byte_off = sec * 2048
            next_sec = sec_table[idx + 1] if idx + 1 < len(sec_table) else (len(data) // 2048)
            sub_len = (next_sec - sec) * 2048
            sub_data = bytearray(data[byte_off : byte_off + sub_len])

            if len(sub_data) < 16:
                continue

            p0 = struct.unpack("<I", sub_data[:4])[0]
            if (p0 & 0xFF000000) == 0x80000000:
                base_ram = p0 & 0xFFFF0000
                p1 = struct.unpack("<I", sub_data[4:8])[0]
                str_rel = p1 - base_ram

                if 0 < str_rel < len(sub_data) and idx in j_entries:
                    entry = j_entries[idx]
                    en_text = entry.get("translation_en", "").strip()
                    if en_text:
                        encoded = self.font_tool.encode_text(en_text, mode="adv")
                        max_allowed = len(sub_data) - str_rel
                        fit_len = min(len(encoded), max_allowed)
                        sub_data[str_rel : str_rel + fit_len] = encoded[:fit_len]
                        if str_rel + fit_len < len(sub_data):
                            sub_data[str_rel + fit_len :] = b"\x00" * (len(sub_data) - (str_rel + fit_len))
                        data[byte_off : byte_off + len(sub_data)] = sub_data
                        recompiled_cutscenes += 1

        out_path.write_bytes(data)
        print(f"[+] Recompiled {recompiled_cutscenes}/{len(sec_table)} cutscenes into {out_path} ({len(data):,} bytes)")


if __name__ == "__main__":
    recompiler = PersonaMESRecompiler()
    recompiler.recompile_all_cutscenes()

