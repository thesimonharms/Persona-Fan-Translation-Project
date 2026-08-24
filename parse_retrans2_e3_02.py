import json

with open('scripts/retranslate2/chunks/E3_part_02.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

entries = chunk['entries']

for b in range(8):
    start = b * 50
    end = min(start + 50, len(entries))
    print(f"=== BLOCK {b} ({start} to {end-1}) ===")
    for idx in range(start, end):
        e = entries[idx]
        cur = e.get('translation_en', '').strip()
        print(f"{idx:3d} (id={e['id']}): [{cur[:25]}] | {e['text_jp']}")
