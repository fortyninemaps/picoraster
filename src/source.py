from os import path

import numpy
from osgeo import gdal

from .geotransform import GeoTransform
from .part import Part
from .types import GDT_TO_NUMPY

class Source(object):
    def part(self, j, i, nx, ny):
        """ Read (nx, ny) pixels, starting from x0, y0 in the top left """
        raise NotImplementedError


class FileSource(Source):
    def __init__(self, filename):
        self.filename = filename
        ds = gdal.Open(self.filename)
        try:
            self._geotransform_array = ds.GetGeoTransform()
            self._projection = ds.GetProjection()
            self.raster_size = (ds.RasterXSize, ds.RasterYSize)
        finally:
            ds = None

    def part(self, j, i, nx, ny):
        """ Read (nx, ny) pixels, starting from x0, y0 in the top left """
        gt0, gt1, gt2, gt3, gt4, gt5 = self._geotransform_array
        new_geotransform = GeoTransform(gt0 + j*gt1 + i*gt4,
                                        gt1,
                                        gt2,
                                        gt3 + i*gt5 + j*gt2,
                                        gt4,
                                        gt5)

        dataset = gdal.Open(self.filename)
        try:
            band = dataset.GetRasterBand(1)
            dt = GDT_TO_NUMPY[band.DataType]
            buf = numpy.empty([ny, nx], dt)
            band.ReadAsArray(j, i, nx, ny, buf_obj=buf)
        finally:
            band = None
            dataset = None

        return Part(new_geotransform, self._projection, buf)

class AWSLandsat8Source(Source):
    def __init__(self, scene_id, band="8", aws_key=None, aws_secret=None):
        self.scene_id = scene_id
        collection, sensor, path, row = self.decode_scene_id(scene_id)
        self.filename = f"/vsis3/landsat-pds/{collection}/{sensor}/{path}/{row}/{scene_id}/{scene_id}_B{band}.TIF"

        gdal.SetConfigOption('AWS_ACCESS_KEY_ID', aws_key)
        gdal.SetConfigOption('AWS_SECRET_ACCESS_KEY', aws_secret)
        self.source = FileSource(self.filename)

        self._geotransform_array = self.source._geotransform_array
        self._projection = self.source._projection
        self.raster_size = self.source.raster_size

    @staticmethod
    def decode_scene_id(scene_id):
        tokens = scene_id.split("_")
        pathrow = tokens[2]
        path = pathrow[:3]
        row = pathrow[3:]
        return "c1", "L8", path, row

    def part(self, j, i, nx, ny):
        """ Read (nx, ny) pixels, starting from x0, y0 in the top left """
        return self.source.part(j, i, nx, ny)