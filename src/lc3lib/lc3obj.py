#!/usr/bin/python
"""
This module defines a class for encapsulating compiled object files.
"""

import lc3asm
import array
import struct

class ObjectFile(object):
    """
    This class represents an object file, with associated symbols.
    """

    def __init__(self, objfile=None, asmfile=None):
        """
        Initialize this ObjectFile from either a pre-existing object file or
        an assembly file.
        """
        self.symbols = {}
        self.ranges = {}

    def add_range(self, addr, values):
        """
        Add the given values to this ObjectFile's ranges.
        """
        self.ranges[addr] = values

    def load_from_obj(self, filename):
        """
        Load the given object file into this machine.
        """
        with open(filename, 'rb') as f:
            while True:
                # read the 4-bytes .orig header
                data = f.read(4)
                if not data:
                    break
                addr, size = struct.unpack('>HH', data)
                # read the data
                for i in xrange(size):
                    data = f.read(2)
                    if not data:
                        raise RuntimeError("Binary file does not follow format")
                    self.mem[addr + i] = struct.unpack('>H', data)[0]


class Range(array.array):
    """A range within LC-3 memory."""

    def __init__(self, initializer=None):
        array.array.__init__(self, 'H', initializer)
