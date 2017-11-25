#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::58ad1935-58aa-46b6-ab3c-823302d97b32][58ad1935-58aa-46b6-ab3c-823302d97b32]]
from collections import namedtuple

from .lib import attr
from .element import Element

_bohr2ang = 0.529177

Point3D = namedtuple("Point3D", ("x", "y", "z"))

def Coord(x, y, z, unit="au"):
    """a convenient wrapper for unit conversion"""

    if unit not in ("angstrom", "au", "bohr"):
        raise TypeError("unkown unit: {}".format(unit))

    if unit == "bohr":
        x, y, z = x*_bohr2ang, y*_bohr2ang, z*_bohr2ang

    # always store in angstrom
    return Point3D(x, y, z)


class Atom(object):
    """repsents a single atom

    >>> atom = Atom("H")
    >>> atom = Atom(element=Element.carbon, postion=(1.0, 1.0, 1.0))
    """

    __slots__ = ('_data')

    def __init__(self, element=Element.dummy, position=(0, 0, 0), index=0, name=None):
        symbol = Element(element).symbol
        postion = tuple(position)
        if name is None:
            name = "{}{}".format(symbol, index)
        # all data stored in a dict
        self._data = dict(symbol=symbol, position=position, index=index, name=name)


    @property
    def index(self):
        i = self._data.get('index')
        if i is not None:
            return i
        raise ValueError("no index data")

    @property
    def element(self):
        e = self._data.get('symbol')
        if e is not None:
            return Element(e)
        return Element.dummy

    @element.setter
    def element(self, new):
        self._data['symbol'] = Element(new).symbol

    @property
    def position(self):
        r = self._data.get('position')
        if r is not None:
            r = Point3D._make(r)
            return r
        raise ValueError("no position data")

    @position.setter
    def position(self, xyz):
        self._data['position'] = tuple(xyz)

    @property
    def name(self):
        n = self._data.get('name')
        if n is not None:
            return n
        n = "{}{}".format(self.element.symbol, self.index)
        self._data['name'] = n
        return n

    @name.setter
    def name(self, new):
        self._data['name'] = new

    def update(self, d):
        self._data.update(d)

    def __str__(self):
        return self.to_string()

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def to_string(self):
        return "%-6s%18.6f%18.6f%18.6f" % (self.element.symbol, self.position.x, self.position.y, self.position.z)

    def to_dict(self):
        return self._data.copy()

    @classmethod
    def from_string(cls, xyzline):
        attrs = xyzline.split()
        assert len(attrs) >= 4, "not enough fields: {}".format(xyzline)

        symbol, x, y, z = attrs[:4]

        if symbol.isdigit():
            symbol = int(symbol)

        return cls(symbol, (float(x), float(y), float(z)))
# 58ad1935-58aa-46b6-ab3c-823302d97b32 ends here
