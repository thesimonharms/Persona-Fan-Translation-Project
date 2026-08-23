# Megami Ibunroku Persona - Localization & Translation Guide

This document establishes the official localization style, character voice profiles, terminology glossary, and formatting rules for the faithful English fan translation of *Megami Ibunroku Persona* (PSX).

---

## 🎯 Core Localization Philosophy

1. **Faithful & Uncensored:**
   - Retain the authentic Japanese setting (Mikage-cho, St. Hermelin High School, Yen, Japanese honorifics where natural, cultural nuances).
   - Restore all cut content, including the full **Snow Queen Quest (雪の女王編)** and uncut demon dialogues.
   - Strictly reverse all 1996 Americanizations (no "Mark is black", no "Lunarvale", no "Mary", no "Nate").

2. **Modern MegaTen Lore Consistency:**
   - Align skill names, demon names, and spell affinities with modern *Shin Megami Tensei* and *Persona* standards (e.g., *Agi / Maragi / Agidyne*, *Bufu / Mabufu / Bufudyne*, *Dia / Mediarahan*, *Megidolaon*, etc.).

3. **Nuanced Character Voices:**
   - Each party member, NPC, and demon archetype has a distinct, consistent register and vernacular.

---

## 🎭 Character Voice Guidelines

### Main Party Cast

| Character | Japanese Name | Voice Profile & Personality |
|---|---|---|
| **Protagonist** | 主人公 / なまえ | Quiet, observant, thoughtful. Dialogue choices range from calm and rational to deadpan or supportive. |
| **Maki Sonomura** | 園村 麻希 (マキ) | Gentle, introspective, artistic, fragile yet resilient. Longs for normalcy and connection due to long hospitalization. |
| **Masao "Mark" Inaba** | 稲葉 正男 (マーク) | Boisterous, expressive, fiercely loyal, graffiti artist. Speaks casually, loudly, occasionally clumsy, with big heart and quick temper. |
| **Kei Nanjo** | 南条 圭 (ナンジョウ) | Heir to the Nanjo Zaibatsu. Highly disciplined, formal, proud, sharp-tongued, constantly quotes family motto: *"I must always be Number One."* |
| **Hidehiko "Brown" Todoroki** | 轟 秀彦 (ブラウン) | High school class clown. Insecure underneath jokes, desperate for female attention and approval, speaks with slang, boasts often. |
| **Eriko "Elly" Kirishima** | 桐島 英理子 (エリー) | Refined, cosmopolitan, wealthy exchange student with keen interest in the occult. Polite, elegant, speaks clear, educated English. |
| **Yuka Ayase** | 綾瀬 優香 (アヤセ) | Classic 90s Kogal (Gyaru). Speaks in bubbly, teasing, trendy teenage slang. Self-absorbed on the surface, remarkably perceptive underneath. |
| **Yukino Mayuzumi** | 黛 雪野 (ユキノ) | Former Sukeban (delinquent girl leader). Protective big-sister figure to the group. Direct, gritty, practical, speaks with grounded strength. |
| **Reiji Kido** | 城戸 玲司 (レイジ) | Grim lone wolf. Terse, intense, brooding. Carries a deep burning vendetta against Kandori. Speaks in short, sharp, cynical sentences. |

---

## 👹 Demon Negotiation Archetypes

The 29 demon conversation files in `/TALK/` each represent a distinct psychological archetype:

| Script File | Archetype | Tone & Localization Style |
|---|---|---|
| `SINSI.BIN` | **Gentleman (紳士)** | Aristocratic, polite, condescending, eloquent, speaks in high-society English. |
| `YAKUZA.BIN` | **Yakuza (極道)** | Gritty underworld slang, prideful, easily provoked, values honor and respect. |
| `YOUEN.BIN` | **Femme Fatale / Seductress (妖艶)** | Sultry, teasing, calculating, seductive, speaks with velvety allure. |
| `TENSI.BIN` / `WTENSI.BIN` | **Angel (天使)** | Pious, righteous, archaic, speaks with divine authority and moral judgment. |
| `KOUMAN.BIN` | **Arrogant / Noble (高慢)** | Haughty, vain, looks down upon human filth with utter disdain. |
| `KOROU.BIN` | **Old Sage (古老)** | Rambling, wise, nostalgic, speaks like an ancient hermit or elder. |
| `SYOUJO.BIN` | **Young Girl (少女)** | Cheerful, innocent on the surface, mercurial, casually cruel or playful. |
| `GAKI.BIN` | **Greedy Brat (餓鬼)** | Gluttonous, whiny, begs for items and snacks, impulsive. |
| `KEMONO.BIN` / `WORM.BIN` | **Beast / Wild (野獣)** | Primal, instinctual, broken syntax, guttural grunts and animalistic logic. |
| `KYOUKI.BIN` | **Maniac / Madman (狂気)** | Unhinged, erratic punctuation, sudden shouting, psychotic ramblings. |
| `TINPRA.BIN` | **Punk / Delinquent (チンピラ)** | Street punk slang, impatient, aggressive, easily intimidated by strength. |
| `KUTISAKE.BIN` | **Urban Legend (口裂け女)** | Creepy, obsessed with beauty and scissors (*"Am I pretty...?"*). |
| `DOPPEL.BIN` | **Doppelganger (生霊)** | Eerie, existential, mimicking, unsettled identity. |

---

## 📐 Text Formatting & Control Codes

- **`<LINE>`**: Line break within the active text box.
- **`<PAGE>`**: Clears the text box and prompts the player to press a button to continue.
- **`<CHOICE id=N>`**: Decision branch or player input prompt.
- **`<CLOSE>`**: Closes the dialog box immediately.
- **Line Length Limits**:
  - Maximum ~32 characters per line (8px half-width equivalent) or ~16 characters (16px full-width).
  - Maximum 3 lines per window before inserting `<PAGE>`.
