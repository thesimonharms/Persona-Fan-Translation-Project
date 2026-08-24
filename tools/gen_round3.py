#!/usr/bin/env python3
"""Generate round-3 translation package for all untranslated strings."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from pathlib import Path
from collections import Counter
from tools.extractor2 import scan_event_strings, find_tims

ROOT = Path(__file__).resolve().parent.parent

# Load all known translations
have = set()
search_dirs = [
    ROOT / 'scripts/retranslate',
    ROOT / 'scripts/retranslate2/chunks',
    ROOT / 'scripts/translated/talk',
    ROOT / 'scripts/translated/events',
    ROOT / 'scripts/final_v2',
    ROOT / 'scripts/retranslate3',
]
for d in search_dirs:
    if not d.is_dir(): continue
    for f in d.glob('*.json'):
        if 'PROMPT' in f.name: continue
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            ents = data.get('entries', data if isinstance(data, list) else [])
            for e in ents:
                if not isinstance(e, dict): continue
                en = e.get('translation_en', '').strip()
                jp = e.get('text_jp', '').strip()
                if jp and en and en != '...' and len(en) >= 2:
                    have.add(jp)
        except: pass

print(f'Known translated strings: {len(have)}')

# Scan files for untranslated strings
out_dir = ROOT / 'scripts/retranslate3'
out_dir.mkdir(exist_ok=True)

files = {
    'E0': 'ADV/E0.BIN', 'E1': 'ADV/E1.BIN',
    'E2': 'ADV/E2.BIN', 'E3': 'ADV/E3.BIN',
    'ADV': 'ADV.BIN', 'S2D': 'S2D.BIN',
}

total_new = 0
for name, rel in files.items():
    fpath = ROOT / 'extracted' / rel
    if not fpath.is_file(): continue
    data = fpath.read_bytes()
    runs = scan_event_strings(data, find_tims(data))

    seen_jp = set()
    new_strings = []
    for run in runs:
        s_off, e_off, raw, txt = run[0], run[1], run[2], run[3]
        jp = txt.strip()
        if not jp or jp in seen_jp or jp in have: continue
        # Skip kana-index patterns
        cc = Counter(jp)
        if cc.most_common(1)[0][1] / max(len(jp), 1) > 0.4: continue
        # Must have some hiragana/katakana
        kana = sum(1 for c in jp if '\u3040' <= c <= '\u30ff')
        if kana == 0 and len(jp) < 6: continue
        seen_jp.add(jp)
        new_strings.append({'id': len(new_strings), 'text_jp': jp})

    out_path = out_dir / f'{name}.json'
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump({'file': rel, 'entries': new_strings}, fh, ensure_ascii=False, indent=1)
    print(f'{name}: {len(new_strings)} new strings')
    total_new += len(new_strings)

print(f'\nTOTAL NEW: {total_new}')
