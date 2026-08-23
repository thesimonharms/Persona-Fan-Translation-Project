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
- [ ] **2.2. Font Expansion & VWF Support**
  - [ ] Design ASCII/half-width 8x16 font glyphs for English text.
  - [ ] Implement font table patcher for single-byte/half-width Latin characters.
  - [ ] Reverse-engineer MIPS R3000 font rendering routine in `SLPS_005.00` for Variable Width Font (VWF) support.

---

### 📜 Phase 3: Script & Bytecode Decompilation
- [x] **3.1. Script Parser & Decompiler (`tools/script_parser.py`)**
  - [x] Disassemble dialogue, control codes (`<PAGE>`, `<LINE>`, `<NAME>`, `<COLOR>`, `<CHOICE>`), and pointer tables.
  - [x] Parse Demon Negotiation scripts (`TALK/*.BIN` - 13,279 strings across 29 files).
  - [ ] Parse Story & Dungeon Event scripts (`D*/*S.BIN` / `*M.BIN`).
  - [ ] Parse Name/Item/Spell databases (`NAME.BIN`, `NAMEDT.BIN`).
  - [x] Export scripts to structured JSON files in `scripts/original/talk/`.
- [ ] **3.2. Context & Scene Graph Extractor**
  - [ ] Link dialogue lines with speaker IDs, scene metadata, and branching choices.

---

### 🤖 Phase 4: Agentic Translation Engine (Gemini / agy)
- [x] **4.1. Translation Prompts & Lore Glossaries**
  - [x] Create character voice style guides (`docs/translation_guide.md`).
  - [x] Build Megaten standardized glossary (`docs/lore_glossary.json`).
  - [x] Define cultural restoration rules (uncut Snow Queen Quest, Mikage-cho, Japanese cultural references).
- [x] **4.2. In-Session Batch Translation Pipeline (`tools/translate_pipeline.py`)**
  - [x] Implement scene-aware batch translation preserving formatting and markup tags.
  - [x] Automated pixel-width and character length calculation to prevent text box overflows (`TranslationValidator`).
  - [x] Translate first full demon conversation file (`scripts/translated/talk/GAKI.json` - 231 lines).
  - [ ] Complete remaining TALK and Event script files.

---

### 🔄 Phase 5: Recompiler & Dynamic Pointer Relocation
- [ ] **5.1. Script Recompiler (`tools/recompiler.py`)**
  - [ ] Re-encode translated English strings into game bytecode and control codes.
  - [ ] Recalculate all internal relative and absolute pointer offsets.
  - [ ] Rebuild container binaries (`TALK/*.BIN`, `D*/*.BIN`, `NAME.BIN`).
- [ ] **5.2. File System Table Relocator**
  - [ ] Update `FSECT.DAT` and `FSIZE.DAT` lookup tables for expanded files.
  - [ ] Update ISO9660 directory records and LBA sector pointers.

---

### 💿 Phase 6: Disc Rebuilding & Patch Generation
- [ ] **6.1. PSX ISO Rebuilder (`tools/rebuilder.py`)**
  - [ ] Repack files into Mode 2 Form 1 CD-ROM image.
  - [ ] Recompute EDC (Error Detection Code) and L-EC/ECC (Error Correction Code) per sector.
  - [ ] Generate valid bootable `.BIN` / `.CUE`.
- [ ] **6.2. Patch Generator**
  - [ ] Produce `.xdelta` and `.bps` distribution patches comparing original vs translated disc.

---

### 🧪 Phase 7: Automated QA & Emulator Smoke Testing
- [ ] **7.1. Emulator Integration**
  - [ ] Setup headless PSX emulator runner (DuckStation / Mednafen / PCSX-Redux).
  - [ ] Script automated boot test, intro sequence verification, and dialogue frame capture.
- [ ] **7.2. Automated Text Box & Overflow Verification**
  - [ ] Verify no text wraps off-screen or clips through UI boundaries.

---

## 🎮 Future Targets
- [ ] Persona 2: Innocent Sin (*ペルソナ2 罪*) (PSX)
- [ ] Persona 2: Eternal Punishment (*ペルソナ2 罰*) (PSX)
- [ ] Sumaru TV Special Disc (*スマルTVスペシャルディスク*) (PSX)
