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

    >>> atom = Atom()
    >>> atom = Atom("H")
    >>> atom = Atom(element='C', position=(1.0, 1.0, 1.0))
    >>> atom = Atom(data={'element'='Br', 'position'=(0, 0, 0)})
    """

    __slots__ = ('_data')

    def __init__(self, element=None, position=None, data=None, **kwargs):
        # all data stored in a private dict
        if data is None:
            self._data = {}
        elif issubclass(type(data), dict):
            self._data  = data
        else:
            raise TypeError("data should be a dict type: {}".format(data))

        # element specified in data dict will be override if element argument is not empty
        if element is None:     # set in data dict?
            element = self._data.get('element')
        else:                   # set in positional argument
            element = Element(element).symbol
        if element is None:      # set default element
            element = Element.dummy.symbol

        # position specified in data dict will be override if position argument is not empty
        if position is None:    # set in data dict?
            position = self._data.get('position')
        else:                   # set in positional argument
            position = tuple(position)
        if position is None:    # set default position
            position = (0, 0, 0)

        kwargs['position'] = position
        kwargs['element'] = element
        self._data.update(kwargs)

    @property
    def index(self):
        return self._data.get('index', 0)

    @property
    def element(self):
        e = self._data.get('element')
        if e is not None:
            return Element(e)
        return Element.dummy

    @element.setter
    def element(self, new):
        self._data['element'] = Element(new).symbol

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

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new):
        self._data = new

    @classmethod
    def from_string(cls, xyzline):
        attrs = xyzline.split()
        assert len(attrs) >= 4, "not enough fields: {}".format(xyzline)

        element, x, y, z = attrs[:4]

        if element.isdigit():
            element = int(element)

        return cls(element, (float(x), float(y), float(z)))
# 58ad1935-58aa-46b6-ab3c-823302d97b32 ends here
