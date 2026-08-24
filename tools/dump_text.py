#!/usr/bin/env python3
"""
tools/dump_text.py - Dump all verified game text to scripts/original2/ JSON.

Output schema per file:
{
  "file": "TALK/GAKI.BIN",
  "format": "talk" | "event",
  "encoding": "persona-psx-v2",
  "entries": [
    {
      "id": 0,
      "offset": 8193,          # byte offset in original binary (reinsertion anchor)
      "length_bytes": 41,       # raw byte length
      "raw_hex": "....",        # exact original bytes (lossless reinsertion)
      "text_jp": "...",         # decoded Japanese with named control tags
      "notes": ""               # extractor confidence notes
    }
  ]
}

Control tags in text_jp (translators MUST preserve):
  <LINE> <PAGE> <CLOSE> <END> <CHOICE> <PAUSE> <MENU_A> <MENU_B> <NAME?> [xx]
Remaining {2xx} placeholders are font symbols not yet mapped.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.extractor2 import extract_talk, scan_event_strings, find_tims, decode

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/original2"
OUT.mkdir(parents=True, exist_ok=True)


def is_clean(txt: str, bad: int) -> bool:
    if bad > 1:
        return False
    n = len(txt)
    if n < 3:
        return False
    kana = sum(1 for c in txt if "\u3040" <= c <= "\u309f")
    if kana < 2 and n < 6:
        return False
    from collections import Counter
    cc = Counter(txt)
    if cc.most_common(1)[0][1] / n > 0.4:
        return False
    # Japanese-likeness: common particles / endings / punctuation present?
    import re
    signals = ['って', 'ない', 'です', 'ます', 'だ', 'か', 'よ', 'ね', 'な', 'の', 'に',
               'は', 'を', 'が', 'と', 'る', 'た', 'して', 'てる', 'じゃ', 'けど',
               'れる', 'たり', 'たち', 'たら', 'れば', 'こう', 'そう', 'どう', 'どこ',
               '!', '?', '…', '。', '、', '<LINE>', '<PAGE>', '<CLOSE>', ':']
    score = sum(1 for s in signals if s in txt)
    # Require signal for short strings; longer strings get benefit of doubt
    if n <= 8 and score == 0:
        return False
    # long kana-soup junk (audio/graphics bleed): mostly-kana, no kanji, high repetition
    kanji = sum(1 for c in txt if "\u4e00" <= c <= "\u9fff")
    kata = sum(1 for c in txt if "\u30a0" <= c <= "\u30ff")
    if n >= 12 and kanji == 0 and (kana + kata) / n > 0.9:
        # allow known-clean short exclamations with punctuation
        if not any(p in txt for p in ('!', '?', '…', '<')):
            return False
    return True


def dump_talk():
    stats = {}
    for p in sorted((ROOT / "extracted/TALK").glob("*.BIN")):
        entries = []
        for off, raw in extract_talk(p):
            txt, bad = decode(raw)
            if not txt.strip():
                continue
            entries.append({
                "id": len(entries),
                "offset": off,
                "length_bytes": len(raw),
                "raw_hex": raw.hex(),
                "text_jp": txt,
                "notes": "" if bad == 0 else f"{bad} unresolved glyphs",
            })
        rel = f"TALK/{p.stem}"
        (OUT / "talk").mkdir(exist_ok=True)
        (OUT / "talk" / f"{p.stem}.json").write_text(
            json.dumps({"file": rel, "format": "talk", "encoding": "persona-psx-v2",
                        "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
        stats[rel] = len(entries)
    return stats


def dump_events():
    stats = {}
    files = ["ADV/E0.BIN", "ADV/E1.BIN", "ADV/E2.BIN", "ADV/E3.BIN",
             "ADV.BIN", "S2D.BIN", "BTLP.BIN", "CASINO.BIN", "OPEN.BIN", "DNG.BIN"]
    files += sorted(str(p.relative_to(ROOT / "extracted"))
                    for d in ("D00", "D01", "D02", "D03", "D04")
                    for p in (ROOT / "extracted" / d).glob("D*.BIN")
                    if p.suffix == ".BIN" and p.stat().st_size > 50000)
    for rel in files:
        p = ROOT / "extracted" / rel
        if not p.is_file():
            continue
        data = p.read_bytes()
        runs = scan_event_strings(data, find_tims(data))
        entries = []
        seen = set()
        for s, e, raw, txt in runs:
            if not is_clean(txt, 0):
                continue
            key = (s, e)
            if key in seen:
                continue
            seen.add(key)
            entries.append({
                "id": len(entries),
                "offset": s,
                "length_bytes": e - s,
                "raw_hex": raw.hex(),
                "text_jp": txt,
            })
        if not entries:
            continue
        outp = OUT / "events" / (rel.replace("/", "__") + ".json")
        outp.parent.mkdir(exist_ok=True)
        outp.write_text(json.dumps({"file": rel, "format": "event",
                                    "encoding": "persona-psx-v2",
                                    "entries": entries}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        stats[rel] = len(entries)
    return stats


if __name__ == "__main__":
    t = dump_talk()
    e = dump_events()
    print("=== TALK ===")
    for k, v in t.items():
        print(f"{v:5d}  {k}")
    print("=== EVENTS ===")
    for k, v in e.items():
        print(f"{v:5d}  {k}")
    print(f"TOTAL: {sum(t.values()) + sum(e.values())} strings")
