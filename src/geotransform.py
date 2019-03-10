class GeoTransform(object):

    def __init__(self, a, b, c, d, e, f):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def apply(self, j, i):
        """ compute the (x, y) coordinates of the upper left corner of a cell
        where the indices are (j, i) """
        x = self.a + j*self.b + i*self.c
        y = self.d + j*self.e + i*self.f
        return (x, y)

    def invert(self, x, y):
        """ compute the (j, i) index of a cell where the top left corner of
        the cell is at (x, y) """
        a, b, c, d, e, f = self.a, self.b, self.c, self.d, self.e, self.f

        if e == 0:
            i = (b*y - b*d - e*x + e*a) / (b*f - e*c)
            j = (x - a - i*c) / b
        else:
            i = (e*x - e*a - b*y + b*d) / (e*c - b*f)
            j = (y - d - i*f) / e

        return int(j), int(i)

    def to_list(self):
        return [self.a, self.b, self.c, self.d, self.e, self.f]