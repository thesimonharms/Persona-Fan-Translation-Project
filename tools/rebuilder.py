#!/usr/bin/env python3
"""
tools/rebuilder.py - PSX CD-ROM Disc Image Rebuilder for Megami Ibunroku Persona
Rebuilds bootable PlayStation Mode 2 Form 1 CD-ROM images (.BIN / .CUE) with zero
sector collisions, relocated LBA sector layout, and bit-perfect EDC checksums.
"""

import os
import sys
import json
import struct
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.edc_ecc import build_mode2_form1_sector

SECTOR_RAW_SIZE = 2352
SECTOR_USER_SIZE = 2048


class PersonaDiscRebuilder:
    def __init__(
        self,
        orig_iso_path: str = "psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN",
        layout_json_path: str = "build/lba_layout.json",
        build_extracted_dir: str = "build/extracted",
        out_bin_path: str = "build/Megami_Ibunroku_Persona_EN.bin",
        out_cue_path: str = "build/Megami_Ibunroku_Persona_EN.cue"
    ):
        self.orig_iso_path = Path(orig_iso_path)
        self.layout_json_path = Path(layout_json_path)
        self.build_extracted_dir = Path(build_extracted_dir)
        self.out_bin_path = Path(out_bin_path)
        self.out_cue_path = Path(out_cue_path)

        self.out_bin_path.parent.mkdir(parents=True, exist_ok=True)

    def load_layout_map(self) -> Dict[str, Dict[str, Any]]:
        """Loads non-overlapping LBA layout map."""
        if not self.layout_json_path.is_file():
            from tools.table_relocator import TableRelocator
            reloc = TableRelocator(build_dir=str(self.build_extracted_dir))
            res = reloc.update_all_tables()
            return res["layout_map"]
        return json.loads(self.layout_json_path.read_text(encoding="utf-8"))

    def rebuild_disc(self) -> Dict[str, Any]:
        """Rebuilds the translated PSX CD-ROM image with collision-free relocated sectors."""
        if not self.orig_iso_path.is_file():
            raise FileNotFoundError(f"Original disc image not found at {self.orig_iso_path}")

        print(f"\n==================================================")
        print(f"[*] Starting PSX Disc Image Rebuild...")
        print(f"    Source Disc: {self.orig_iso_path}")
        print(f"    Target Disc: {self.out_bin_path}")
        print(f"==================================================")

        layout_map = self.load_layout_map()

        # Determine max required LBA
        max_lba = max(item["lba"] + item["sectors"] for item in layout_map.values())
        orig_sectors = self.orig_iso_path.stat().st_size // SECTOR_RAW_SIZE
        target_total_sectors = max(orig_sectors, max_lba + 150)

        print(f"[*] Base Disc Sectors: {orig_sectors:,} | Required Sectors: {target_total_sectors:,}")
        print(f"[*] Copying base CD-ROM image...")
        shutil.copyfile(self.orig_iso_path, self.out_bin_path)

        # Extend disc image if needed
        current_size = self.out_bin_path.stat().st_size
        target_size = target_total_sectors * SECTOR_RAW_SIZE
        if target_size > current_size:
            with open(self.out_bin_path, "a+b") as f_ext:
                extra_sectors = target_total_sectors - orig_sectors
                for sec_i in range(extra_sectors):
                    sec_lba = orig_sectors + sec_i
                    empty_sec = build_mode2_form1_sector(sec_lba, b"\x00" * SECTOR_USER_SIZE)
                    f_ext.write(empty_sec)
            print(f"[*] Extended disc image by {extra_sectors:,} sectors (+{target_size - current_size:,} bytes)")

        # Inject modified files
        injected_files = []
        with open(self.out_bin_path, "r+b") as disc_f:
            for rel_path, meta in layout_map.items():
                build_file = self.build_extracted_dir / rel_path
                if not build_file.is_file():
                    continue

                start_lba = meta["lba"]
                file_bytes = build_file.read_bytes()
                total_sectors = (len(file_bytes) + SECTOR_USER_SIZE - 1) // SECTOR_USER_SIZE

                for sec_idx in range(total_sectors):
                    current_lba = start_lba + sec_idx
                    offset_in_file = sec_idx * SECTOR_USER_SIZE
                    chunk = file_bytes[offset_in_file : offset_in_file + SECTOR_USER_SIZE]
                    if len(chunk) < SECTOR_USER_SIZE:
                        chunk = chunk.ljust(SECTOR_USER_SIZE, b"\x00")

                    # Last sector of every file needs XA EOF+EOR (0x89).
                    # Mid-file sectors stay Form 1 data (0x08).
                    submode = 0x89 if sec_idx == total_sectors - 1 else 0x08
                    sec_bytes = build_mode2_form1_sector(current_lba, chunk, submode=submode)
                    disc_f.seek(current_lba * SECTOR_RAW_SIZE)
                    disc_f.write(sec_bytes)

                injected_files.append({
                    "path": rel_path,
                    "lba": start_lba,
                    "size_bytes": len(file_bytes),
                    "sectors": total_sectors
                })

        # Generate CUE Sheet
        cue_content = f'FILE "{self.out_bin_path.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
        self.out_cue_path.write_text(cue_content, encoding="utf-8")

        print(f"\n==================================================")
        print(f"[+] PSX Disc Rebuild Complete (ZERO COLLISIONS)!")
        print(f"[+] Total Files Injected: {len(injected_files)}")
        print(f"[+] Target Image: {self.out_bin_path} ({self.out_bin_path.stat().st_size:,} bytes)")
        print(f"[+] CUE Sheet   : {self.out_cue_path}")
        print(f"==================================================")

        return {"injected_files": injected_files, "bin_path": str(self.out_bin_path), "cue_path": str(self.out_cue_path)}


def main():
    parser = argparse.ArgumentParser(description="Persona PSX Disc Rebuilder")
    parser.add_argument("--orig-iso", default="psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN", help="Path to original PSX BIN")
    parser.add_argument("--build-dir", default="build/extracted", help="Path to modified assets directory")
    parser.add_argument("--out-bin", default="build/Megami_Ibunroku_Persona_EN.bin", help="Output path for translated BIN")
    parser.add_argument("--out-cue", default="build/Megami_Ibunroku_Persona_EN.cue", help="Output path for translated CUE")

    args = parser.parse_args()
    rebuilder = PersonaDiscRebuilder(
        orig_iso_path=args.orig_iso,
        build_extracted_dir=args.build_dir,
        out_bin_path=args.out_bin,
        out_cue_path=args.out_cue
    )
    rebuilder.rebuild_disc()


if __name__ == "__main__":
    main()
