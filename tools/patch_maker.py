#!/usr/bin/env python3
"""
tools/patch_maker.py - Binary Delta Patch Generator for Megami Ibunroku Persona
Creates a high-efficiency binary delta patch between the original Japanese disc
and the translated English disc, and provides patch application and verification tools.
"""

import os
import sys
import zlib
import struct
import shutil
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

CHUNK_SIZE = 64 * 1024


class PersonaPatchMaker:
    def __init__(
        self,
        orig_bin_path: str = "psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN",
        trans_bin_path: str = "build/Megami_Ibunroku_Persona_EN.bin",
        patch_out_path: str = "build/Megami_Ibunroku_Persona_EN.patch"
    ):
        self.orig_bin_path = Path(orig_bin_path)
        self.trans_bin_path = Path(trans_bin_path)
        self.patch_out_path = Path(patch_out_path)
        self.patch_out_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sha256_file(filepath: Path) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()

    def create_patch(self) -> Dict[str, Any]:
        """
        Creates a fast, compressed block delta patch between original and translated images.
        """
        if not self.orig_bin_path.is_file() or not self.trans_bin_path.is_file():
            raise FileNotFoundError("Source or target binary image missing.")

        print(f"\n==================================================")
        print(f"[*] Generating Binary Delta Patch...")
        print(f"    Source (JPN): {self.orig_bin_path}")
        print(f"    Target (EN) : {self.trans_bin_path}")
        print(f"==================================================")

        orig_sha = self.sha256_file(self.orig_bin_path)
        trans_sha = self.sha256_file(self.trans_bin_path)

        orig_size = self.orig_bin_path.stat().st_size
        trans_size = self.trans_bin_path.stat().st_size

        print(f"[*] Source SHA-256: {orig_sha}")
        print(f"[*] Target SHA-256: {trans_sha}")

        diff_blocks = []
        block_size = 2352 * 16  # 16 CD sectors per chunk

        with open(self.orig_bin_path, "rb") as f_orig, open(self.trans_bin_path, "rb") as f_trans:
            offset = 0
            while True:
                chunk_o = f_orig.read(block_size)
                chunk_t = f_trans.read(block_size)
                if not chunk_t:
                    break

                if chunk_o != chunk_t:
                    comp = zlib.compress(chunk_t, level=9)
                    diff_blocks.append({
                        "offset": offset,
                        "raw_len": len(chunk_t),
                        "comp_data": comp
                    })

                offset += len(chunk_t)

        with open(self.patch_out_path, "wb") as f_out:
            f_out.write(b"MIP1")
            f_out.write(bytes.fromhex(orig_sha))
            f_out.write(bytes.fromhex(trans_sha))
            f_out.write(struct.pack("<Q", orig_size))
            f_out.write(struct.pack("<Q", trans_size))
            f_out.write(struct.pack("<I", len(diff_blocks)))

            for blk in diff_blocks:
                f_out.write(struct.pack("<Q", blk["offset"]))
                f_out.write(struct.pack("<I", blk["raw_len"]))
                f_out.write(struct.pack("<I", len(blk["comp_data"])))
                f_out.write(blk["comp_data"])

        patch_size = self.patch_out_path.stat().st_size
        print(f"\n==================================================")
        print(f"[+] Binary Delta Patch Generated Successfully!")
        print(f"[+] Patch File: {self.patch_out_path} ({patch_size:,} bytes)")
        print(f"[+] Modified Blocks Packed: {len(diff_blocks):,} blocks")
        print(f"==================================================")

        return {
            "patch_path": str(self.patch_out_path),
            "patch_size_bytes": patch_size,
            "orig_sha256": orig_sha,
            "trans_sha256": trans_sha,
            "modified_blocks": len(diff_blocks)
        }

    def apply_and_verify_patch(self, test_applied_path: str = "build/test_applied_persona.bin") -> bool:
        """Applies patch to original image and verifies SHA-256 against translated image."""
        applied_path = Path(test_applied_path)
        print(f"\n[*] Verifying patch application integrity...")

        with open(self.patch_out_path, "rb") as pf:
            magic = pf.read(4)
            assert magic == b"MIP1", f"Invalid patch magic: {magic}"
            expected_orig_sha = pf.read(32).hex()
            expected_trans_sha = pf.read(32).hex()
            orig_sz, trans_sz, num_blocks = struct.unpack("<QQI", pf.read(20))

            shutil.copyfile(self.orig_bin_path, applied_path)
            with open(applied_path, "r+b") as out_f:
                for _ in range(num_blocks):
                    offset, raw_len, comp_len = struct.unpack("<QII", pf.read(16))
                    comp_data = pf.read(comp_len)
                    raw_data = zlib.decompress(comp_data)
                    assert len(raw_data) == raw_len
                    out_f.seek(offset)
                    out_f.write(raw_data)

        actual_sha = self.sha256_file(applied_path)
        passed = (actual_sha == expected_trans_sha)
        if passed:
            print(f"[+] Patch Verification PASSED: Output SHA-256 matches translated image 100% BIT-PERFECT ({actual_sha})")
            if applied_path.is_file():
                applied_path.unlink()
        else:
            print(f"[-] Patch Verification FAILED: expected {expected_trans_sha}, got {actual_sha}")
        return passed


def main():
    parser = argparse.ArgumentParser(description="Persona Patch Generator")
    parser.add_argument("--orig", default="psx/Megami Ibunroku Persona (JPN)/PERSONA.BIN", help="Path to original PSX BIN")
    parser.add_argument("--trans", default="build/Megami_Ibunroku_Persona_EN.bin", help="Path to translated PSX BIN")
    parser.add_argument("--out-patch", default="build/Megami_Ibunroku_Persona_EN.patch", help="Path for patch output")
    parser.add_argument("--verify", action="store_true", default=True, help="Verify patch by test application")

    args = parser.parse_args()
    maker = PersonaPatchMaker(args.orig, args.trans, args.out_patch)
    maker.create_patch()
    if args.verify:
        maker.apply_and_verify_patch()


if __name__ == "__main__":
    main()
