#!/usr/bin/python
"""
This module defines an LC3 machine class for simulating the LC-3 environment.
"""

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
        self.INSTR_SET[opcode](env)

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

    def _update_cc(self, val):
        """Update the condition codes based on the given value."""
        if val == 0:
            self.cc = 'z'
        elif val < 0:
            self.cc = 'n'
        elif val > 0:
            self.cc = 'p'

    INSTR_SET = {
        0x1: LC3Machine.ADD,
        0x5: LC3Machine.AND,
        0x0: LC3Machine.BR,
        0xC: LC3Machine.JMP,
        0x4: LC3Machine.JSR,
        0x2: LC3Machine.LD,
        0xA: LC3Machine.LDI,
        0x6: LC3Machine.LDR,
        0x9: LC3Machine.NOT,
        0x3: LC3Machine.ST,
        0xB: LC3Machine.STI,
        0x7: LC3Machine.STR,
        0xF: LC3Machine.TRAP,
    }

    """
    LC-3 instruction set

    Each of the following functions accept an object env, with the following
    attributes, where [a:b] means bits a through b, inclusive.

                 DR: [9:11]
                 SR: [9:11]
                SR1: [6:8]
              BaseR: [6:8]
                SR2: [0:2]
               bit5: [5]
               imm5: [0-4]
          PCoffset9: [0:8]
         PCoffset11: [0:10]
              bit11: [11]
            offset6: [0:5]
          trapvect8: [0:7]
                 cc: some subset of 'nzp', depending on bits [9:11]
    """

    def ADD(self, env):
        if env.bit5:
            self.reg[env.DR] = self.reg[env.SR1] + env.imm5
        else:
            self.reg[env.DR] = self.reg[env.SR1] + self.reg[env.SR2]
        self._update_cc(self.reg[env.DR])

    def AND(self, env):
        if env.bit5:
            self.reg[env.DR] = self.reg[env.SR1] & env.imm5
        else:
            self.reg[env.DR] = self.reg[env.SR1] & self.reg[env.SR2]
        self._update_cc(self.reg[env.DR])

    def BR(self, env):
        if self.cc in env.cc:
            self.pc += env.PCoffset9

    def JMP(self, env):
        self.pc = env.BaseR

    def JSR(self, env):
        temp = self.pc
        if env.bit11:
            self.pc += env.PCoffset11
        else:
            self.pc = env.BaseR
        self.reg[7] = temp

    def LD(self, env):
        self.reg[env.DR] = self.mem[self.pc + env.PCoffset9]
        self._update_cc(self.reg[env.DR])

    def LDI(self, env):
        self.reg[env.DR] = self.mem[self.mem[self.pc + env.PCoffset9]]
        self._update_cc(self.reg[env.DR])

    def LDR(self, env):
        self.reg[env.DR] = self.mem[self.reg[env.BaseR] + env.offset6]
        self._update_cc(self.reg[env.DR])

    def LEA(self, env):
        self.reg[env.DR] = self.pc + env.PCoffset9
        self._update_cc(self.reg[env.DR])

    def NOT(self, env):
        self.reg[env.DR] = (~self.reg[env.SR] & 0xFFFF)
        self._update_cc(self.reg[env.DR])

    def ST(self, env):
        self.mem[self.pc + env.PCoffset9] = self.reg[env.SR]

    def STI(self, env):
        self.mem[self.mem[self.pc + env.PCoffset9]] = self.reg[env.SR]

    def STR(self, env):
        self.mem[self.reg[env.BaseR] + env.offset6] = self.reg[env.SR]

    def TRAP(self, env):
        self.reg[7] = self.pc
        self.pc = self.mem[env.trapvect8]

