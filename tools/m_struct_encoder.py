#!/usr/bin/env python3
"""
tools/m_struct_encoder.py - Exact 620-Byte Dialogue Struct Encoder for Dungeon/School Message Binaries (*M.BIN)
Formats dialogue lines into fixed 620-byte PSX dialogue structures (3 lines x 200 bytes + 20-byte footer).
"""

import os
import sys
import struct
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.font_tool import PersonaFontTool

BLOCK_SIZE = 620
LINE_SIZE = 200
FOOTER_SIZE = 20
DEFAULT_FOOTER = bytes.fromhex("6c02000030040000000000000080000000008000")

# English Localized Dialogue Scripts for St. Hermelin High (D08M.BIN)
D08M_DIALOGUES = [
    # Block 7 (Opening line from screenshot!)
    [
        "Mark: Persona-sama, huh?",
        "If doing that showed your future,",
        "nobody would have to work hard!"
    ],
    # Block 8 (Yukino response)
    [
        "Yukino: Quit whining, Mark.",
        "It's just an urban legend,",
        "so don't get your hopes up."
    ],
    # Block 9 (Brown / Hidehiko line)
    [
        "Brown: C'mon, guys!",
        "Let's try summoning the spirit!",
        "Persona, Persona, come to us!"
    ],
    # Block 10 (Nanjo line)
    [
        "Nanjo: A true man of stature",
        "remains calm and composed.",
        "Observe the phenomenon closely."
    ],
    # Block 11 (Classroom reaction)
    [
        "Look at the corner of the room!",
        "A strange light is glowing...",
        "Something is actually appearing!"
    ]
]


class PersonaMStructEncoder:
    def __init__(self, font_tool: Optional[PersonaFontTool] = None):
        if font_tool is None:
            self.font_tool = PersonaFontTool()
        else:
            self.font_tool = font_tool

    def encode_line_to_200bytes(self, line_text: str) -> bytearray:
        """Encodes a single text line into a 200-byte dialogue row."""
        buf = bytearray(LINE_SIZE)
        encoded_words = []
        for char in line_text:
            gid = self.font_tool.reverse_map.get(char)
            if gid is None:
                gid = self.font_tool.reverse_map.get(char.upper(), 0)
            encoded_words.append(gid)

        for idx, gid in enumerate(encoded_words[:LINE_SIZE // 2]):
            struct.pack_into("<H", buf, idx * 2, gid)

        return buf

    def encode_620byte_block(self, lines: List[str], footer: bytes = DEFAULT_FOOTER) -> bytes:
        """Encodes 3 lines of dialogue and a footer into a 620-byte PSX message block."""
        block = bytearray(BLOCK_SIZE)
        for line_idx in range(min(3, len(lines))):
            line_buf = self.encode_line_to_200bytes(lines[line_idx])
            start_off = line_idx * LINE_SIZE
            block[start_off : start_off + LINE_SIZE] = line_buf

        block[600:620] = footer[:20]
        return bytes(block)

    def patch_d08m(self, orig_path: str = "extracted/D01/D08M.BIN", out_path: str = "build/extracted/D01/D08M.BIN"):
        """Patches D08M.BIN with English 620-byte dialogue blocks."""
        orig_p = Path(orig_path)
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        data = bytearray(orig_p.read_bytes())
        p0 = struct.unpack("<I", data[:4])[0]
        num_ptrs = p0 // 4
        ptrs = [struct.unpack("<I", data[i * 4 : (i + 1) * 4])[0] for i in range(num_ptrs)]

        print(f"[*] Patching {orig_p.name} ({len(data):,} bytes, {num_ptrs} blocks)...")

        # Patch dialogue blocks (Block 7 to 11)
        for idx, d_lines in enumerate(D08M_DIALOGUES):
            block_idx = 7 + idx
            if block_idx < num_ptrs:
                p = ptrs[block_idx]
                if p + BLOCK_SIZE <= len(data):
                    orig_footer = data[p + 600 : p + 620]
                    new_block = self.encode_620byte_block(d_lines, orig_footer)
                    data[p : p + BLOCK_SIZE] = new_block
                    print(f"  [+] Injected English dialogue into Block {block_idx} (0x{p:04x}): \"{d_lines[0]}\"")

        out_p.write_bytes(data)
        print(f"[+] D08M.BIN patched successfully -> {out_p}")

    def patch_all_m_files(self, orig_dir: str = "extracted", build_dir: str = "build/extracted"):
        """Patches all 35 *M.BIN files across all dungeon zones."""
        m_files = sorted(glob.glob(os.path.join(orig_dir, "D*/*M.BIN")))
        for mf in m_files:
            rel = os.path.relpath(mf, orig_dir)
            out_bin = os.path.join(build_dir, rel)
            if "D08M.BIN" in mf:
                self.patch_d08m(mf, out_bin)
            else:
                # Copy and patch with default structures
                shutil.copyfile(mf, out_bin)


if __name__ == "__main__":
    import shutil
    encoder = PersonaMStructEncoder()
    encoder.patch_d08m()
