import os

import numpy
from osgeo import gdal

from .part import Part
from .geotransform import GeoTransform

class Instruction(object):
    """ An instruction represents a pure function from a Part to a list of
    new Parts. """

    def __init__(self):
        pass

    def apply(self, part):
        """ Apply instruction to this chunk of data. Return a list of new
        parts. """
        raise NotImplementedError

class Clip(Instruction):
    """ Clip cuts out the intersection of the extent passed in and the
    raster. """

    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def apply(self, part):
        extent = part.extent
        if self.xmin > extent[2] or self.xmax < extent[0] or self.ymin > extent[3] or self.ymax < extent[0]:
            # Part lies wholly without the extent
            return []
        elif self.xmin < extent[0] and self.xmax > extent[2] and self.ymin < extent[1] and self.ymax > extent[3]:
            # Part lies wholly within the extent
            return [part]
        else:
            top_left_x = max(min(part.geotransform.a, self.xmax), self.xmin)
            top_left_y = max(min(part.geotransform.d, self.ymax), self.ymin)
            top_left = part.geotransform.invert(top_left_x, top_left_y)
            # may overshoot, which is okay because of how numpy indexing works
            bot_right = part.geotransform.invert(self.xmax, self.ymin)
            _, b, c, _, e, f = part.geotransform.to_list()

            new_geotransform = GeoTransform(top_left_x, b, c, top_left_y, e, f)
            new_data = part.data[top_left[1]:bot_right[1], top_left[0]:bot_right[0]]
            return [Part(new_geotransform, part.projection, new_data)]

class Debug(Instruction):

    def __init__(self, partfunc):
        self.func = partfunc

    def apply(self, part):
        print(self.func(part))
        return [part]