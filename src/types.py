import numpy
from osgeo import gdal

GDT_TO_NUMPY = {
    gdal.GDT_Byte: numpy.uint8,
    gdal.GDT_UInt16: numpy.uint16,
    gdal.GDT_UInt32: numpy.uint32,
    gdal.GDT_Int16: numpy.int16,
    gdal.GDT_Int32: numpy.int32,
    gdal.GDT_Float32: numpy.float32,
    gdal.GDT_Float64: numpy.float64,
    gdal.GDT_CFloat64: numpy.complex64,
}

NUMPY_TO_GDT = {v: k for k, v in GDT_TO_NUMPY.items()}