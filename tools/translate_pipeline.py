#!/usr/bin/env python3
"""
tools/translate_pipeline.py - Translation Pipeline & Auto-Wrapping Validator for Megami Ibunroku Persona
Manages translation progress, validates control tags (<LINE>, <PAGE>, <CHOICE>),
calculates line lengths, and auto-wraps English text to fit PSX text windows.
"""

import os
import sys
import json
import glob
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
        at natural word boundaries so it never overflows the PSX dialog window.
        """
        # Preserve explicit control tags
        # Replace existing <LINE> and <PAGE> if re-wrapping
        normalized = text.replace("<LINE>", " \n ").replace("<PAGE>", " \f ")
        words = normalized.split()
        
        pages: List[List[str]] = [[]]
        current_line: List[str] = []
        current_len = 0
        
        for w in words:
            if w == "\f":
                if current_line:
                    pages[-1].append(" ".join(current_line))
                    current_line = []
                    current_len = 0
                pages.append([])
                continue
            elif w == "\n":
                if current_line:
                    pages[-1].append(" ".join(current_line))
                    current_line = []
                    current_len = 0
                if len(pages[-1]) >= max_lines_page:
                    pages.append([])
                continue
                
            w_len = len(w)
            # Check if word fits on current line
            space_needed = 1 if current_line else 0
            if current_len + space_needed + w_len <= max_line:
                current_line.append(w)
                current_len += space_needed + w_len
            else:
                # Flush line
                if current_line:
                    pages[-1].append(" ".join(current_line))
                    current_line = []
                    current_len = 0
                    
                # Check page overflow
                if len(pages[-1]) >= max_lines_page:
                    pages.append([])
                    
                current_line.append(w)
                current_len = w_len
                
        if current_line:
            pages[-1].append(" ".join(current_line))
            
        # Rebuild formatted string
        page_strs = []
        for p in pages:
            if p:
                page_strs.append("<LINE>".join(p))
                
        return "<PAGE>".join(page_strs)

    @staticmethod
    def validate_entry(entry: Dict[str, Any]) -> List[str]:
        """Validates control codes, tag balancing, and line lengths for a translated entry."""
        errors = []
        en_text = entry.get("translation_en", "").strip()
        if not en_text:
            return ["Empty translation"]
            
        jp_text = entry.get("text_jp", "")
        
        # Check CHOICE tags
        jp_choices = [t for t in jp_text.split("<") if t.startswith("CHOICE")]
        en_choices = [t for t in en_text.split("<") if t.startswith("CHOICE")]
        if len(jp_choices) != len(en_choices):
            errors.append(f"CHOICE tag mismatch: expected {len(jp_choices)}, found {len(en_choices)}")
            
        # Check CLOSE tag
        if ("<CLOSE>" in jp_text) != ("<CLOSE>" in en_text):
            errors.append("CLOSE tag presence mismatch with original")
            
        # Check line lengths
        pages = en_text.split("<PAGE>")
        for p_idx, page in enumerate(pages):
            lines = page.split("<LINE>")
            if len(lines) > MAX_LINES_PER_PAGE:
                errors.append(f"Page {p_idx} has {len(lines)} lines (maximum is {MAX_LINES_PER_PAGE})")
            for l_idx, line in enumerate(lines):
                # Strip tags for length calculation
                clean_line = line
                for tag in ["<CLOSE>", "<END>"]:
                    clean_line = clean_line.replace(tag, "")
                if "<CHOICE" in clean_line:
                    clean_line = clean_line.split(">")[-1]
                if len(clean_line) > MAX_LINE_CHARS + 6:  # Small tolerance for formatting
                    errors.append(f"Page {p_idx} Line {l_idx} too long ({len(clean_line)} chars): '{clean_line}'")
                    
        return errors


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


def main():
    parser = argparse.ArgumentParser(description="Persona Translation Pipeline")
    parser.add_argument("--status", action="store_true", help="Display translation progress")
    parser.add_argument("--auto-wrap", type=str, help="Test auto-wrapping on given string")

    args = parser.parse_args()
    pipeline = TranslationPipeline()

    if args.auto_wrap:
        wrapped = TranslationValidator.auto_wrap_text(args.auto_wrap)
        print(f"Original: {args.auto_wrap}")
        print(f"Wrapped:\n{wrapped}")
        return

    pipeline.print_status()


if __name__ == "__main__":
    main()
