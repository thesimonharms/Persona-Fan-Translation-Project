# Persona Fan Translation Project - Master TODO

A roadmap and task tracking list for the 100% agentic translation pipeline for *Megami Ibunroku Persona* (PSX) and subsequent Persona titles.

---

## 🎯 Target 1: Megami Ibunroku Persona (PSX)

### 📦 Phase 1: Disc & Asset Extraction
- [x] **1.1. Disc Extractor (`tools/extractor.py`)**
  - [x] Implement ISO9660 Mode 2 / 2352 raw sector reader and directory tree walker.
  - [x] Extract all game files preserving directory hierarchy into `extracted/`.
  - [x] Parse and validate engine fast-lookup tables (`FNAME.DAT`, `FSECT.DAT`, `FSIZE.DAT`).
  - [x] Generate extraction manifest with LBA offsets, sector ranges, and file sizes (`extracted/manifest.json`).
- [x] **1.2. Asset Identification & Classification**
  - [x] Map all script files across `/TALK/` (demon negotiation), `/D00/`..`/D04/` (dungeons/events), and `NAME.BIN` (names/items).
  - [x] Document all file formats and compression types.

---

### 🔤 Phase 2: Font & Character Mapping System
- [x] **2.1. Font Table Dumper (`tools/font_tool.py`)**
  - [x] Extract and decode 2,048 16x16 1-bpp glyph bitmaps from `FONT.BIN`.
  - [x] Generate comprehensive 2-byte Gojūon/Kanji table mapping file (`docs/tbl/persona_jp.tbl` and JSON).
  - [x] Create font previewer/renderer script (render glyphs to ASCII/bitmap).
- [x] **2.2. Font Expansion & Lowercase ASCII Support**
  - [x] Design crisp 16x16 font glyphs for English lowercase letters `a`..`z`.
  - [x] Implement font table patcher for ASCII and special characters (`tools/font_tool.py --patch-lowercase`).
  - [ ] Reverse-engineer MIPS R3000 font rendering routine in `SLPS_005.00` for Variable Width Font (VWF) support.

---

### 📜 Phase 3: Script & Bytecode Decompilation
- [x] **3.1. Script Parser & Decompiler (`tools/script_parser.py` & `tools/event_parser.py`)**
  - [x] Disassemble dialogue, control codes (`<PAGE>`, `<LINE>`, `<NAME>`, `<COLOR>`, `<CHOICE>`), and pointer tables.
  - [x] Parse Demon Negotiation scripts (`TALK/*.BIN` - 13,279 strings across 29 files).
  - [x] Parse Story & Adventure cutscene scripts (`ADV/MES.BIN`, `ADV/BST.BIN`, `ADV.BIN`, `ADV/E0..E3.BIN` - 1,760 strings).
  - [x] Parse Battle System & Combat dialogues (`BTLP.BIN` - 1,108 strings).
  - [x] Parse Dungeon Event & School NPC dialogues (`D00.BIN`..`D24.BIN` - 2,337 strings across 35 files).
  - [x] Parse System & Minigame dialogues (`CASINO.BIN`, `OPEN.BIN`, `S2D.BIN` - 122 strings).
  - [x] Export all scripts to structured JSON files in `scripts/original/`.

---

### 🤖 Phase 4: Agentic Translation Engine (Gemini / agy)
- [x] **4.1. Translation Prompts & Lore Glossaries**
  - [x] Create character voice style guides (`docs/translation_guide.md`).
  - [x] Build Megaten standardized glossary (`docs/lore_glossary.json`).
  - [x] Define cultural restoration rules (uncut Snow Queen Quest, Mikage-cho, Japanese cultural references).
- [x] **4.2. In-Session Batch Translation Pipeline (`tools/translate_pipeline.py`)**
  - [x] Implement scene-aware batch translation preserving formatting and markup tags.
  - [x] Automated pixel-width and character length calculation to prevent text box overflows (`TranslationValidator`).
  - [x] Translate all 29 Demon Negotiation files (13,279 strings).
  - [x] Translate all Story Cutscene files (1,760 strings).
  - [x] Translate all Battle System & Combat Quote files (1,108 strings).
  - [x] Translate all 35 Dungeon Event & School NPC files (2,337 strings).
  - [x] Translate all System Menus & Minigame files (122 strings).
  - [x] **100.00% Game Script Translation Completed** in `scripts/translated/`.

---

### 🔄 Phase 5: Recompiler & Dynamic Pointer Relocation
- [x] **5.1. Script Recompiler (`tools/recompiler.py`)**
  - [x] Re-encode translated English strings into game bytecode and control codes.
  - [x] Recalculate all internal relative and absolute pointer offsets.
  - [x] Rebuild container binaries (`TALK/*.BIN`) with dynamic section shifting.
  - [x] 100% lossless string round-trip verification across all 29 negotiation binaries.
  - [x] Recompile all Battle, Story, Event Cutscenes, Dungeon, System, and Font assets into `build/extracted/`.
- [x] **5.2. File System Table Relocator (`tools/table_relocator.py`)**
  - [x] Update `FSECT.DAT` and `FSIZE.DAT` lookup tables for all expanded files (+1,302 sectors).
  - [x] Assign zero-collision continuous relocation LBA range (`297,344+`).

---

### 💿 Phase 6: Disc Rebuilding & Patch Generation
- [x] **6.1. PSX ISO Rebuilder (`tools/rebuilder.py` & `tools/edc_ecc.py`)**
  - [x] Build 2352-byte Mode 2 Form 1 CD-ROM sectors with bit-perfect EDC and sector headers.
  - [x] Rebuild translated bootable PlayStation image (`build/Megami_Ibunroku_Persona_EN.bin`).
  - [x] Generate matching CUE sheet (`build/Megami_Ibunroku_Persona_EN.cue`).
- [x] **6.2. Patch Generator (`tools/patch_maker.py`)**
  - [x] Generate compressed binary delta patch (`build/Megami_Ibunroku_Persona_EN.patch`).
  - [x] Verify patch application with 100% bit-perfect SHA-256 validation.

---

### 🧪 Phase 7: Automated QA & Emulator Smoke Testing
- [x] **7.1. Emulator Integration (`tools/qa_runner.py`)**
  - [x] Setup headless PSX emulator runner (RetroArch / SwanStation / PCSX-ReARMed).
  - [x] Automated boot test, zero crash detection, and video frame capture.
- [x] **7.2. Automated Text Box & Overflow Verification**
  - [x] Automated OCR analysis and disc sector integrity validation.
  - [x] Generate comprehensive QA report (`build/qa_report/QA_REPORT.md`).

---

## 🎮 Future Targets
- [ ] Persona 2: Innocent Sin (*ペルソナ2 罪*) (PSX)
- [ ] Persona 2: Eternal Punishment (*ペルソナ2 罰*) (PSX)
- [ ] Sumaru TV Special Disc (*スマルTVスペシャルディスク*) (PSX)
