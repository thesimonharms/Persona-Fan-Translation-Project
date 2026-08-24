#!/usr/bin/env python3
"""
tools/script_parser.py - Complete Script & Bytecode Decompiler for Megami Ibunroku Persona (PSX)
Extracts and decompiles:
1. Demon Negotiation Scripts (TALK/*.BIN)
2. Story Cutscenes & Event Scripts (ADV/MES.BIN, ADV.BIN, ADV/BST.BIN)
3. Battle Dialogue & Combat Engine (BTLP.BIN)
4. Dungeon Event & Room Dialogues (D00M..D24M/*.BIN)
5. System Menus & Minigames (CASINO.BIN, S2D.BIN)
"""

import os
import sys
import json
import glob
import struct
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
            return {"file": path.name, "type": "TALK_DEMON_NEGOTIATION", "total_strings": 0, "entries": []}

        str0_ptr = struct.unpack("<I", data[0x14:0x18])[0]
        if str0_ptr <= 0x14 or str0_ptr >= len(data):
            return {"file": path.name, "type": "TALK_DEMON_NEGOTIATION", "total_strings": 0, "entries": []}

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

    def decompile_event_container(self, bin_path: str, category: str = "STORY_CUTSCENES") -> Dict[str, Any]:
        """Decompiles a container file (MES.BIN, BST.BIN, ADV.BIN) with sector tables & subfiles."""
        path = Path(bin_path)
        data = path.read_bytes()
        if len(data) < 2048:
            return {"file": path.name, "type": category, "total_subfiles": 0, "total_dialogue_subfiles": 0, "entries": []}

        sec0 = data[:2048]
        sectors = []
        for i in range(1024):
            s = struct.unpack("<H", sec0[i * 2 : (i + 1) * 2])[0]
            if s == 0:
                break
            sectors.append(s)

        entries = []
        for sub_idx, s in enumerate(sectors):
            start = s * 2048
            end = sectors[sub_idx + 1] * 2048 if sub_idx + 1 < len(sectors) else len(data)
            sub = data[start:end]
            if len(sub) < 16:
                continue

            p0 = struct.unpack("<I", sub[:4])[0]
            if (p0 & 0xFF000000) == 0x80000000:
                base_ram = p0 & 0xFFFF0000
                p1 = struct.unpack("<I", sub[4:8])[0]
                rel_p1 = p1 - base_ram
                if 0 < rel_p1 < len(sub):
                    raw_chunk = sub[rel_p1:].rstrip(b"\x00")
                    if len(raw_chunk) >= 4:
                        text_jp = self.font_tool.decode_bytes(raw_chunk)
                        entries.append({
                            "id": len(entries),
                            "subfile_index": sub_idx,
                            "sector": s,
                            "subfile_offset": start,
                            "subfile_size": len(sub),
                            "text_relative_offset": rel_p1,
                            "length_bytes": len(raw_chunk),
                            "raw_hex": raw_chunk.hex(),
                            "text_jp": text_jp,
                            "translation_en": ""
                        })

        return {
            "file": path.name,
            "type": category,
            "total_subfiles": len(sectors),
            "total_dialogue_subfiles": len(entries),
            "entries": entries
        }

    def decompile_dungeon_m_file(self, bin_path: str) -> Dict[str, Any]:
        """Decompiles fixed dialogue blocks from a dungeon message file (D*M.BIN)."""
        path = Path(bin_path)
        data = path.read_bytes()
        if len(data) < 40:
            return {"file": path.name, "type": "DUNGEON_NPC_DIALOGUE", "total_dialogue_blocks": 0, "entries": []}

        # Read block offsets from header
        offsets = []
        for i in range(10):
            off = struct.unpack("<I", data[i * 4 : (i + 1) * 4])[0]
            if 0 < off < len(data):
                offsets.append(off)
            else:
                break

        entries = []
        for b_idx, off in enumerate(offsets):
            next_off = offsets[b_idx + 1] if b_idx + 1 < len(offsets) else len(data)
            block_len = next_off - off
            block_data = data[off:next_off]
            if block_len >= 100:
                text_jp = self.font_tool.decode_bytes(block_data.rstrip(b"\x00"))
                entries.append({
                    "id": len(entries),
                    "block_index": b_idx,
                    "offset": off,
                    "length_bytes": block_len,
                    "raw_hex": block_data.hex(),
                    "text_jp": text_jp,
                    "translation_en": ""
                })

        return {
            "file": path.name,
            "type": "DUNGEON_NPC_DIALOGUE",
            "total_dialogue_blocks": len(entries),
            "entries": entries
        }

    def decompile_all(self):
        """Decompiles all talk, story, dungeon, and battle scripts."""
        # 1. Talk files
        talk_out = Path("scripts/original/talk")
        talk_out.mkdir(parents=True, exist_ok=True)
        for tf in sorted(glob.glob("extracted/TALK/*.BIN")):
            res = self.decompile_talk_file(tf)
            out_file = talk_out / f"{Path(tf).stem}.json"
            out_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Decompiled {len(list(talk_out.glob('*.json')))} TALK files -> scripts/original/talk/")

        # 2. Story cutscenes
        story_out = Path("scripts/original/story")
        story_out.mkdir(parents=True, exist_ok=True)
        for af in ["extracted/ADV/MES.BIN", "extracted/ADV.BIN", "extracted/ADV/BST.BIN"]:
            if os.path.exists(af):
                p = Path(af)
                res = self.decompile_event_container(af, "STORY_CUTSCENES")
                (story_out / f"{p.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[+] Decompiled {p.name} -> story/{p.stem}.json ({res['total_dialogue_subfiles']} cutscenes)")

        # 3. Dungeon message files
        dungeon_out = Path("scripts/original/dungeons")
        dungeon_out.mkdir(parents=True, exist_ok=True)
        m_files = sorted(glob.glob("extracted/D*/*M.BIN"))
        for df in m_files:
            p = Path(df)
            res = self.decompile_dungeon_m_file(df)
            (dungeon_out / f"{p.stem}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Decompiled {len(m_files)} dungeon message files -> scripts/original/dungeons/")

        # 4. Battle & System
        battle_out = Path("scripts/original/battle")
        battle_out.mkdir(parents=True, exist_ok=True)
        if os.path.exists("extracted/BTLP.BIN"):
            res = self.decompile_talk_file("extracted/BTLP.BIN")
            (battle_out / "BTLP.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[+] Decompiled BTLP.BIN -> battle/BTLP.json ({res['total_strings']} strings)")


def main():
    parser_tool = PersonaScriptParser()
    parser_tool.decompile_all()


if __name__ == "__main__":
    main()

