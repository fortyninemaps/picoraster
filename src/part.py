from osgeo import gdal 

class Part(object):

    def __init__(self, geotransform, projection, j, i, data):
        self.geotransform = geotransform
        self.projection = projection
        self._j = j
        self._i = i
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def datatype(self):
        # FIXME
        return gdal.GDT_Int16

    @property
    def extent(self):
        a, b, c, d, e, f = self.geotransform
        ny, nx = self.data.shape
        top_left = (a, d)
        bot_right = (a + nx * b + ny * c, d + nx * e + ny * f)

        return (
            min(top_left[0], bot_right[0]),
            min(top_left[1], bot_right[1]),
            max(top_left[0], bot_right[0]),
            max(top_left[1], bot_right[1])
        )