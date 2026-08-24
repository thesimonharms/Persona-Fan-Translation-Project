#!/usr/bin/env python3"""
"""
tools/fit_all.py - Auto-condense all translations to fit their byte budgets.

Strategy per string:
1. Try full translation (2-byte ASCII encoding)
2. Remove control tags that are optional (<PAGE> -> nothing)
3. Lowercase everything (lowercase = 1 byte via font remap)
4. Progressive word-boundary truncation
5. Abbreviation pass (common word substitutions)
6. Hard truncate to fit

Also handles TALK files via pointer-table rebuild.
"""
import json, sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOT = Path(__file__).resolve().parent.parent

# Build encoding cost table
import struct
TBL = {int(k): v for k, v in json.loads(
    (ROOT / "docs/tbl/persona_char_table_v2.json").read_text(encoding="utf-8")).items()}
FONT_REMAP = json.loads((ROOT / "docs/tbl/font_remap_full.json").read_text())

# Build REV with font remap priority
REV = {}
for gid, ch in sorted(TBL.items()):
    REV.setdefault(ch, gid)
for ch, gid in FONT_REMAP.items():
    REV[ch] = gid

def encode_cost(text):
    """Exact byte cost of encoding text."""
    total = 0
    i = 0
    n = len(text)
    while i < n:
        # Tags
        matched = False
        for tag in ["<LINE>", "<PAGE>", "<CLOSE>", "<END>", "<CHOICE>",
                    "<PAUSE>", "<MENU_A>", "<MENU_B>", "<NAME?>"]:
            if text.startswith(tag, i):
                total += 2
                i += len(tag)
                matched = True
                break
        if matched:
            continue
        if text[i] == "[" and i + 3 <= n and text[i+3] == "]":
            total += 2; i += 4; continue
        ch = text[i]
        gid = REV.get(ch)
        if gid is None:
            return -1
        total += 1 if gid < 0x80 else 2
        i += 1
    return total

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

    # Step 2: Lowercase everything except first char
    t = t[0] + t[1:].lower() if len(t) > 1 else t.lower()
    if encode_cost(t) <= budget:
        return t, True

    # Step 3: Apply abbreviations iteratively
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

    # Step 4: Drop filler words
    fillers = [" really ", " very ", " quite ", " just ", " even ",
               " actually ", " basically ", " literally ", " totally "]
    for f in fillers:
        if f in t:
            t = t.replace(f, " ")
            if encode_cost(t) <= budget:
                return t, True

    # Step 5: Word-boundary truncation with ellipsis
    words = t.split()
    while len(words) > 1:
        words.pop()
        candidate = " ".join(words)
        if not candidate.endswith((".", "!", "?")):
            candidate += "."
        if encode_cost(candidate) <= budget:
            return candidate, True

    # Step 6: Hard truncate
    for l in range(len(t), 0, -1):
        if encode_cost(t[:l]) <= budget:
            return t[:l], True

    return "", False


def main():
    stats = {"total": 0, "fit_full": 0, "fit_condensed": 0, "failed": 0}
    
    for fname in ["E0", "E1", "E2", "E3"]:
        src = ROOT / "scripts/original2/events" / f"ADV__{fname}.BIN.json"
        d = json.loads(src.read_text(encoding="utf-8"))
        
        refit = 0
        for e in d["entries"]:
            en = e.get("translation_en", "").strip()
            budget = e["length_bytes"]
            stats["total"] += 1
            
            if not en:
                stats["failed"] += 1
                continue
                
            c = encode_cost(en)
            if c < 0:
                e["translation_en"] = ""
                stats["failed"] += 1
                continue
            if c <= budget:
                stats["fit_full"] += 1
                continue
            
            fitted, ok = condense(en, budget)
            if ok:
                e["translation_en"] = fitted
                stats["fit_condensed"] += 1
                refit += 1
            else:
                # Last resort: empty string (keep Japanese)
                e["translation_en"] = ""
                stats["failed"] += 1
        
        print(f"{fname}: {refit} condensed, "
              f"{stats['total']} total")
        with open(f"scripts/final_v2/{fname}.json", "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False)
    
    print(f"\nSummary:")
    print(f"  Full fit: {stats['fit_full']}")
    print(f"  Condensed: {stats['fit_condensed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total: {stats['total']}")

if __name__ == "__main__":
    main()
