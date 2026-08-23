#!/usr/bin/env python3
"""
tools/translate_pipeline.py - Translation Pipeline & Auto-Wrapping Validator for Megami Ibunroku Persona
Manages translation progress, validates control tags (<LINE>, <PAGE>, <CHOICE>),
calculates line lengths, and auto-wraps English text with atomic tag preservation.
"""

import os
import sys
import json
import glob
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

MAX_LINE_CHARS = 32     # Maximum half-width characters per text box line
MAX_LINES_PER_PAGE = 3  # Maximum lines visible at once in a dialog window


class TranslationValidator:
    @staticmethod
    def auto_wrap_text(text: str, max_line: int = MAX_LINE_CHARS, max_lines_page: int = MAX_LINES_PER_PAGE) -> str:
        """
        Auto-formats and word-wraps raw English text by inserting <LINE> and <PAGE> tags
        at natural word boundaries, keeping all XML-like tags (<CHOICE id=N>, <CLOSE>, etc.) strictly atomic.
        """
        # Protect control tags by replacing with unique tokens
        tag_pattern = re.compile(r"<[^>]+>")
        tags = tag_pattern.findall(text)
        
        # Replace tags with placeholders
        placeholder_text = text
        placeholders = {}
        for idx, tag in enumerate(tags):
            ph = f"__TAG_{idx}__"
            placeholders[ph] = tag
            placeholder_text = placeholder_text.replace(tag, f" {ph} ", 1)

        # Normalize linebreaks
        words = placeholder_text.split()
        
        pages: List[List[str]] = [[]]
        current_line: List[str] = []
        current_len = 0
        
        for w in words:
            # Check if word is a tag placeholder
            if w in placeholders:
                raw_tag = placeholders[w]
                if raw_tag == "<PAGE>":
                    if current_line:
                        pages[-1].append(" ".join(current_line))
                        current_line = []
                        current_len = 0
                    pages.append([])
                    continue
                elif raw_tag == "<LINE>":
                    if current_line:
                        pages[-1].append(" ".join(current_line))
                        current_line = []
                        current_len = 0
                    if len(pages[-1]) >= max_lines_page:
                        pages.append([])
                    continue
                else:
                    # Non-breaking tag like <CLOSE>, <CHOICE id=...>, etc.
                    current_line.append(raw_tag)
                    continue

            w_len = len(w)
            space_needed = 1 if current_line else 0
            if current_len + space_needed + w_len <= max_line:
                current_line.append(w)
                current_len += space_needed + w_len
            else:
                if current_line:
                    pages[-1].append(" ".join(current_line))
                    current_line = []
                    current_len = 0
                    
                if len(pages[-1]) >= max_lines_page:
                    pages.append([])
                    
                current_line.append(w)
                current_len = w_len
                
        if current_line:
            pages[-1].append(" ".join(current_line))
            
        page_strs = []
        for p in pages:
            if p:
                page_strs.append("<LINE>".join(p))
                
        return "<PAGE>".join(page_strs)


class TranslationPipeline:
    def __init__(self, orig_dir: str = "scripts/original", trans_dir: str = "scripts/translated"):
        self.orig_dir = Path(orig_dir)
        self.trans_dir = Path(trans_dir)
        self.trans_dir.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        """Reports translation progress across all script categories."""
        orig_files = list(self.orig_dir.rglob("*.json"))
        stats = {
            "total_files": len(orig_files),
            "total_strings": 0,
            "translated_strings": 0,
            "files": []
        }

        for of in sorted(orig_files):
            rel = of.relative_to(self.orig_dir)
            tf = self.trans_dir / rel

            o_data = json.loads(of.read_text(encoding="utf-8"))
            o_entries = o_data.get("entries", [])
            total = len(o_entries)
            stats["total_strings"] += total

            trans_count = 0
            if tf.is_file():
                t_data = json.loads(tf.read_text(encoding="utf-8"))
                t_entries = t_data.get("entries", [])
                trans_count = sum(1 for e in t_entries if e.get("translation_en", "").strip())

            stats["translated_strings"] += trans_count
            pct = (trans_count / total * 100) if total > 0 else 0
            stats["files"].append({
                "path": str(rel),
                "total": total,
                "translated": trans_count,
                "percent": f"{pct:.1f}%"
            })

        return stats

    def print_status(self):
        stats = self.get_status()
        pct = (stats["translated_strings"] / stats["total_strings"] * 100) if stats["total_strings"] > 0 else 0
        print(f"\n==================================================")
        print(f" Persona Fan Translation Progress: {pct:.2f}%")
        print(f" Total Strings: {stats['translated_strings']:,} / {stats['total_strings']:,}")
        print(f"==================================================")
        for f in stats["files"][:15]:
            print(f"  {f['path']:<35} : {f['translated']:4d} / {f['total']:4d} ({f['percent']})")
        if len(stats["files"]) > 15:
            print(f"  ... and {len(stats['files']) - 15} more files.")


if __name__ == "__main__":
    pipeline = TranslationPipeline()
    pipeline.print_status()
