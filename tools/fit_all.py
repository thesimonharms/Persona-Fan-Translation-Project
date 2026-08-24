#!/usr/bin/env python3
"""
tools/fit_all.py - Preview how many translations fit under the encode-time
1-byte remap. Does NOT rewrite scripts/translated/.

Writes a report to build/fit_preview.json only.
"""
import json, sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOT = Path(__file__).resolve().parent.parent

from tools.extractor2 import TBL
from tools.font_remap import encode_text, drop_speaker

REV = {}
for gid, ch in TBL.items():
    REV.setdefault(ch, gid)

def encode_cost(text):
    enc, errs = encode_text(text, rev=REV)
    if errs:
        return -1
    return len(enc)

# Common abbreviations that preserve meaning while saving bytes
ABBREVIATIONS = {
    "you ": "u ", "You ": "U ", "your ": "ur ", "Your ": "Ur ",
    "are ": "r ", "Are ": "R ", "would": "wld", "Would": "Wld",
    "could ": "cld ", "should ": "shd ", "about ": "abt ",
    "really ": "rly ", "very ": "vry ", "because": "cuz",
    "Before": "B4", "before": "b4", "to be": "2b", "To be": "2B",
    "going to": "gonna", "Going to": "Gonna",
    "something": "sumthin", "Something": "Sumthin",
    "everyone": "evry1", "Everyone": "Evry1",
    "probably": "prolly", "Probably": "Prolly",
    "right now": "rn", "Right now": "RN",
    "thank you": "thx", "Thanks": "Thx",
    "what is": "whats", "What is": "Whats",
    "that is": "thats", "That is": "Thats",
    "do not": "dont", "Do not": "Dont",
    "cannot": "cant", "Cannot": "Cant",
    "it is": "its", "It is": "Its",
}

def condense(text: str, budget: int) -> tuple:
    """Try to make text fit budget. Returns (fitted_text, success)."""
    if encode_cost(text) <= budget:
        return text, True

    # Step 1: Remove optional spacing
    t = text.replace("  ", " ")

    # Step 2: Apply abbreviations iteratively
    changed = True
    while changed:
        changed = False
        for abbr, short in ABBREVIATIONS.items():
            if abbr in t:
                new = t.replace(abbr, short)
                if encode_cost(new) <= budget:
                    return new, True
                if len(new) < len(t):
                    t = new; changed = True

    # Step 3: Drop filler words
    fillers = [" really ", " very ", " quite ", " just ", " even ",
               " actually ", " basically ", " literally ", " totally "]
    for f in fillers:
        if f in t:
            t = t.replace(f, " ")
            if encode_cost(t) <= budget:
                return t, True

    # Step 4: Word-boundary truncation with ellipsis
    words = t.split()
    while len(words) > 1:
        words.pop()
        candidate = " ".join(words)
        if not candidate.endswith((".", "!", "?")):
            candidate += "."
        if encode_cost(candidate) <= budget:
            return candidate, True

    # Never hard-truncate: a mid-sentence cut reads worse than Japanese.
    return "", False


def main():
    stats = {"total": 0, "fit_full": 0, "fit_drop_speaker": 0, "failed": 0}
    leftovers = []

    files = [
        ("E0", ROOT / "scripts/translated/events/E0.json"),
        ("E1", ROOT / "scripts/translated/events/E1.json"),
        ("E2", ROOT / "scripts/translated/events/E2.json"),
        ("E3", ROOT / "scripts/translated/events/E3.json"),
        ("ADV", ROOT / "scripts/translated/story/ADV.json"),
        ("S2D", ROOT / "scripts/translated/system/S2D.json"),
    ]
    for fname, src in files:
        d = json.loads(src.read_text(encoding="utf-8"))
        file_failed = 0
        for e in d["entries"]:
            en = e.get("translation_en", "").strip()
            budget = e["length_bytes"]
            stats["total"] += 1
            if not en:
                stats["failed"] += 1
                file_failed += 1
                continue
            c = encode_cost(en)
            if 0 <= c <= budget:
                stats["fit_full"] += 1
                continue
            dropped = drop_speaker(en)
            cd = encode_cost(dropped)
            if dropped != en and 0 <= cd <= budget:
                stats["fit_drop_speaker"] += 1
                continue
            stats["failed"] += 1
            file_failed += 1
            leftovers.append({
                "file": fname, "offset": e.get("offset"),
                "budget": budget, "need": c, "en": en[:80],
                "text_jp": e.get("text_jp", "")[:40],
            })
        print(f"{fname}: leftover {file_failed}")

    out = ROOT / "build/fit_preview.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"stats": stats, "leftovers": leftovers},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nSummary (scripts/translated left untouched):")
    print(f"  Full fit: {stats['fit_full']}")
    print(f"  Speaker-drop fit: {stats['fit_drop_speaker']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total: {stats['total']}")
    print(f"  Report: {out}")

if __name__ == "__main__":
    main()
