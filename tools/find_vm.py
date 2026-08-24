#!/usr/bin/env python3
"""
VM Reverser: Find and decode the Persona PSX script interpreter.

Strategy:
1. The game loads E-files to RAM at 0x80100000+ (confirmed from subfile headers)
2. A VM loop reads bytes sequentially: FF-prefixed opcodes control flow,
   other bytes are text glyphs
3. Find the dispatch by looking for the FF-check pattern near the
   font-rendering code we already identified at 0x8001fc50
"""
import struct
from pathlib import Path

exe = Path('extracted/SLPS_005.00').read_bytes()
code = exe[0x800:]  # skip 2048-byte header
BASE = 0x80011930

def disasm(start, length):
    from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32)
    off = start - BASE
    out = []
    for ins in md.disasm(code[off:off+length], start):
        out.append(f'{ins.address:#010x}  {ins.mnemonic:8s} {ins.op_str}')
        if ins.mnemonic == 'jr' and 'ra' in ins.op_str:
            out.append('--- END OF FUNCTION ---')
            break
    return '\n'.join(out)

# Search for the pattern where the VM reads a byte and tests for 0xFF
# In MIPS assembly this would look like:
#   lbu $v0, 0($a0)          ; read byte
#   li $v1, 0xFF             ; or addiu/ori  
#   beq $v0, $v1, <handler>  ; is it a control code?
#
# OR: 
#   lbu $v0, ($ptr)
#   sltiu $t, $v0, 0xFF      ; less than FF?
#   beq $t, $zero, <ctrl_handler>
#
# Let me scan for lbu followed within 6 instructions by an immediate compare with 0xFF

words = struct.unpack('<%dI' % (len(code)//4), code[:len(code)//4*4])

candidates = []
for i in range(len(words) - 12):
    w = words[i]
    op = w >> 26
    
    # Look for LBU (opcode 0x24) or LB (opcode 0x20)
    if op not in (0x24, 0x20):
        continue
    
    # Scan next 8 instructions for comparisons with 0xFF
    found_ff = False
    found_80 = False
    ff_off = -1
    
    for j in range(i+1, min(i+9, len(words))):
        wj = words[j]
        jop = wj >> 26
        imm = wj & 0xFFFF
        
        # ori/addiu with 0xFF, or beq/bne with reg loaded from 0xFF
        if jop in (0x0D, 0x09) and imm == 0xFFFF:
            found_ff = True; ff_off = j - i
        # sltiu with 0x80 (single-byte boundary)
        if jop == 0x0B and imm == 0x0080:
            found_80 = True
    
    if found_ff and found_80:
        candidates.append(i)
    elif found_ff:
        candidates.append(i)

print(f'FF-check + 0x80-boundary candidates: {len(candidates)}')
for c in candidates:
    print(f'  {hex(BASE + c*4)}')
