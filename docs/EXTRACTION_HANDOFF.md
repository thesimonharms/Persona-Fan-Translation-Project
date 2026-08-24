# Extracted Text Handoff — Translation Input Spec

**Source:** `scripts/original2/` (67 files, 51,712 strings)
**Tools:** `tools/extractor2.py` (encoding + format parsers), `tools/dump_text.py` (dumper)
**Char table:** `docs/tbl/persona_char_table_v2.json` (glyph id → Unicode, 2048 entries)

---

## 1. Game text encoding (verified)

- **1-byte codes** → glyph ids 0–255:
  - `0x00` space, `0x01–0x2E` hiragana gojūon, `0x2F–0x47` dakuten hiragana,
    `0x48–0x51` smalls (ぁぃぅぇぉ っゃゅょゎ), `0x52–0x7F` half-width katakana gojūon,
    `0x80–0x87` (lead bytes — see below), `0x88–0xFF` single bytes for
    full-width katakana (dakuten set, 136–165), ASCII (166–201), punctuation/symbols (202–255)
- **2-byte codes**: lead `0x80–0x87` + index byte → glyph id `((lead & 0x7F) << 8) | index`
  → kanji (256–1791), Greek/symbols (1792–1826), **lowercase a–z (1827–1861)**,
    tail symbols (1862–2047)
- **Kanji bank is custom-ordered** (NOT JIS order). Do not assume — always use the table.

### Known symbol glyphs
| Glyph | Char | | Glyph | Char |
|---|---|---|---|---|
| 204 | ー | | 213 | 、 |
| 206 | ・ | | 214 | 〜 |
| 207 | 。 | | 215 | … |
| 218/219 | 「 」 | | 220 | 『 |
| 227 | × | | 1847 | 』 |
| 234 | ○ | | 236 | □ |
| 238 | △ | | 243/244 | ♂ ♀ |

`{2xx}` placeholders in `text_jp` = unmapped glyphs; keep them **verbatim**.

---

## 2. Control codes (dialogue engine)

Raw `FF xx` pairs decode to named tags. **Translators MUST preserve all tags** —
they drive line breaks, paging, and window behavior.

| Tag | Bytes | Meaning |
|---|---|---|
| `<LINE>` | FF F5 | line break in text window |
| `<PAGE>` | FF F6 | page break / player waits |
| `<CLOSE>` | FF FC | close dialogue window |
| `<END>` | FF FE | end of message block |
| `<CHOICE>` | FF FD | choice node (argument follows in raw) |
| `<PAUSE>` | FF F1 | beat/pause |
| `<MENU_A>`/`<MENU_B>` | FF FB / FF F7 | negotiation menu delimiters (TALK) |
| `<NAME?>` | FF F3 | speaker-name control |
| `[xx]` | FF xx | other opcode — preserve exactly |

In TALK files the FF F3 argument byte directly follows; event scripts (E0–E3)
frame text with `FF 21` (display) and terminate with `FF 02`/`FF 03`.

---

## 3. JSON schema

One file per game binary: `scripts/original2/talk/<NAME>.json`, `scripts/original2/events/<PATH__NAME>.json`.

```json
{
  "file": "TALK/GAKI.BIN",
  "format": "talk",              // "talk" = pointer-table container, "event" = ff-framed script
  "encoding": "persona-psx-v2",
  "entries": [
    {
      "id": 0,
      "offset": 8193,           // byte offset in the ORIGINAL binary (reinsertion anchor)
      "length_bytes": 41,
      "raw_hex": "31 1a 48 …",  // exact original bytes — lossless reinsertion fallback
      "text_jp": "ぐはぁ!<CLOSE><PAGE>アニギに惚れちまうぜ!",
      "translation_en": ""      // <- fill this
    }
  ]
}
```

### Translation rules
1. Fill `translation_en` only. Never edit `text_jp`, `raw_hex`, `offset`, `length_bytes`.
2. Preserve every tag (`<LINE>`, `<PAGE>`, `<CLOSE>`, `[xx]`, `{2xx}`) in position-equivalent order.
3. Japanese full-width space (0x00 → `" "`) is a word separator; use normal spaces in English.
4. **Length budget:** the original byte length is the safe in-place cap. English
   expansions will need the pointer-relocation recompiler (planned) — for now,
   keep translations ≤ roughly 1.6× the Japanese character count and we'll
   measure precisely at reinsertion.
5. Speaker names appear inline as `名前:` (e.g. `ゆきの:`, `マ{204}ク:` = マーク/Mark).
   Character glossary: `docs/translation_guide.md`, `docs/lore_glossary.json`.
6. `{204}` inside names is ー (long-vowel mark): マ{204}ク = マーク = Mark.

---

## 4. Corpus contents

| Group | Files | Strings | Content |
|---|---|---|---|
| TALK | 29 | 13,279 | Demon negotiation dialogue (exact pointer-table extraction, 0 suspicious) |
| ADV/E0–E3 | 4 | 38,085 | Story cutscenes (opening, school, hospital, Snow Queen) |
| ADV.BIN | 1 | 43 | System messages (save/memory card) |
| S2D.BIN | 1 | 116 | Casino/side-game dialogue |
| D*/D*.BIN | 26 | ~190 | Dungeon/NPC messages |
| BTLP/DNG/OPEN | 3 | 8 | Battle/dungeon/opening fragments |

**Not text** (verified, excluded): MES.BIN, BST.BIN, BVB.BIN, SVB.BIN, EBG.BIN (voice/bgm banks),
DxxS.BIN (formation), DxxM.BIN (BGM), NAMEDT.BIN (name-entry UI graphics),
NAME.BIN (pure MIPS code — item/demon names NOT in this file; likely in SLPS_005.00,
still to locate).

### Known quality caveats
- **Kanji table ~95% accurate** on the ~1,000 most-used glyphs; rarer kanji may be
  misidentified (e.g. 場会 should read 場合, 選捉 should read 選択 — the kana
  is reliable, individual rare kanji may be wrong). Flag anything reading oddly.
- E0–E3 strings include some repeated system strings (card-game help text) —
  genuine duplicates in the original.
- A handful of short junk strings (<10 total) survive in BTLP/DNG/OPEN dumps — skip them.

## 5. Reinsertion contract

Reinsertion will use `offset` + `raw_hex` per entry, re-encoding `translation_en`
through the same table (`docs/tbl/persona_char_table_v2.json` inverse mapping),
with these guarantees:
- TALK: pointer table rebuilt, strings relocated (already-proven `extract_talk_final` rule).
- Event scripts: in-place replacement where `len(encoded_en) <= length_bytes`,
  otherwise region rebuild with offset fixups (recompiler work, next phase).
