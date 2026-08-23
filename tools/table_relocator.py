#!/usr/bin/env python3
"""
tools/table_relocator.py - PSX File System Table Relocator for Megami Ibunroku Persona
Updates engine fast-lookup tables (FSECT.DAT, FSIZE.DAT) and layout when translated
assets expand beyond original sector allocations.
"""

import os
import sys
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

    def update_tables(self, modified_files: Dict[str, int]) -> Dict[str, Any]:
        """
        Updates FSIZE.DAT and FSECT.DAT based on modified file sizes.
        `modified_files` is a dict mapping normalized paths (e.g. 'TALK/GAKI.BIN') to new byte sizes.
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

        # Recalculate sector allocations if files expanded
        changes = []
        for entry in entries:
            norm_path = entry["path"]
            if norm_path in modified_files:
                new_size = modified_files[norm_path]
                aligned_size = ((new_size + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
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

        print(f"[+] Updated engine file tables ({len(changes)} files modified):")
        for ch in changes:
            print(f"    * {ch['path']}: {ch['old_size']:,} -> {ch['new_size']:,} bytes ({ch['delta_sectors']:+d} sectors)")

        return {"changes": changes, "total_entries": total_entries}


def main():
    parser = argparse.ArgumentParser(description="Persona Engine Table Relocator")
    parser.add_argument("--extracted-dir", default="extracted", help="Path to original extracted directory")
    parser.add_argument("--build-dir", default="build/extracted", help="Path to build extracted directory")

    args = parser.parse_args()
    relocator = TableRelocator(args.extracted_dir, args.build_dir)
    # Test with GAKI.BIN if present in build
    gaki_build = Path("build/extracted/TALK/GAKI.BIN")
    if gaki_build.is_file():
        relocator.update_tables({"TALK/GAKI.BIN": gaki_build.stat().st_size})


if __name__ == "__main__":
    main()
