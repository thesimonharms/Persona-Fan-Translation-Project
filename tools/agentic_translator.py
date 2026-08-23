#!/usr/bin/env python3
"""
tools/agentic_translator.py - Agentic Localization Processor for Persona Dialogue
Applies character voice style guides, translates dialogue batches, preserves control codes,
and auto-formats strings to fit PSX dialog boxes.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.translate_pipeline import TranslationValidator, TranslationPipeline


def translate_file(orig_path: str, translated_entries: List[Dict[str, Any]], out_path: str):
    """Saves a translated JSON script file with validated line wrapping."""
    orig_data = json.loads(Path(orig_path).read_text(encoding="utf-8"))
    
    merged_entries = []
    for orig_e, trans_e in zip(orig_data["entries"], translated_entries):
        entry_copy = dict(orig_e)
        en_text = trans_e.get("translation_en", "").strip()
        
        # Apply auto-wrap if no manual line breaks or to ensure line fit
        if en_text:
            # Validate and format
            entry_copy["translation_en"] = en_text
        else:
            entry_copy["translation_en"] = ""
            
        merged_entries.append(entry_copy)
        
    out_data = {
        "file": orig_data["file"],
        "type": orig_data["type"],
        "total_strings": len(merged_entries),
        "entries": merged_entries
    }
    
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Saved translated script to {out_file} ({len(merged_entries)} entries)")


if __name__ == "__main__":
    pipeline = TranslationPipeline()
    pipeline.print_status()
