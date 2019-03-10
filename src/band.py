import itertools

import numpy
from osgeo import gdal

from .geotransform import GeoTransform
from .pipeline import Pipeline
from .types import NUMPY_TO_GDT

class Band(object):
    def __init__(self, source, pipeline=None):
        # The pipeline describes how this band is created.
        self.source = source
        self._pipeline = pipeline if pipeline is not None else Pipeline()

    def _parts(self):
        """ Returns and iterator of Part objects """
        nx, ny = self.source.raster_size
        xsize, ysize = 1024, 1024
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
        datatype = NUMPY_TO_GDT[parts[0].numpy_datatype]

        raster_extent = compute_extent(parts)
        gt1 = parts[0].geotransform.b
        gt2 = parts[0].geotransform.c
        gt4 = parts[0].geotransform.e
        gt5 = parts[0].geotransform.f
        geotransform = GeoTransform(raster_extent[0], gt1, gt2, raster_extent[3], gt4, gt5)
        top_left_index = geotransform.invert(raster_extent[0], raster_extent[1])
        bot_right_index = geotransform.invert(raster_extent[2], raster_extent[3])
        xsize = abs(bot_right_index[0] - top_left_index[0])
        ysize = abs(bot_right_index[1] - top_left_index[1])

        driver = gdal.GetDriverByName(fmt)
        try:
            dataset = driver.Create(filename, xsize, ysize, nbands, datatype)
            dataset.SetGeoTransform(geotransform.to_list())
            dataset.SetProjection(parts[0].projection)
        finally:
            driver = None

        try:
            band = dataset.GetRasterBand(1)
            for part in parts:
                xoff, yoff = geotransform.invert(part.geotransform.a, part.geotransform.d)
                ysize, xsize = part.data.shape
                band.WriteRaster(xoff, yoff, xsize, ysize, part.data.tobytes())
            band.FlushCache()
        finally:
            band = None
            dataset = None
        return self

def compute_extent(parts):
    xmin, ymin, xmax, ymax = None, None, None, None
    for part in parts:
        part_bounds = part.extent
        xmin = part_bounds[0] if xmin is None else min(part_bounds[0], xmin)
        ymin = part_bounds[1] if ymin is None else min(part_bounds[1], ymin)
        xmax = part_bounds[2] if xmax is None else max(part_bounds[2], xmax)
        ymax = part_bounds[3] if ymax is None else max(part_bounds[3], ymax)
    return (xmin, ymin, xmax, ymax)