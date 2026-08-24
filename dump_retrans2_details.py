import json

with open('scripts/retranslate2/chunks/E3_part_02.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

for idx, e in enumerate(chunk['entries']):
    print(f"IDX_{idx:03d}\tID_{e['id']}\t{e['text_jp']}")
