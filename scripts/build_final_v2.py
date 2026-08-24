import json, sys, glob, os, re
sys.path.insert(0, '.')
from pathlib import Path
from tools.extractor2 import scan_event_strings, find_tims

have = {}
for f in glob.glob('scripts/retranslate/*.json') + glob.glob('scripts/retranslate2/chunks/*.json'):
    if 'PROMPT' in f or 'reference' in f: continue
    try:
        d = json.load(open(f))
        for e in d.get('entries', []):
            jp = e.get('text_jp','').strip()
            en = e.get('translation_en','').strip()
            if jp and en and en != '...' and len(en) >= 2:
                have.setdefault(jp, en)
    except: pass

for f in glob.glob('scripts/translated/talk/*.json'):
    d = json.load(open(f))
    for e in d.get('entries', []):
        jp = e.get('text_jp','').strip()
        en = e.get('translation_en','').strip()
        if jp and en and len(en) >= 2:
            have.setdefault(jp, en)

print(f'Translation pool: {len(have)}')

TBL = {int(k): v for k, v in json.loads(
    Path('docs/tbl/persona_char_table_v2.json').read_text(encoding='utf-8')).items()}
REV = {}
for gid, ch in sorted(TBL.items()):
    REV.setdefault(ch, gid)

def gid_cost(gid):
    # Safe 1-byte range is 0x00-0x7F only. 0x80-0x87 are 2-byte leads
    # and 0xFF is the control lead.
    return 1 if gid < 0x80 else 2

def encode_cost(text):
    total = 0; i = 0; n = len(text)
    while i < n:
        matched = False
        for tag in ["<LINE>","<PAGE>","<CLOSE>","<END>","<CHOICE>",
                    "<PAUSE>","<MENU_A>","<MENU_B>","<NAME?>"]:
            if text.startswith(tag, i):
                total += 2; i += len(tag); matched = True; break
        if text[i] == "[" and i + 3 <= n and text[i+3:i+4] == "]":
            total += 2; i += 4; continue
        gid = REV.get(text[i])
        if gid is None: return -1
        total += gid_cost(gid)
        i += 1
    return total

def condense(text, budget):
    if encode_cost(text) <= budget: return text, True
    words = text.split()
    while len(words) > 1:
        words.pop()
        cand = ' '.join(words)
        if not cand.endswith(('.','!','?')): cand += '.'
        c = encode_cost(cand)
        if 0 <= c <= budget: return cand, True
    return '', False  # never hard-truncate; keep Japanese instead

os.makedirs('scripts/final_v2', exist_ok=True)

for name, path in [('E0','ADV/E0.BIN'), ('E1','ADV/E1.BIN'), ('E2','ADV/E2.BIN'),
                   ('E3','ADV/E3.BIN'), ('ADV','ADV.BIN'), ('S2D','S2D.BIN')]:
    data = Path(f'extracted/{path}').read_bytes()
    runs = scan_event_strings(data, find_tims(data))
    
    entries = []
    seen_off = set()
    stats = {'total': 0, 'translated': 0, 'condensed': 0, 'untranslatable': 0}
    
    for run in runs:
        s_off = run[0]
        if s_off in seen_off: continue
        seen_off.add(s_off)
        
        raw = run[2]
        txt = run[3]
        budget = run[1] - s_off
        stats['total'] += 1
        
        en = have.get(txt.strip(), have.get(txt, ''))
        if not en:
            stats['untranslatable'] += 1
            entries.append({'offset': s_off, 'length_bytes': budget,
                          'raw_hex': raw.hex(), 'text_jp': txt, 'translation_en': ''})
            continue
        
        c = encode_cost(en)
        if c < 0 or c > budget:
            fitted, ok = condense(en, budget)
            if ok and fitted:
                en = fitted; stats['condensed'] += 1; stats['translated'] += 1
            else:
                stats['untranslatable'] += 1
        else:
            stats['translated'] += 1
        
        entries.append({'offset': s_off, 'length_bytes': budget,
                       'raw_hex': raw.hex(), 'text_jp': txt, 'translation_en': en})
    
    out = Path(f'scripts/final_v2/{name}.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(entries, fh, ensure_ascii=False)
    print(f'{name}: {stats["total"]} strings | translated={stats["translated"]} '
          f'condensed={stats["condensed"]} no-trans={stats["untranslatable"]}')
