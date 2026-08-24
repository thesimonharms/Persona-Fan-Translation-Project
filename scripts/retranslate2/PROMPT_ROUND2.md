# Task: Translate NEWLY FOUND Megami Ibunroku Persona strings (round 2)

Same rules as before (`scripts/retranslate/PROMPT.md` applies in full):
- Every string gets a real `translation_en`. No "..." filler.
- Preserve `<LINE>`, `<PAGE>`, `<CLOSE>`, `<END>`, `<CHOICE>`, `[xx]` tags exactly.
- `{2xx}` are font glyphs ({204}=ー). Drop {204} in English names.
- Speaker name glossary and tone guide from the previous prompt apply.
- These strings were missed by the previous extraction pass — they include
  dialogue from the game's opening (classroom rumor scene), hospital intro,
  and various NPC exchanges.

Input files (JSON) in this directory:
- `E0.json` — 3,546 strings
- `E1.json` — 1,703 strings
- `E2.json` — 2,461 strings
- `E3.json` —   797 strings

Output: same files with `translation_en` filled for every entry.
