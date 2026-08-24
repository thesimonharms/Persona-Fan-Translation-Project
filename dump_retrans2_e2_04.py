import json

with open('scripts/retranslate2/chunks/E2_part_04.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

for idx, e in enumerate(chunk['entries']):
    status = "FILLED" if e.get('translation_en', '').strip() not in ['', '...'] else "EMPTY"
    print(f"{idx:3d}\t{e['id']}\t[{status}]\t{e['text_jp']}\t-->\t{e.get('translation_en','')[:30]}")
