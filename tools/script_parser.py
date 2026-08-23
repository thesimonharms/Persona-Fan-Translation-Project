#!/usr/bin/env python3
"""
tools/script_parser.py - Complete Script & Bytecode Decompiler for Megami Ibunroku Persona (PSX)
Extracts and decompiles:
1. Demon Negotiation Scripts (TALK/*.BIN)
2. Battle Dialogue & Contact Engine (BTLP.BIN)
3. Story Cutscenes & Event Scripts (ADV/MES.BIN, ADV.BIN)
4. Dungeon Event & Room Dialogues (D00..D04/*.BIN)
5. System Menus & Minigames (CASINO.BIN, OPEN.BIN, S2D.BIN)
"""

import os
import sys
import json
import glob
import struct
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool


class PersonaScriptParser:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def decompile_talk_file(self, bin_path: str) -> Dict[str, Any]:
        """Decompiles a TALK binary into structured script data."""
        path = Path(bin_path)
        data = path.read_bytes()
        if len(data) < 0x14:
            return {"file": path.name, "entries": []}

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
                    "translation_en": ""
                })

        return {
            "file": path.name,
            "type": "TALK_DEMON_NEGOTIATION",
            "total_strings": len(entries),
            "entries": entries
        }

    def decompile_binary_stream(self, bin_path: str, category: str) -> Dict[str, Any]:
        """Scans and extracts all dialogue blocks and strings from a story/battle/system binary."""
        path = Path(bin_path)
        data = path.read_bytes()

        # Find string boundaries using control codes and string terminators
        # Extract meaningful dialogue blocks containing text and control tags
        entries = []
        visited_offsets = set()

        # Search for control codes and text segments
        matches = [m.start() for m in re.finditer(b'\xff[\xf3\xf5\xf6\xfc\xfd\xfe]', data)]
        for m_idx, offset in enumerate(matches):
            if offset in visited_offsets:
                continue

            # Walk backward to find the start of the string
            start = offset
            while start > 0 and (offset - start) < 256:
                b = data[start - 1]
                if b == 0x00:
                    break
                start -= 1

            # Walk forward to find the end of the string
            end = offset
            while end < len(data) and (end - offset) < 512:
                b = data[end]
                if b == 0x00 or (b == 0xFF and end + 1 < len(data) and data[end + 1] in (0xFC, 0xFE)):
                    if b == 0xFF:
                        end += 2
                    break
                end += 1

            raw_chunk = data[start:end].lstrip(b"\x00\xff").rstrip(b"\x00")
            if len(raw_chunk) >= 4:
                for off in range(start, end):
                    visited_offsets.add(off)

                text_jp = self.font_tool.decode_bytes(raw_chunk)
                if any(c in self.font_tool.char_map.values() for c in text_jp):
                    entries.append({
                        "id": len(entries),
                        "offset": start,
                        "length_bytes": len(raw_chunk),
                        "raw_hex": raw_chunk.hex(),
                        "text_jp": text_jp,
                        "translation_en": ""
                    })

        return {
            "file": path.name,
            "type": category,
            "total_strings": len(entries),
            "entries": entries
        }

    def decompile_all(self):
        """Decompiles all talk, battle, story, dungeon, and system scripts."""
        # 1. Talk files
        talk_out = Path("scripts/original/talk")
        talk_out.mkdir(parents=True, exist_ok=True)
        for tf in sorted(glob.glob("extracted/TALK/*.BIN")):
            res = self.decompile_talk_file(tf)
            out_file = talk_out / f"{Path(tf).stem}.json"
            out_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. Battle files
        battle_out = Path("scripts/original/battle")
        battle_out.mkdir(parents=True, exist_ok=True)
        if os.path.exists("extracted/BTLP.BIN"):
            res = self.decompile_binary_stream("extracted/BTLP.BIN", "BATTLE_SYSTEM_AND_QUOTES")
            (battle_out / "BTLP.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[+] Decompiled BTLP.BIN -> battle/BTLP.json ({res['total_strings']} strings)")

        # 3. Story & Adventure cutscenes
        story_out = Path("scripts/original/story")
        story_out.mkdir(parents=True, exist_ok=True)
        for af in ["extracted/ADV/MES.BIN", "extracted/ADV.BIN", "extracted/ADV/BST.BIN"]:
            if os.path.exists(af):
                p = Path(af)
                res = self.decompile_binary_stream(af, "STORY_CUTSCENES")
                (story_out / f"{p.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[+] Decompiled {p.name} -> story/{p.stem}.json ({res['total_strings']} strings)")

        # 4. Dungeon & NPC dialogue files
        dungeon_out = Path("scripts/original/dungeons")
        dungeon_out.mkdir(parents=True, exist_ok=True)
        for df in sorted(glob.glob("extracted/D*/D*.BIN")):
            if not (df.endswith("M.BIN") or df.endswith("S.BIN")):
                p = Path(df)
                res = self.decompile_binary_stream(df, "DUNGEON_NPC_DIALOGUE")
                if res["total_strings"] > 0:
                    (dungeon_out / f"{p.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                    print(f"[+] Decompiled {p.name} -> dungeons/{p.stem}.json ({res['total_strings']} strings)")

        # 5. System & Minigames
        sys_out = Path("scripts/original/system")
        sys_out.mkdir(parents=True, exist_ok=True)
        for sf in ["extracted/CASINO.BIN", "extracted/OPEN.BIN", "extracted/S2D.BIN"]:
            if os.path.exists(sf):
                p = Path(sf)
                res = self.decompile_binary_stream(sf, "SYSTEM_AND_MINIGAMES")
                (sys_out / f"{p.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[+] Decompiled {p.name} -> system/{p.stem}.json ({res['total_strings']} strings)")


def main():
    parser = argparse.ArgumentParser(description="Megami Ibunroku Persona Script Decompiler")
    args = parser.parse_args()
    parser_tool = PersonaScriptParser()
    parser_tool.decompile_all()


if __name__ == "__main__":
    main()
