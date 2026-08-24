# Task: Translate Megami Ibunroku Persona (PSX, 1996) — Story Script

You are translating the Japanese script of the 1996 PlayStation game
*Megami Ibunroku Persona* (the original Persona 1) into English for a fan
translation. A previous translation attempt FAILED because it returned "..."
for most strings. **That is not acceptable.** Every single string must receive
a genuine translation.

## Input files (JSON, in `scripts/retranslate/`)

- `E0.json` (5,096 strings) — story cutscenes: intro, school, hospital, invasion
- `E1.json` (4,067 strings) — mid-game story
- `E2.json` (3,207 strings) — late story, includes casino/card-game help
- `E3.json` (1,642 strings) — Snow Queen Quest
- `ADV.json` (38) — system messages (save/memory card)
- `S2D.json` (99) — casino dialogue
- `ALREADY_TRANSLATED_reference.json` — 715 strings already translated.
  Use for consistency of names/voice. Strings in this file do NOT need
  re-translation.

Each entry has: `id`, `offset` (ignore — technical anchor), `text_jp`.
You must add a `translation_en` field to every entry.

## CRITICAL RULES

1. **EVERY entry gets a real translation.** Never output "...", "!", "?", or
   any placeholder. If the Japanese is short ("うん"), translate it ("Yeah.").
   If it's an interjection, translate it ("Whoa!"). No skipping, no filler.
2. **Preserve all control tags EXACTLY, in order:**
   - `<LINE>` = line break in the text window
   - `<PAGE>` = page break (player presses button)
   - `<CLOSE>` = close the dialogue window
   - `<END>` = end of message block
   - `<CHOICE>` = choice node
   - `<PAUSE>`, `<MENU_A>`, `<MENU_B>`, `<NAME?>`, `[xx]` — keep verbatim,
     keep position (or the game will crash/misrender).
3. **`{204}` = ー (long-vowel bar), `{214}` = 〜, `{207}` = 。** — these are
   game-font glyphs. In English you'd normally drop `{204}` (it's only in
   katakana names like マ{204}ク = Mark). Keep `{214}` as ~ where it reads as
   a drawn-out vowel ("あ{214}ん" → "Ah~").
4. **No length limit.** Write natural English. The insertion tool relocates
   strings, so length is not a constraint — BUT prefer concise, punchy
   dialogue (it's a game script, not a novel).
5. **Speaker names appear inline** as `名前:` at string start. Translate the
   name and keep the colon format. Use these (matching the reference file):
   - ゆきの → Yukino, アヤセ → Ayase, マ{204}ク → Mark, ブラウン → Brown,
     南{204}(南条) → Nanjo, エリ{204} → Elly, たまき → Tamaki, 園村/マキ → Maki,
     大石 → Oishi, 反谷 → Sori, 教顧/光生 → (teacher, context)
   - Keep demon/character names consistent with ALREADY_TRANSLATED_reference.json.
6. **Tone:** 1990s Atlus urban dark fantasy. Demons speak in varied registers:
   some in katakana-baby-talk (keep it dumb/cute: "オレサマ" → "ME, THE GREAT..."),
   old demons in archaic speech ("~じゃよ" → "I daresay..."), punks rough
   ("おめぇ" → "ya"). Match register to the Japanese.
7. **Do not add quotes around dialogue.** Do not add speaker names that
   aren't in the source. Translate only what's there.
8. **If a string is pure symbols or untranslatable** (e.g. just "………"),
   reproduce it as "..." — this is the ONLY permitted use of ellipsis.
9. Japanese ` | ` and `『 』` are quotes/brackets: ｜雪の女王』 → "Snow Queen".
10. Output the COMPLETE JSON files with all entries, same schema, plus
    `translation_en` filled in. Preserve `id` and `offset` fields unchanged.

## Context

The game: students of St. Hermelin High (エルミン学園) in Mikage-cho (御影町)
play the "Persona" game, summon Personas, and face SEBEC (セベク) corp's
DEVA System and the Snow Queen (雪の女王). Characters named above. Place:
Satomi Tadashi pharmacy (サトミ), Joy Street (ジョイ街), Peace Diner, SEBEC,
Mikage hospital. When unsure of a name, transliterate and stay consistent.

Translate E0.json, E1.json, E2.json, E3.json, ADV.json, S2D.json — all six,
fully.
