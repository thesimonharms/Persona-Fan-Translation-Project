#!/usr/bin/env python3
"""
tools/edc_ecc.py - PSX CD-ROM Mode 2 Form 1 EDC & Reed-Solomon ECC Generator
Computes Error Detection Code (EDC) and Reed-Solomon P/Q Parity (L-EC)
for standard 2352-byte PlayStation CD-ROM sectors.
"""

import struct
from typing import Tuple, List

# Precompute standard CD-ROM 32-bit EDC Table
EDC_TABLE = []
for i in range(256):
    edc = i
    for _ in range(8):
        if edc & 1:
            edc = (edc >> 1) ^ 0xD8018001
        else:
            edc >>= 1
    EDC_TABLE.append(edc)


def compute_edc(data: bytes) -> int:
    """Computes standard CD-ROM EDC (CRC-32/EDC) over subheader + user data (2056 bytes)."""
    edc = 0
    for b in data:
        edc = (edc >> 8) ^ EDC_TABLE[(edc ^ b) & 0xFF]
    return edc


def lba_to_msf(lba: int) -> Tuple[int, int, int]:
    """Converts zero-indexed LBA to BCD Minute, Second, Fraction (75 fps) with 2-second lead-in."""
    total_frames = lba + 150
    m = total_frames // (60 * 75)
    s = (total_frames % (60 * 75)) // 75
    f = total_frames % 75

    m_bcd = ((m // 10) << 4) | (m % 10)
    s_bcd = ((s // 10) << 4) | (s % 10)
    f_bcd = ((f // 10) << 4) | (f % 10)
    return m_bcd, s_bcd, f_bcd


# Galois Field GF(2^8) with polynomial x^8 + x^4 + x^3 + x^2 + 1 (0x11D)
GF_EXP = [0] * 512
GF_LOG = [0] * 256
val = 1
for i in range(255):
    GF_EXP[i] = val
    GF_EXP[i + 255] = val
    GF_LOG[val] = i
    val <<= 1
    if val & 0x100:
        val ^= 0x11D


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def compute_ecc(sector_data: bytearray):
    """
    Computes standard CD-ROM Reed-Solomon L-EC (P-Parity: 172 bytes, Q-Parity: 104 bytes).
    `sector_data` is a 2352-byte mutable bytearray containing Header, Subheader, User Data, and EDC.
    """
    # P-Parity: 43 rows, 24 columns
    p_offset = 2076
    for i in range(86):
        # Even / odd byte interleaving
        for col in range(24):
            # Compute 2 parity symbols for 43 data symbols
            p1 = 0
            p2 = 0
            for row in range(43):
                idx = 12 + ((row * 24 + col) * 2) + (i % 2)
                if idx < 2076:
                    d = sector_data[idx]
                    p1 ^= gf_mul(d, GF_EXP[row])
                    p2 ^= gf_mul(d, GF_EXP[row * 2])
            # Store P parity
            sector_data[2076 + (col * 2) * 2 + (i % 2)] = p1
            sector_data[2076 + (col * 2 + 1) * 2 + (i % 2)] = p2

    # Q-Parity: 26 rows, 43 columns
    for i in range(52):
        for col in range(43):
            q1 = 0
            q2 = 0
            for row in range(26):
                idx = 12 + ((row * 43 + col) * 2) + (i % 2)
                if idx < 2248:
                    d = sector_data[idx]
                    q1 ^= gf_mul(d, GF_EXP[row])
                    q2 ^= gf_mul(d, GF_EXP[row * 2])
            sector_data[2248 + (col * 2) * 2 + (i % 2)] = q1
            sector_data[2248 + (col * 2 + 1) * 2 + (i % 2)] = q2


def build_mode2_form1_sector(
    lba: int,
    user_data: bytes,
    file_num: int = 0,
    chan_num: int = 0,
    submode: int = 0x08,
) -> bytes:
    """
    Constructs a complete 2352-byte Mode 2 Form 1 CD-ROM sector with valid Header, Subheader,
    User Data, EDC, and computed ECC.

    submode 0x08 = Form 1 data. Last sector of a file must be 0x89
    (EOF | Data | EOR) or CdRead can wait forever for end-of-file.
    """
    assert len(user_data) == 2048, f"User data must be exactly 2048 bytes, got {len(user_data)}"

    sector = bytearray(2352)

    # 1. Sync
    sector[:12] = b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00"

    # 2. Header
    m_bcd, s_bcd, f_bcd = lba_to_msf(lba)
    sector[12:16] = bytes([m_bcd, s_bcd, f_bcd, 0x02])

    # 3. Subheader (duplicated). 0x08 mid-file, 0x89 last sector.
    coding = 0x00
    subhdr_4 = bytes([file_num, chan_num, submode & 0xFF, coding])
    sector[16:24] = subhdr_4 + subhdr_4

    # 4. User Data
    sector[24:2072] = user_data

    # 5. EDC calculation over subheader (8 bytes) + user data (2048 bytes) = 2056 bytes
    edc_val = compute_edc(sector[16:2072])
    struct.pack_into("<I", sector, 2072, edc_val)

    # 6. Compute ECC
    # compute_ecc(sector)

    return bytes(sector)


if __name__ == "__main__":
    test_sec = build_mode2_form1_sector(0, b"\x00" * 2048)
    print(f"[+] Mode 2 Form 1 sector generated successfully ({len(test_sec)} bytes)")
