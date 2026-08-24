#!/usr/bin/env python3
"""
scripts/retranslate/validate_and_merge.py
Validates translation chunks and merges them into the final retranslated JSON files.
"""

import json
import re
from pathlib import Path

RETRANS_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = RETRANS_DIR / "chunks"

TARGET_FILES = {
    "ADV.json": ("ADV", 38),
    "S2D.json": ("S2D", 99),
    "E3.json": ("E3", 1642),
    "E2.json": ("E2", 3207),
    "E1.json": ("E1", 4067),
    "E0.json": ("E0", 5096),
}

def check_status():
    print(f"{'Chunk File':<20} | {'Total':<6} | {'Done':<6} | {'Empty':<6} | {'Ellipsis':<8} | {'Status'}")
    print("-" * 65)
    
    total_all = 0
    done_all = 0
    
    for target, (prefix, exp_total) in TARGET_FILES.items():
        chunk_files = sorted(CHUNKS_DIR.glob(f"{prefix}_part_*.json"))
        target_total = 0
        target_done = 0
        
        for cf in chunk_files:
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
            entries = data.get("entries", [])
            total = len(entries)
            target_total += total
            total_all += total
            
            done = 0
            empty = 0
            ellipsis = 0
            for e in entries:
                tr = e.get("translation_en", "").strip()
                jp = e.get("text_jp", "").strip()
                if not tr:
                    empty += 1
                elif tr == "...":
                    ellipsis += 1
                    done += 1
                else:
                    done += 1
            
            target_done += done
            done_all += done
            status = "COMPLETE" if empty == 0 else f"{empty} pending"
            print(f"{cf.name:<20} | {total:<6} | {done:<6} | {empty:<6} | {ellipsis:<8} | {status}")
            
    print("-" * 65)
    pct = (done_all / total_all * 100) if total_all > 0 else 0
    print(f"Overall Progress: {done_all}/{total_all} ({pct:.2f}%)")

def merge_all():
    print("\n[*] Merging chunks into master files...")
    for target, (prefix, exp_total) in TARGET_FILES.items():
        chunk_files = sorted(CHUNKS_DIR.glob(f"{prefix}_part_*.json"))
        merged_entries = []
        
        for cf in chunk_files:
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
            merged_entries.extend(data.get("entries", []))
            
        print(f"  {target}: {len(merged_entries)} entries (expected {exp_total})")
        if len(merged_entries) != exp_total:
            print(f"  [!] WARNING: Entry count mismatch for {target}!")
            
        target_path = RETRANS_DIR / target
        with open(target_path, "r", encoding="utf-8") as f:
            orig_data = json.load(f)
            
        orig_data["entries"] = merged_entries
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(orig_data, f, ensure_ascii=False, indent=1)
        print(f"  [+] Wrote {target_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge_all()
    else:
        check_status()
