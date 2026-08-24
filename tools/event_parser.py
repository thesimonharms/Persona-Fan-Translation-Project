#!/usr/bin/env python3
"""
tools/event_parser.py - Story Event Container Decompiler (E0.BIN .. E3.BIN, ADVCMD.BIN, DVL.BIN)
Extracts and decompiles the core story cutscenes (Classroom, Philemon, Hospital, Invasion)
using container sector tables and subfile RAM headers rather than blind regex scanning.
"""

import os
import sys
import json
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool


class PersonaEventParser:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def decompile_event_package(self, bin_path: str) -> Dict[str, Any]:
        """Extracts dialogue strings and control tags from an event package (e.g. E0.BIN)."""
        path = Path(bin_path)
        data = path.read_bytes()
        if len(data) < 2048:
            return {"file": path.name, "type": "STORY_EVENT_PACKAGE", "total_strings": 0, "entries": []}

        # Sector 0 contains 16-bit subfile sector offsets
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
                        # Check if text contains Japanese kana or kanji
                        has_text = any(ord(c) > 127 or c in ":!?「」" for c in text_jp)
                        if has_text:
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
            "type": "STORY_EVENT_PACKAGE",
            "total_subfiles": len(sectors),
            "total_dialogue_subfiles": len(entries),
            "entries": entries
        }

    def decompile_all_events(self):
        out_dir = Path("scripts/original/events")
        out_dir.mkdir(parents=True, exist_ok=True)

        event_files = [
            "extracted/ADV/E0.BIN",
            "extracted/ADV/E1.BIN",
            "extracted/ADV/E2.BIN",
            "extracted/ADV/E3.BIN",
            "extracted/ADV/ADVCMD.BIN",
            "extracted/ADV/ADVCMD0.BIN",
            "extracted/ADV/DVL.BIN",
            "extracted/ADV/TYNSE.BIN"
        ]

        for ef in event_files:
            if os.path.exists(ef):
                res = self.decompile_event_package(ef)
                p = Path(ef)
                out_path = out_dir / f"{p.stem}.json"
                out_path.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[+] Decompiled {p.name} -> events/{p.stem}.json ({res['total_dialogue_subfiles']} dialogue subfiles)")


def main():
    parser = PersonaEventParser()
    parser.decompile_all_events()


if __name__ == "__main__":
    main()
