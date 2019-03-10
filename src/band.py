import itertools

import numpy
from osgeo import gdal

from .instruction import LoadSource
from .part import Part

class Band(object):
    def __init__(self, source, pipeline=None):
        # The pipeline describes how this band is created.
        self.source = source
        self._pipeline = pipeline if pipeline is not None else Pipeline([LoadSource(source)])

    def _parts(self):
        """ Returns and iterator of Part objects """
        nx, ny = self.source.raster_size
        xsize, ysize = 2048, 2048
        x, y = 0, 0
        while y < ny - 1:
            while x < nx - 1:
                part = self.source.part(x, y, min(xsize, nx - x), min(ysize, ny - y))
                yield self._pipeline.apply(part)
                x += xsize
            x = 0
            y += ysize
        return

    @property
    def pipeline(self):
        return self._pipeline

    def and_then(self, instruction):
        return Band(self.source, self.pipeline.and_then(instruction))

    def apply(self):
        parts = [p for p in self._parts()]
        return itertools.chain(*parts)

    def render_to_file(self, filename, fmt='GTiff'):
        parts = list(self.apply())
        if len(parts) == 0:
            return self

        nbands = 1 # FIXME
        datatype = gdal.GDT_UInt16 # FIXME

        raster_extent = compute_extent(parts)
        gt1 = parts[0].geotransform[1]
        gt2 = parts[0].geotransform[2]
        gt4 = parts[0].geotransform[4]
        gt5 = parts[0].geotransform[5]
        geotransform = [raster_extent[0], gt1, gt2, raster_extent[3], gt4, gt5]
        top_left_index = invert(geotransform, raster_extent[0], raster_extent[1])
        bot_right_index = invert(geotransform, raster_extent[2], raster_extent[3])
        xsize = abs(bot_right_index[0] - top_left_index[0])
        ysize = abs(bot_right_index[1] - top_left_index[1])

        driver = gdal.GetDriverByName(fmt)
        try:
            dataset = driver.Create(filename, xsize, ysize, nbands, datatype)
            dataset.SetGeoTransform(geotransform)
            dataset.SetProjection(parts[0].projection)
        finally:
            driver = None

        try:
            band = dataset.GetRasterBand(1)
            for part in parts:
                xoff, yoff = invert(geotransform, part.geotransform[0], part.geotransform[3])
                ysize, xsize = part.data.shape
                band.WriteRaster(xoff, yoff, xsize, ysize, part.data.tobytes())
            band.FlushCache()
        finally:
            band = None
            dataset = None
        return self

def invert(geotransform, x, y):
    """ compute the (j, i) index of a cell given a geotransform, where the
    top left corner of the cell is at (x, y) """
    a, b, c, d, e, f = geotransform

    if e == 0:
        i = (b * y - b * d - e * x + e * a) / (b * f - e * c)
        j = (x - a - i * c) / b
    else:
        i = (e * x - e * a - b * y + b * d) / (e * c - b * f)
        j = (y - d - i * f) / e

    return int(j), int(i)

def compute_extent(parts):
    xmin, ymin, xmax, ymax = None, None, None, None
    for part in parts:
        part_bounds = part.extent
        xmin = part_bounds[0] if xmin is None else min(part_bounds[0], xmin)
        ymin = part_bounds[1] if ymin is None else min(part_bounds[1], ymin)
        xmax = part_bounds[2] if xmax is None else max(part_bounds[2], xmax)
        ymax = part_bounds[3] if ymax is None else max(part_bounds[3], ymax)
    return (xmin, ymin, xmax, ymax)

def combine_to_array(parts):
    print("done")

class Pipeline(object):

    def __init__(self, steps=None):
        self._instructions = steps if steps else []

    @property
    def instructions(self):
        return [instr for instr in self._instructions]

    def and_then(self, instruction):
        return Pipeline(self.instructions + [instruction])

    def apply(self, part):
        parts = [part]
        for instr in self.instructions:
            new_parts = []
            for p in parts:
                new_parts.extend(instr.apply(p))
            parts = new_parts
        return parts

class FileInput(object):
    def __init__(self, filename):
        self.filename = filename
        ds = gdal.Open(self.filename)
        try:
            self._geotransform = ds.GetGeoTransform()
            self._projection = ds.GetProjection()
            self.raster_size = (ds.RasterXSize, ds.RasterYSize)
        finally:
            ds = None

    def part(self, j, i, nx, ny):
        """ Read (nx, ny) pixels, starting from x0, y0 in the top left """
        gt0, gt1, gt2, gt3, gt4, gt5 = self._geotransform
        new_geotransform = [
            gt0 + j * gt1 + i * gt4,
            gt1,
            gt2,
            gt3 + i * gt5 + j * gt2,
            gt4,
            gt5,
        ]
        return Part(new_geotransform, self._projection, j, i, numpy.empty([ny, nx], numpy.uint16))

    def read_into(self, part):
        ysize, xsize = part.data.shape
        dataset = gdal.Open(self.filename)
        try:
            band = dataset.GetRasterBand(1)
            band.ReadAsArray(part._j,
                             part._i,
                             xsize,
                             ysize,
                             buf_obj=part.data)
        finally:
            band = None
            dataset = None
