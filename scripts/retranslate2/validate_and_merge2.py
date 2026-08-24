#!/usr/bin/env python3
"""
scripts/retranslate2/validate_and_merge2.py
Validates and merges Round 2 translation chunks for Megami Ibunroku Persona.
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = BASE_DIR / "chunks"

CHUNK_FILES = [
    ("E3_part_01.json", 399),
    ("E3_part_02.json", 398),
    ("E1_part_01.json", 568),
    ("E1_part_02.json", 568),
    ("E1_part_03.json", 567),
    ("E2_part_01.json", 616),
    ("E2_part_02.json", 616),
    ("E2_part_03.json", 616),
    ("E2_part_04.json", 613),
    ("E0_part_01.json", 591),
    ("E0_part_02.json", 591),
    ("E0_part_03.json", 591),
    ("E0_part_04.json", 591),
    ("E0_part_05.json", 591),
    ("E0_part_06.json", 591),
]

MASTER_FILES = {
    "E3.json": ["E3_part_01.json", "E3_part_02.json"],
    "E1.json": ["E1_part_01.json", "E1_part_02.json", "E1_part_03.json"],
    "E2.json": ["E2_part_01.json", "E2_part_02.json", "E2_part_03.json", "E2_part_04.json"],
    "E0.json": ["E0_part_01.json", "E0_part_02.json", "E0_part_03.json", "E0_part_04.json", "E0_part_05.json", "E0_part_06.json"],
}

def validate_chunk(filename, expected_count):
    filepath = CHUNKS_DIR / filename
    if not filepath.exists():
        return False, 0, 0, 0, "MISSING"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, 0, 0, 0, f"JSON_ERROR: {e}"

    entries = data.get("entries", [])
    if len(entries) != expected_count:
        return False, len(entries), 0, 0, f"COUNT_MISMATCH ({len(entries)} != {expected_count})"

    empty_count = 0
    ellipsis_count = 0
    done_count = 0

    for e in entries:
        trans = e.get("translation_en", "")
        jp = e.get("text_jp", "")
        if not trans or trans.strip() == "":
            empty_count += 1
        elif trans in ("...", "!", "?") and jp not in ("……", "…", "!", "?"):
            ellipsis_count += 1
            done_count += 1
        else:
            done_count += 1

    status = "COMPLETE" if empty_count == 0 else f"{empty_count} pending"
    return True, len(entries), done_count, empty_count, ellipsis_count, status

def check_all():
    print(f"{'Chunk File':20s} | {'Total':6s} | {'Done':6s} | {'Empty':6s} | {'Ellipsis':8s} | {'Status'}")
    print("-" * 75)
    total_all = 0
    done_all = 0
    for fname, exp_count in CHUNK_FILES:
        res = validate_chunk(fname, exp_count)
        if len(res) == 6:
            ok, total, done, empty, ellipsis, status = res
            print(f"{fname:20s} | {total:<6d} | {done:<6d} | {empty:<6d} | {ellipsis:<8d} | {status}")
            total_all += total
            done_all += done
        else:
            print(f"{fname:20s} | {res[-1]}")
    print("-" * 75)
    pct = (done_all / total_all * 100) if total_all > 0 else 0
    print(f"Round 2 Overall Progress: {done_all}/{total_all} ({pct:.2f}%)\n")

def merge_all():
    print("\n[*] Merging Round 2 chunks into master files...")
    for master_name, chunk_list in MASTER_FILES.items():
        all_entries = []
        for chunk_name in chunk_list:
            chunk_file = CHUNKS_DIR / chunk_name
            with open(chunk_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            all_entries.extend(cdata["entries"])

        master_path = BASE_DIR / master_name
        with open(master_path, "r", encoding="utf-8") as f:
            mdata = json.load(f)

        assert len(mdata["entries"]) == len(all_entries), f"Count mismatch for {master_name}: {len(mdata['entries'])} != {len(all_entries)}"
        mdata["entries"] = all_entries

        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(mdata, f, ensure_ascii=False, indent=1)
        print(f"  {master_name}: {len(all_entries)} entries merged into {master_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge_all()
    else:
        check_all()
