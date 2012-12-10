#!/usr/bin/python
"""
This module defines an LC3 machine class for simulating the LC-3 environment.
"""

import lc3instr
import array
import itertools

class LC3Machine(object):
    """
    This class allows for the complete simulation of an LC-3 environment.
    """

    def __init__(self):
        self.pc = 0x3000
        self.mem = array.array('H', itertools.repeat(0, 0x10000))
        self.reg = array.array('H', itertools.repeat(0, 0x8))
        self.cc = 'z'

    def execute(self):
        """Execute one instruction."""
        # get the instruction
        ir = self.mem[self.pc]
        self.pc += 1
        # set up the environment
        env = self._get_instruction_env(ir)
        # call the instruction
        opcode = (ir & 0xF000) >> 12
        self.INSTR_SET[opcode](self, env)

    def _get_instruction_env(self, ir):
        """Fill an environment object for the instruction variables."""
        bits = lambda l, h: (ir >> l) & ((1 << (h - l)) - 1)
        bit = lambda n: (ir >> n) & 1
        env = object()
        env.DR = bits(9, 11)
        env.SR = bits(9, 11)
        env.SR1 = bits(6, 8)
        env.BaseR = bits(6, 8)
        env.SR2 = bits(0, 2)
        env.bit5 = bit(5)
        env.imm5 = bits(0, 4)
        env.PCoffset9 = bits(0, 8)
        env.PCoffset11 = bits(0, 10)
        env.bit11 = bit(11)
        env.offset6 = bits(0, 5)
        env.trapvect8 = bits(0, 7)
        env.cc = ''.join(['pzn'[i - 9] for i in range(11, 8, -1) if bit(i)])
        return env

    def set_cc(self, val):
        """Update the condition codes based on the given value."""
        if val == 0:
            self.cc = 'z'
        elif val < 0:
            self.cc = 'n'
        elif val > 0:
            self.cc = 'p'

    INSTR_SET = {
        0x1: lc3instr.ADD,
        0x5: lc3instr.AND,
        0x0: lc3instr.BR,
        0xC: lc3instr.JMP,
        0x4: lc3instr.JSR,
        0x2: lc3instr.LD,
        0xA: lc3instr.LDI,
        0x6: lc3instr.LDR,
        0x9: lc3instr.NOT,
        0x3: lc3instr.ST,
        0xB: lc3instr.STI,
        0x7: lc3instr.STR,
        0xF: lc3instr.TRAP,
    }

