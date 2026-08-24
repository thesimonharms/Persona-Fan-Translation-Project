import json

with open('scripts/retranslate2/chunks/E3_part_02.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

entries = chunk['entries']
for i, e in enumerate(entries):
    print(f"{i:3d} | id={e['id']:3d} | [{e.get('translation_en','')[:30]}] | {e['text_jp']}")
