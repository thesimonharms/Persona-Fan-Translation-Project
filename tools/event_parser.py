#!/usr/bin/env python3
"""
tools/event_parser.py - Story Event Container Decompiler (E0.BIN .. E3.BIN, ADVCMD.BIN, DVL.BIN)
Extracts, translates, and recompiles the core story cutscenes (Classroom, Philemon, Hospital, Invasion).
"""

import os
import sys
import json
import struct
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool
from tools.translate_pipeline import TranslationValidator


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

        # Find string boundaries using control codes and string terminators
        entries = []
        visited_offsets = set()

        matches = [m.start() for m in re.finditer(b'\xff[\xf3\xf5\xf6\xfc\xfd\xfe]', data)]
        for m_idx, offset in enumerate(matches):
            if offset in visited_offsets:
                continue

            start = offset
            while start > 0 and (offset - start) < 256:
                b = data[start - 1]
                if b == 0x00:
                    break
                start -= 1

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
            "type": "STORY_EVENT_PACKAGE",
            "total_strings": len(entries),
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
                print(f"[+] Decompiled {p.name:<14} -> events/{p.stem}.json ({res['total_strings']:4d} strings)")


if __name__ == "__main__":
    parser = PersonaEventParser()
    parser.decompile_all_events()
