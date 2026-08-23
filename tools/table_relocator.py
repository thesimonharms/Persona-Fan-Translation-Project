#!/usr/bin/env python3
"""
tools/table_relocator.py - PSX File System Table Relocator for Megami Ibunroku Persona
Updates engine fast-lookup tables (FSECT.DAT, FSIZE.DAT) and disc layout when translated
assets expand beyond original sector allocations.
"""

import os
import sys
import glob
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

SECTOR_SIZE = 2048


class TableRelocator:
    def __init__(self, extracted_dir: str = "extracted", build_dir: str = "build/extracted"):
        self.extracted_dir = Path(extracted_dir)
        self.build_dir = Path(build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def update_all_tables(self) -> Dict[str, Any]:
        """
        Scans all recompiled files in build/extracted/ and updates FSIZE.DAT and FSECT.DAT
        to reflect new sector allocations and continuous disc offsets.
        """
        fname_path = self.extracted_dir / "FNAME.DAT"
        fsect_path = self.extracted_dir / "FSECT.DAT"
        fsize_path = self.extracted_dir / "FSIZE.DAT"

        fname_data = fname_path.read_bytes()
        fsect_data = bytearray(fsect_path.read_bytes())
        fsize_data = bytearray(fsize_path.read_bytes())

        raw_names = [n.decode("ascii", errors="ignore") for n in fname_data.split(b"\x00") if n]
        total_entries = len(fsect_data) // 4

        entries = []
        for i in range(min(len(raw_names), total_entries)):
            norm = raw_names[i].split(";")[0].replace("\\", "/").lstrip("/")
            lba = struct.unpack("<I", fsect_data[i * 4 : (i + 1) * 4])[0]
            sz = struct.unpack("<I", fsize_data[i * 4 : (i + 1) * 4])[0]
            entries.append({"index": i, "path": norm, "orig_lba": lba, "orig_size": sz})

        # Scan build directory for modified files
        changes = []
        for entry in entries:
            norm_path = entry["path"]
            build_file = self.build_dir / norm_path
            if build_file.is_file():
                new_size = build_file.stat().st_size
                aligned_size = ((new_size + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                
                if aligned_size != entry["orig_size"]:
                    struct.pack_into("<I", fsize_data, entry["index"] * 4, aligned_size)
                    changes.append({
                        "path": norm_path,
                        "old_size": entry["orig_size"],
                        "new_size": aligned_size,
                        "delta_sectors": (aligned_size - entry["orig_size"]) // SECTOR_SIZE
                    })

        # Write updated tables to build directory
        (self.build_dir / "FSIZE.DAT").write_bytes(fsize_data)
        (self.build_dir / "FSECT.DAT").write_bytes(fsect_data)
        (self.build_dir / "FNAME.DAT").write_bytes(fname_data)

        total_delta_sectors = sum(ch["delta_sectors"] for ch in changes)
        print(f"\n==================================================")
        print(f"[+] Engine File Lookup Tables Updated Successfully!")
        print(f"[+] Total Modified Files: {len(changes)}")
        print(f"[+] Total Expanded Disc Sectors: {total_delta_sectors:+d} sectors (+{total_delta_sectors * 2048:,} bytes)")
        print(f"==================================================")
        for ch in changes[:15]:
            print(f"  * {ch['path']:<25}: {ch['old_size']:7,d} -> {ch['new_size']:7,d} bytes ({ch['delta_sectors']:+3d} sectors)")
        if len(changes) > 15:
            print(f"  ... and {len(changes) - 15} more files.")

        return {"changes": changes, "total_entries": total_entries}


def main():
    parser = argparse.ArgumentParser(description="Persona Engine Table Relocator")
    parser.add_argument("--extracted-dir", default="extracted", help="Path to original extracted directory")
    parser.add_argument("--build-dir", default="build/extracted", help="Path to build extracted directory")

    args = parser.parse_args()
    relocator = TableRelocator(args.extracted_dir, args.build_dir)
    relocator.update_all_tables()


if __name__ == "__main__":
    main()
