#!/usr/bin/env python3
"""
tools/table_relocator.py - PSX File System Relocator & Collision Prevention Engine
Allocates non-overlapping sector layouts on the CD-ROM, updates engine fast-lookup tables
(FSECT.DAT, FSIZE.DAT), and exports relocation mappings.
"""

import os
import sys
import json
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

SECTOR_SIZE = 2048
RELOC_BASE_LBA = 297344  # Safe end-of-disc relocation area


class TableRelocator:
    def __init__(self, extracted_dir: str = "extracted", build_dir: str = "build/extracted"):
        self.extracted_dir = Path(extracted_dir)
        self.build_dir = Path(build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def update_all_tables(self) -> Dict[str, Any]:
        """
        Scans all files, assigns non-overlapping LBAs for expanded files,
        and updates FSIZE.DAT and FSECT.DAT.
        """
        fname_path = self.extracted_dir / "FNAME.DAT"
        fsect_path = self.extracted_dir / "FSECT.DAT"
        fsize_path = self.extracted_dir / "FSIZE.DAT"

        fname_data = fname_path.read_bytes()
        fsect_data = bytearray(fsect_path.read_bytes())
        fsize_data = bytearray(fsize_path.read_bytes())

        raw_names = [n.decode("ascii", errors="ignore") for n in fname_data.split(b"\x00") if n]
        total_entries = len(fsect_data) // 4

        current_reloc_lba = RELOC_BASE_LBA
        layout_map = {}
        changes = []

        for i in range(total_entries):
            norm = raw_names[i].split(";")[0].replace("\\", "/").lstrip("/")
            orig_lba = struct.unpack("<I", fsect_data[i * 4 : (i + 1) * 4])[0]
            orig_sz = struct.unpack("<I", fsize_data[i * 4 : (i + 1) * 4])[0]
            orig_sec = (orig_sz + SECTOR_SIZE - 1) // SECTOR_SIZE

            build_file = self.build_dir / norm
            if build_file.is_file():
                new_sz = build_file.stat().st_size
                new_aligned_sz = ((new_sz + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                new_sec = new_aligned_sz // SECTOR_SIZE
            else:
                new_sz = orig_sz
                new_aligned_sz = orig_sz
                new_sec = orig_sec

            if new_sec > orig_sec:
                # Assign to collision-free relocation zone at end of disc
                assigned_lba = current_reloc_lba
                current_reloc_lba += new_sec
                changes.append({
                    "path": norm,
                    "old_lba": orig_lba,
                    "new_lba": assigned_lba,
                    "old_size": orig_sz,
                    "new_size": new_aligned_sz,
                    "delta_sectors": new_sec - orig_sec,
                    "relocated": True
                })
            else:
                assigned_lba = orig_lba
                if build_file.is_file() and new_aligned_sz != orig_sz:
                    changes.append({
                        "path": norm,
                        "old_lba": orig_lba,
                        "new_lba": assigned_lba,
                        "old_size": orig_sz,
                        "new_size": new_aligned_sz,
                        "delta_sectors": 0,
                        "relocated": False
                    })

            struct.pack_into("<I", fsect_data, i * 4, assigned_lba)
            struct.pack_into("<I", fsize_data, i * 4, new_aligned_sz)
            layout_map[norm] = {
                "lba": assigned_lba,
                "size_bytes": new_aligned_sz,
                "sectors": new_sec
            }

        # Write updated tables to build directory
        (self.build_dir / "FSIZE.DAT").write_bytes(fsize_data)
        (self.build_dir / "FSECT.DAT").write_bytes(fsect_data)
        (self.build_dir / "FNAME.DAT").write_bytes(fname_data)

        # Export layout map
        layout_json_path = Path("build/lba_layout.json")
        layout_json_path.write_text(json.dumps(layout_map, indent=2), encoding="utf-8")

        print(f"\n==================================================")
        print(f"[+] Engine File Lookup Tables Relocated Successfully!")
        print(f"[+] Total Relocated Files: {sum(1 for ch in changes if ch.get('relocated'))}")
        print(f"[+] Relocation Sector Range: LBA {RELOC_BASE_LBA:,} - {current_reloc_lba:,} ({current_reloc_lba - RELOC_BASE_LBA} sectors)")
        print(f"==================================================")
        for ch in changes[:15]:
            print(f"  * {ch['path']:<22}: LBA {ch['old_lba']:6d} -> {ch['new_lba']:6d} | {ch['old_size']:6,d} -> {ch['new_size']:6,d} bytes")
        if len(changes) > 15:
            print(f"  ... and {len(changes) - 15} more files.")

        return {"changes": changes, "layout_map": layout_map}


def main():
    parser = argparse.ArgumentParser(description="Persona Engine Table Relocator")
    parser.add_argument("--extracted-dir", default="extracted", help="Path to original extracted directory")
    parser.add_argument("--build-dir", default="build/extracted", help="Path to build extracted directory")

    args = parser.parse_args()
    relocator = TableRelocator(args.extracted_dir, args.build_dir)
    relocator.update_all_tables()


if __name__ == "__main__":
    main()
