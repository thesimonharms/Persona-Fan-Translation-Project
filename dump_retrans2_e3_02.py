import json

with open('scripts/retranslate2/chunks/E3_part_02.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

entries = chunk['entries']
print("Total entries:", len(entries))

for idx, e in enumerate(entries):
    t_en = e.get('translation_en', '').strip()
    status = "FILLED" if t_en and t_en != '...' else "EMPTY"
    print(f"{idx:3d}\t{e['id']}\t[{status}]\t{e['text_jp']}\t-->\t{t_en}")
