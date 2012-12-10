"""
This module defines the LC-3 instruction set.

Each of the following functions accept an LC-3 object mach, and an instruction
environment object env with the following attributes, where [a:b] means bits a
through b, inclusive:

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

def ADD(mach, env):
    if env.bit5:
        mach.reg[env.DR] = mach.reg[env.SR1] + env.imm5
    else:
        mach.reg[env.DR] = mach.reg[env.SR1] + mach.reg[env.SR2]
    mach.set_cc(mach.reg[env.DR])

def AND(mach, env):
    if env.bit5:
        mach.reg[env.DR] = mach.reg[env.SR1] & env.imm5
    else:
        mach.reg[env.DR] = mach.reg[env.SR1] & mach.reg[env.SR2]
    mach.set_cc(mach.reg[env.DR])

def BR(mach, env):
    if mach.cc in env.cc:
        mach.pc += env.PCoffset9

def JMP(mach, env):
    mach.pc = env.BaseR

def JSR(mach, env):
    temp = mach.pc
    if env.bit11:
        mach.pc += env.PCoffset11
    else:
        mach.pc = env.BaseR
    mach.reg[7] = temp

def LD(mach, env):
    mach.reg[env.DR] = mach.mem[mach.pc + env.PCoffset9]
    mach.set_cc(mach.reg[env.DR])

def LDI(mach, env):
    mach.reg[env.DR] = mach.mem[mach.mem[mach.pc + env.PCoffset9]]
    mach.set_cc(mach.reg[env.DR])

def LDR(mach, env):
    mach.reg[env.DR] = mach.mem[mach.reg[env.BaseR] + env.offset6]
    mach.set_cc(mach.reg[env.DR])

def LEA(mach, env):
    mach.reg[env.DR] = mach.pc + env.PCoffset9
    mach.set_cc(mach.reg[env.DR])

def NOT(mach, env):
    mach.reg[env.DR] = (~mach.reg[env.SR] & 0xFFFF)
    mach.set_cc(mach.reg[env.DR])

def ST(mach, env):
    mach.mem[mach.pc + env.PCoffset9] = mach.reg[env.SR]

def STI(mach, env):
    mach.mem[mach.mem[mach.pc + env.PCoffset9]] = mach.reg[env.SR]

def STR(mach, env):
    mach.mem[mach.reg[env.BaseR] + env.offset6] = mach.reg[env.SR]

def TRAP(mach, env):
    mach.reg[7] = mach.pc
    mach.pc = mach.mem[env.trapvect8]
