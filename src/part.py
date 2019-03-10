from osgeo import gdal 

class Part(object):

    def __init__(self, geotransform, projection, data):
        self.geotransform = geotransform
        self.projection = projection
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
        ny, nx = self.data.shape
        top_left = (self.geotransform.a, self.geotransform.d)
        bot_right = self.geotransform.apply(nx, ny)

        return (
            min(top_left[0], bot_right[0]),
            min(top_left[1], bot_right[1]),
            max(top_left[0], bot_right[0]),
            max(top_left[1], bot_right[1])
        )