import os

import numpy
from osgeo import gdal

class Instruction(object):
    """ An instruction represents a pure function from a Part to a list of
    new Parts. """

    def __init__(self):
        pass

    def apply(self, part):
        """ Apply instruction to this chunk of data. Return a list of new
        parts. """
        raise NotImplementedError

class LoadSource(Instruction):
    """ Somewhat special (because it mutates) instruction that reads from a
    source into the array. """

    def __init__(self, source):
        self.source = source

    def apply(self, part):
        self.source.read_into(part)
        return [part]