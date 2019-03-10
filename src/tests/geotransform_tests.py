import unittest

from ..geotransform import GeoTransform

class GeotransformTests(unittest.TestCase):

    def round_trip(self, t, j, i):
        x, y = t.apply(j, i)
        nj, ni = t.invert(x, y)
        self.assertEqual((j, i), (nj, ni))

    def test_north_up(self):
        t = GeoTransform(1.0, 2, 0, 2.0, 0, 3)
        self.assertEqual(t.apply(3, 4), (7.0, 14.0))
        self.round_trip(t, 3, 4)

    def test_north_down(self):
        t = GeoTransform(1.0, 2, 0, 2.0, 0, -3)
        self.assertEqual(t.apply(3, 4), (7.0, -10.0))
        self.round_trip(t, 3, 4)

    def test_east_up(self):
        t = GeoTransform(1.0, 0, 1, 2.0, 3, 0)
        self.assertEqual(t.apply(3, 4), (5.0, 11.0))
        self.round_trip(t, 3, 4)