import json

with open('scripts/retranslate2/chunks/E2_part_04.json', 'r', encoding='utf-8') as f:
    chunk = json.load(f)

entries = chunk['entries']
print("Total entries:", len(entries))

for b in range(13):
    start = b * 50
    end = min(start + 50, len(entries))
    print(f"=== BLOCK {b} ({start} to {end-1}) ===")
    for idx in range(start, end):
        e = entries[idx]
        cur = e.get('translation_en', '').strip()
        filled = "YES" if cur and cur != '...' else "NO"
        print(f"{idx:3d} (id={e['id']}): [{filled}] {e['text_jp']}")
