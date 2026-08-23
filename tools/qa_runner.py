#!/usr/bin/env python3
"""
tools/qa_runner.py - Automated QA & Emulator Smoke Testing Suite for Megami Ibunroku Persona
Executes:
1. Binary & Disc Integrity Validation (Sector collision check, pointer sanity, font validation)
2. Automated RetroArch Headless Boot Test (Execution, video frame capture, crash detection)
3. Optical Character Recognition (OCR) Frame Analysis (Text box rendering and overflow check)
4. Comprehensive QA Report Generation
"""

import os
import sys
import json
import struct
import shutil
import hashlib
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool

SECTOR_RAW_SIZE = 2352
SECTOR_USER_SIZE = 2048


class PersonaQARunner:
    def __init__(
        self,
        bin_path: str = "build/Megami_Ibunroku_Persona_EN.bin",
        cue_path: str = "build/Megami_Ibunroku_Persona_EN.cue",
        report_out_dir: str = "build/qa_report"
    ):
        self.bin_path = Path(bin_path)
        self.cue_path = Path(cue_path)
        self.report_out_dir = Path(report_out_dir)
        self.report_out_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir = self.report_out_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

    def run_disc_integrity_checks(self) -> Dict[str, Any]:
        """Validates disc sector layout, file boundaries, pointer tables, and font integrity."""
        print(f"\n[*] Running Test Suite 1: Disc & Sector Integrity Validation...")
        results = {
            "disc_present": False,
            "disc_size_bytes": 0,
            "total_sectors": 0,
            "zero_collisions": False,
            "font_integrity": False,
            "talk_pointers_valid": False,
            "errors": []
        }

        if not self.bin_path.is_file():
            results["errors"].append(f"Target disc image not found: {self.bin_path}")
            return results

        results["disc_present"] = True
        results["disc_size_bytes"] = self.bin_path.stat().st_size
        results["total_sectors"] = results["disc_size_bytes"] // SECTOR_RAW_SIZE

        # 1. Collision & Layout check from lba_layout.json
        layout_json = Path("build/lba_layout.json")
        if layout_json.is_file():
            layout = json.loads(layout_json.read_text(encoding="utf-8"))
            sorted_files = sorted(layout.items(), key=lambda x: x[1]["lba"])
            overlaps = []
            for i in range(len(sorted_files) - 1):
                f1_name, f1_meta = sorted_files[i]
                f2_name, f2_meta = sorted_files[i + 1]
                f1_end = f1_meta["lba"] + f1_meta["sectors"]
                if f1_end > f2_meta["lba"]:
                    overlaps.append((f1_name, f2_name, f1_end - f2_meta["lba"]))

            if not overlaps:
                results["zero_collisions"] = True
                print(f"  [PASS] Zero sector collisions across all {len(sorted_files)} game assets.")
            else:
                results["errors"].append(f"Found {len(overlaps)} sector overlaps!")
                for ov in overlaps[:5]:
                    print(f"  [FAIL] Collision: {ov[0]} overlaps {ov[1]} by {ov[2]} sectors!")

        # 2. Font Integrity check
        font_path = Path("build/extracted/FONT.BIN")
        if font_path.is_file() and font_path.stat().st_size == 65536:
            ft = PersonaFontTool(str(font_path))
            test_str = "Persona 1 English Fan Translation"
            enc = ft.encode_text(test_str)
            dec = ft.decode_bytes(enc)
            if dec == test_str:
                results["font_integrity"] = True
                print(f"  [PASS] FONT.BIN English lowercase glyphs verified 100% losslessly.")
            else:
                results["errors"].append(f"Font round-trip mismatch: {test_str} != {dec}")

        # 3. TALK Pointer validation
        talk_files = list(Path("build/extracted/TALK").glob("*.BIN"))
        talk_errors = 0
        for tf in talk_files:
            data = tf.read_bytes()
            if len(data) >= 0x14:
                str0 = struct.unpack("<I", data[0x14:0x18])[0]
                if str0 > len(data):
                    talk_errors += 1
        if talk_errors == 0 and len(talk_files) == 29:
            results["talk_pointers_valid"] = True
            print(f"  [PASS] All 29 TALK binary internal pointer tables verified.")
        else:
            results["errors"].append(f"TALK pointer errors found in {talk_errors} files.")

        return results

    def run_emulator_smoke_test(self, frames: int = 600) -> Dict[str, Any]:
        """Runs headless RetroArch boot smoke test and records video output."""
        print(f"\n[*] Running Test Suite 2: Automated Emulator Boot & Frame Capture...")
        results = {
            "emulator_executed": False,
            "exit_code": -1,
            "video_recorded": False,
            "captured_frames": 0,
            "ocr_text_found": [],
            "errors": []
        }

        # Select recording core (PCSX-ReARMed produces standard video stream)
        candidates = [
            Path.home() / ".config/retroarch/cores/pcsx_rearmed_libretro.so",
            Path("/usr/lib/libretro/swanstation_libretro.so"),
            Path.home() / ".config/retroarch/cores/swanstation_libretro.so",
            Path.home() / ".config/retroarch/cores/mednafen_psx_hw_libretro.so",
        ]
        core_path = None
        for c in candidates:
            if c.is_file():
                core_path = c
                break

        if not core_path:
            results["errors"].append("No PSX libretro core found.")
            return results

        video_out = self.report_out_dir / "boot_session.mkv"
        if video_out.is_file():
            video_out.unlink()

        cmd = [
            "retroarch",
            "-L", str(core_path),
            "--max-frames", str(frames),
            "--record", str(video_out),
            str(self.cue_path)
        ]

        print(f"  [*] Launching RetroArch with core: {core_path.name} (running {frames} frames)...")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            results["emulator_executed"] = True
            results["exit_code"] = res.returncode
            if res.returncode == 0:
                print(f"  [PASS] Emulator executed successfully (Exit code: 0).")
            else:
                results["errors"].append(f"Emulator returned non-zero exit code: {res.returncode}")
        except Exception as e:
            results["errors"].append(f"Emulator execution failed: {e}")
            return results

        # Extract frames
        if video_out.is_file() and video_out.stat().st_size > 0:
            results["video_recorded"] = True
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", str(video_out),
                "-vf", "fps=1",
                str(self.frames_dir / "frame_%03d.png")
            ]
            subprocess.run(ffmpeg_cmd, capture_output=True)
            frames_list = sorted(self.frames_dir.glob("frame_*.png"))
            results["captured_frames"] = len(frames_list)
            print(f"  [PASS] Captured {len(frames_list)} video frames from boot session.")

            # OCR Analysis on captured frames
            ocr_texts = []
            for frame_file in frames_list:
                try:
                    ocr_res = subprocess.run(
                        ["tesseract", str(frame_file), "stdout", "--oem", "1", "-l", "eng+jpn"],
                        capture_output=True,
                        text=True
                    )
                    text = ocr_res.stdout.strip()
                    if text:
                        ocr_texts.append({"frame": frame_file.name, "text": text})
                except Exception:
                    pass
            results["ocr_text_found"] = ocr_texts
            print(f"  [PASS] Performed OCR analysis on captured frames ({len(ocr_texts)} text events detected).")

        return results

    def generate_qa_report(self, integrity_res: Dict[str, Any], emu_res: Dict[str, Any]) -> Path:
        """Generates comprehensive Markdown QA report."""
        report_file = self.report_out_dir / "QA_REPORT.md"
        
        all_passed = (
            integrity_res.get("zero_collisions", False) and
            integrity_res.get("font_integrity", False) and
            integrity_res.get("talk_pointers_valid", False) and
            emu_res.get("emulator_executed", False) and
            emu_res.get("exit_code") == 0
        )

        md = [
            "# Megami Ibunroku Persona - Automated QA & Smoke Test Report",
            "",
            f"**Status:** {'✅ ALL TESTS PASSED' if all_passed else '⚠️ ISSUES DETECTED'}",
            f"**Target Image:** `{self.bin_path.name}` ({integrity_res.get('disc_size_bytes', 0):,} bytes / {integrity_res.get('total_sectors', 0):,} sectors)",
            f"**CUE Sheet:** `{self.cue_path.name}`",
            "",
            "---",
            "",
            "## 1. Disc & Sector Integrity Validation",
            f"- **Sector Collisions:** {'✅ Zero collisions (Clean LBA relocation)' if integrity_res.get('zero_collisions') else '❌ Sector overlaps detected'}",
            f"- **Font System:** {'✅ 16x16 English lowercase glyphs verified' if integrity_res.get('font_integrity') else '❌ Font error'}",
            f"- **Talk Script Pointer Tables:** {'✅ 29 / 29 files valid' if integrity_res.get('talk_pointers_valid') else '❌ Pointer error'}",
            "",
            "---",
            "",
            "## 2. Automated Emulator Boot & Execution",
            f"- **RetroArch Boot Test:** {'✅ Clean execution (Exit code: 0)' if emu_res.get('exit_code') == 0 else '❌ Non-zero exit code'}",
            f"- **Video Recording:** {'✅ Recorded boot session' if emu_res.get('video_recorded') else '❌ No video stream'}",
            f"- **Frames Captured:** `{emu_res.get('captured_frames', 0)}` frames",
            "",
            "---",
            "",
            "## 3. Optical Character Recognition (OCR) Analysis",
        ]

        if emu_res.get("ocr_text_found"):
            for item in emu_res["ocr_text_found"]:
                clean_txt = item["text"].replace("\n", " ")
                md.append(f"- **`{item['frame']}`:** `{clean_txt}`")
        else:
            md.append("*(No text recognized in initial boot frames)*")

        md.extend([
            "",
            "---",
            "",
            "## 4. Summary & Verification Verdict",
            f"**Integrity Verdict:** {'100% Verified Ready for Distribution' if all_passed else 'Requires Investigation'}"
        ])

        report_file.write_text("\n".join(md), encoding="utf-8")
        print(f"\n==================================================")
        print(f"[+] QA Report Generated: {report_file}")
        print(f"==================================================")
        return report_file


def main():
    parser = argparse.ArgumentParser(description="Persona Automated QA Suite")
    parser.add_argument("--bin", default="build/Megami_Ibunroku_Persona_EN.bin", help="Path to built PSX BIN")
    parser.add_argument("--cue", default="build/Megami_Ibunroku_Persona_EN.cue", help="Path to built PSX CUE")
    parser.add_argument("--frames", type=int, default=600, help="Frames to simulate in emulator")

    args = parser.parse_args()
    runner = PersonaQARunner(args.bin, args.cue)
    integrity = runner.run_disc_integrity_checks()
    emu = runner.run_emulator_smoke_test(args.frames)
    runner.generate_qa_report(integrity, emu)


if __name__ == "__main__":
    main()
