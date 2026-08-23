#!/usr/bin/env python3
"""
tools/rebuilder.py - PSX CD-ROM Disc Image Rebuilder for Megami Ibunroku Persona
Rebuilds bootable PlayStation Mode 2 Form 1 CD-ROM images (.BIN / .CUE) with valid
sector headers, subheaders, and EDC checksums for all modified game assets.
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
        manifest_path: str = "extracted/manifest.json",
        build_extracted_dir: str = "build/extracted",
        out_bin_path: str = "build/Megami_Ibunroku_Persona_EN.bin",
        out_cue_path: str = "build/Megami_Ibunroku_Persona_EN.cue"
    ):
        self.orig_iso_path = Path(orig_iso_path)
        self.manifest_path = Path(manifest_path)
        self.build_extracted_dir = Path(build_extracted_dir)
        self.out_bin_path = Path(out_bin_path)
        self.out_cue_path = Path(out_cue_path)

        self.out_bin_path.parent.mkdir(parents=True, exist_ok=True)

    def load_file_lba_map(self) -> Dict[str, int]:
        """Loads file -> LBA mapping from extraction manifest and FSECT.DAT."""
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        lba_map = {}
        for f in manifest["files"]:
            lba_map[f["path"]] = f["lba"]

        # Also check build FSECT.DAT if present
        fsect_path = self.build_extracted_dir / "FSECT.DAT"
        fname_path = self.build_extracted_dir / "FNAME.DAT"
        if fsect_path.is_file() and fname_path.is_file():
            fname_data = fname_path.read_bytes()
            fsect_data = fsect_path.read_bytes()
            raw_names = [n.decode("ascii", errors="ignore") for n in fname_data.split(b"\x00") if n]
            for i in range(min(len(raw_names), len(fsect_data) // 4)):
                norm = raw_names[i].split(";")[0].replace("\\", "/").lstrip("/")
                lba = struct.unpack("<I", fsect_data[i * 4 : (i + 1) * 4])[0]
                lba_map[norm] = lba

        return lba_map

    def rebuild_disc(self) -> Dict[str, Any]:
        """Rebuilds the translated PSX CD-ROM image by injecting modified assets."""
        if not self.orig_iso_path.is_file():
            raise FileNotFoundError(f"Original disc image not found at {self.orig_iso_path}")

        print(f"\n==================================================")
        print(f"[*] Starting PSX Disc Image Rebuild...")
        print(f"    Source Disc: {self.orig_iso_path}")
        print(f"    Target Disc: {self.out_bin_path}")
        print(f"==================================================")

        # 1. Initialize target disc from source image
        print(f"[*] Copying base CD-ROM image ({self.orig_iso_path.stat().st_size:,} bytes)...")
        shutil.copyfile(self.orig_iso_path, self.out_bin_path)

        lba_map = self.load_file_lba_map()
        injected_files = []

        # 2. Find all modified files in build/extracted/
        with open(self.out_bin_path, "r+b") as disc_f:
            for build_file in sorted(self.build_extracted_dir.rglob("*")):
                if not build_file.is_file():
                    continue

                rel_path = str(build_file.relative_to(self.build_extracted_dir)).replace("\\", "/")
                
                # Check if this file has an LBA mapping
                if rel_path not in lba_map:
                    print(f"[-] Warning: No LBA mapping found for {rel_path}, skipping.")
                    continue

                start_lba = lba_map[rel_path]
                file_bytes = build_file.read_bytes()
                total_sectors = (len(file_bytes) + SECTOR_USER_SIZE - 1) // SECTOR_USER_SIZE

                # Inject sectors
                for sec_idx in range(total_sectors):
                    current_lba = start_lba + sec_idx
                    offset_in_file = sec_idx * SECTOR_USER_SIZE
                    chunk = file_bytes[offset_in_file : offset_in_file + SECTOR_USER_SIZE]
                    if len(chunk) < SECTOR_USER_SIZE:
                        chunk = chunk.ljust(SECTOR_USER_SIZE, b"\x00")

                    # Construct full 2352-byte sector with EDC
                    sec_bytes = build_mode2_form1_sector(current_lba, chunk)
                    disc_f.seek(current_lba * SECTOR_RAW_SIZE)
                    disc_f.write(sec_bytes)

                injected_files.append({
                    "path": rel_path,
                    "lba": start_lba,
                    "size_bytes": len(file_bytes),
                    "sectors": total_sectors
                })
                print(f"[+] Injected {rel_path:<24}: LBA {start_lba:6d} ({len(file_bytes):7,d} bytes, {total_sectors:3d} sectors)")

        # 3. Create CUE Sheet
        cue_content = f'FILE "{self.out_bin_path.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
        self.out_cue_path.write_text(cue_content, encoding="utf-8")
        print(f"[+] Generated CUE sheet: {self.out_cue_path}")

        print(f"\n==================================================")
        print(f"[+] PSX Disc Rebuild Complete!")
        print(f"[+] Total Files Injected: {len(injected_files)}")
        print(f"[+] Target Image: {self.out_bin_path} ({self.out_bin_path.stat().st_size:,} bytes)")
        print(f"==================================================")

        return {"injected_files": injected_files, "bin_path": str(self.out_bin_path), "cue_path": str(self.out_cue_path)}


def main():
    parser = argparse.ArgumentParser(description="Persona PSX Disc Rebuilder")
    parser.add_argument("--orig-iso", default="psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN", help="Path to original PSX BIN")
    parser.add_argument("--manifest", default="extracted/manifest.json", help="Path to extraction manifest")
    parser.add_argument("--build-dir", default="build/extracted", help="Path to modified assets directory")
    parser.add_argument("--out-bin", default="build/Megami_Ibunroku_Persona_EN.bin", help="Output path for translated BIN")
    parser.add_argument("--out-cue", default="build/Megami_Ibunroku_Persona_EN.cue", help="Output path for translated CUE")

    args = parser.parse_args()
    rebuilder = PersonaDiscRebuilder(
        orig_iso_path=args.orig_iso,
        manifest_path=args.manifest,
        build_extracted_dir=args.build_dir,
        out_bin_path=args.out_bin,
        out_cue_path=args.out_cue
    )
    rebuilder.rebuild_disc()


if __name__ == "__main__":
    main()
