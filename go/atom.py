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


@attr.s(slots=True, hash=False, cmp=False)
class Atom(object):
    """repsents a single atom

    >>> atom = Atom("H")
    >>> atom = Atom(element=Element.carbon, postion=(1.0, 1.0, 1.0))
    """

    element = attr.ib(default=Element.carbon, convert=Element)

    _position = attr.ib(default=Point3D(0.0, 0.0, 0.0), convert=Point3D._make, repr=False)

    # the index of this atom which will be managed by its parent molecule
    index = attr.ib(default=0, validator=attr.validators.instance_of(int))

    # atom's name, e.g.: C1, C13
    _name = attr.ib(default=None)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, xyz):
        self._position = Coord(*xyz)

    @property
    def name(self):
        return self._name or "{}{}".format(self.element.symbol, self.index)

    @name.setter
    def name(self, new):
        self._name = new

    def __str__(self):
        return self.to_string()

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def to_string(self):
        return "%-6s%18.6f%18.6f%18.6f" % (self.element.symbol, self.position.x, self.position.y, self.position.z)

    @classmethod
    def from_string(cls, xyzline):
        attrs = xyzline.split()
        assert len(attrs) >= 4, "not enough fields: {}".format(xyzline)

        symbol, x, y, z = attrs[:4]

        if symbol.isdigit():
            symbol = int(symbol)

        return cls(symbol, (float(x), float(y), float(z)))
# 58ad1935-58aa-46b6-ab3c-823302d97b32 ends here
