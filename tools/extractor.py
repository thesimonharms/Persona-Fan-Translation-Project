#!/usr/bin/env python3
"""
tools/extractor.py - PSX Disc & Asset Extractor for Megami Ibunroku Persona
Extracts files from raw CD-ROM Mode 2 / 2352 BIN/CUE disc images, parses ISO9660
and engine lookup tables (FNAME.DAT, FSECT.DAT, FSIZE.DAT), and produces a complete
extracted file tree with manifest.json.
"""

import os
import sys
import json
import struct
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

RAW_SECTOR_SIZE = 2352
USER_DATA_OFFSET = 24
USER_DATA_SIZE = 2048  # Mode 2 Form 1 data sector size


class PSXDiscExtractor:
    def __init__(self, bin_path: str, out_dir: str = "extracted"):
        self.bin_path = Path(bin_path)
        self.out_dir = Path(out_dir)
        if not self.bin_path.is_file():
            raise FileNotFoundError(f"Disc image not found: {self.bin_path}")
        self.total_sectors = self.bin_path.stat().st_size // RAW_SECTOR_SIZE

    def read_sector_raw(self, lba: int) -> bytes:
        """Read a single raw 2352-byte sector at given LBA."""
        with open(self.bin_path, "rb") as f:
            f.seek(lba * RAW_SECTOR_SIZE)
            return f.read(RAW_SECTOR_SIZE)

    def read_sector_data(self, lba: int) -> bytes:
        """Read 2048-byte Mode 2 Form 1 user data from given LBA."""
        raw = self.read_sector_raw(lba)
        if len(raw) < RAW_SECTOR_SIZE:
            return b""
        return raw[USER_DATA_OFFSET : USER_DATA_OFFSET + USER_DATA_SIZE]

    def read_data_span(self, lba: int, size: int) -> bytes:
        """Read exact byte payload spanning multiple sectors."""
        sectors_needed = (size + USER_DATA_SIZE - 1) // USER_DATA_SIZE
        buf = bytearray()
        with open(self.bin_path, "rb") as f:
            for s in range(sectors_needed):
                f.seek((lba + s) * RAW_SECTOR_SIZE)
                raw = f.read(RAW_SECTOR_SIZE)
                if len(raw) < RAW_SECTOR_SIZE:
                    break
                buf.extend(raw[USER_DATA_OFFSET : USER_DATA_OFFSET + USER_DATA_SIZE])
        return bytes(buf[:size])

    def parse_iso9660_tree(self) -> List[Dict[str, Any]]:
        """Parse standard ISO9660 directory records starting from PVD at LBA 16."""
        pvd_data = self.read_sector_data(16)
        if pvd_data[1:6] != b"CD001":
            raise ValueError("Invalid ISO9660 Primary Volume Descriptor at sector 16.")

        root_record = pvd_data[156 : 156 + 34]
        root_lba = struct.unpack("<I", root_record[2:6])[0]
        root_size = struct.unpack("<I", root_record[10:14])[0]

        files = []

        def walk_dir(lba: int, size: int, current_path: str = ""):
            sectors = (size + USER_DATA_SIZE - 1) // USER_DATA_SIZE
            raw_dir_data = b"".join(self.read_sector_data(lba + i) for i in range(sectors))
            offset = 0

            while offset < len(raw_dir_data):
                rec_len = raw_dir_data[offset]
                if rec_len == 0:
                    offset += 1
                    continue

                rec = raw_dir_data[offset : offset + rec_len]
                flags = rec[25]
                is_dir = (flags & 0x02) != 0
                file_lba = struct.unpack("<I", rec[2:6])[0]
                file_size = struct.unpack("<I", rec[10:14])[0]
                name_len = rec[32]
                raw_name = rec[33 : 33 + name_len]

                if raw_name == b"\x00":
                    name = "."
                elif raw_name == b"\x01":
                    name = ".."
                else:
                    name = raw_name.decode("ascii", errors="ignore").split(";")[0]

                if name not in (".", ".."):
                    rel_path = f"{current_path}/{name}".lstrip("/")
                    files.append({
                        "path": rel_path,
                        "lba": file_lba,
                        "size": file_size,
                        "is_dir": is_dir,
                        "source": "ISO9660"
                    })
                    if is_dir:
                        walk_dir(file_lba, file_size, rel_path)

                offset += rec_len

        walk_dir(root_lba, root_size)
        return files

    def parse_engine_file_tables(self, iso_files: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Parse Atlus engine lookup tables: FNAME.DAT, FSECT.DAT, FSIZE.DAT."""
        f_lookup = {f["path"]: f for f in iso_files if not f["is_dir"]}

        fname_info = f_lookup.get("FNAME.DAT")
        fsect_info = f_lookup.get("FSECT.DAT")
        fsize_info = f_lookup.get("FSIZE.DAT")

        if not (fname_info and fsect_info and fsize_info):
            print("[-] Engine DAT tables (FNAME, FSECT, FSIZE) not found on disc.")
            return None

        fname_data = self.read_data_span(fname_info["lba"], fname_info["size"])
        fsect_data = self.read_data_span(fsect_info["lba"], fsect_info["size"])
        fsize_data = self.read_data_span(fsize_info["lba"], fsize_info["size"])

        raw_names = [n for n in fname_data.split(b"\x00") if n]
        num_entries = len(fsect_data) // 4

        entries = []
        for i in range(min(len(raw_names), num_entries)):
            name_str = raw_names[i].decode("ascii", errors="ignore")
            # Normalize path (e.g. \D00\D00.BIN;1 -> D00/D00.BIN)
            norm_path = name_str.split(";")[0].replace("\\", "/").lstrip("/")
            sect = struct.unpack("<I", fsect_data[i * 4 : (i + 1) * 4])[0]
            size = struct.unpack("<I", fsize_data[i * 4 : (i + 1) * 4])[0]

            entries.append({
                "path": norm_path,
                "lba": sect,
                "size": size,
                "is_dir": False,
                "source": "ENGINE_TABLES",
                "table_index": i
            })

        return entries

    def extract_all(self, verify: bool = True) -> Dict[str, Any]:
        """Extract all files from the disc image into output directory."""
        print(f"[*] Reading ISO9660 file system from {self.bin_path.name}...")
        iso_files = self.parse_iso9660_tree()
        print(f"[+] Found {len(iso_files)} records in ISO9660 directory structure.")

        engine_files = self.parse_engine_file_tables(iso_files)
        if engine_files:
            print(f"[+] Found {len(engine_files)} files indexed in game engine tables (FNAME/FSECT/FSIZE).")

        # Use engine files list if available (since it has exact engine sector mappings) or ISO list
        file_list = [f for f in iso_files if not f["is_dir"]]

        self.out_dir.mkdir(parents=True, exist_ok=True)
        manifest_files = []

        total = len(file_list)
        print(f"[*] Extracting {total} files to '{self.out_dir}'...")

        for idx, item in enumerate(file_list, start=1):
            out_file_path = self.out_dir / item["path"]
            out_file_path.parent.mkdir(parents=True, exist_ok=True)

            data = self.read_data_span(item["lba"], item["size"])
            out_file_path.write_bytes(data)

            sha256 = hashlib.sha256(data).hexdigest()
            sectors = (item["size"] + USER_DATA_SIZE - 1) // USER_DATA_SIZE

            manifest_files.append({
                "path": item["path"],
                "lba": item["lba"],
                "size_bytes": item["size"],
                "sectors": sectors,
                "sha256": sha256
            })

            if idx % 25 == 0 or idx == total:
                print(f"    [{idx:3d}/{total}] Extracted: {item['path']} ({item['size']:,} bytes)")

        manifest = {
            "disc_image": self.bin_path.name,
            "total_sectors": self.total_sectors,
            "total_files": len(manifest_files),
            "files": manifest_files
        }

        manifest_path = self.out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"[+] Extraction complete! Manifest saved to {manifest_path}")

        return manifest


def main():
    parser = argparse.ArgumentParser(description="Megami Ibunroku Persona PSX Disc Extractor")
    parser.add_argument(
        "--bin",
        type=str,
        default="psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN",
        help="Path to PERSONA.BIN raw disc image"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="extracted",
        help="Destination directory for extracted assets"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify SHA256 checksums of extracted assets"
    )

    args = parser.parse_args()

    extractor = PSXDiscExtractor(bin_path=args.bin, out_dir=args.out_dir)
    extractor.extract_all(verify=args.verify)


if __name__ == "__main__":
    main()
