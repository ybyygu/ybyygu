#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::58ad1935-58aa-46b6-ab3c-823302d97b32][58ad1935-58aa-46b6-ab3c-823302d97b32]]
from .lib import attr
from .element import Element

@attr.s(slots=True, hash=False, cmp=False)
class Atom(object):
    """repsents a single atom

    >>> atom = Atom("H")
    >>> atom = Atom(element=Element.carbon, postion=(1.0, 1.0, 1.0))
    """

    element = attr.ib(default=Element.carbon, convert=Element)

    _position = attr.ib(default=Point3D(0.0, 0.0, 0.0), convert=Point3D._make, repr=False)

    # the index of this atom which will be managed by its parent molecule
    index = attr.ib(default=0)

    # atomic charge, partial charge
    charge = attr.ib(default=0, repr=False)

    # atom's name, e.g.: C1, C13
    _name = attr.ib(default=None)

    properties = attr.ib(default=attr.Factory(dict), init=False)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, xyz):
        self._position = Coord(*xyz)

    @property
    def id(self):
        return self.index

    @property
    def name(self):
        return self._name or "{}{}".format(self.element.symbol, self.index)

    @name.setter
    def name(self, new):
        self._name = new

    @property
    def type(self):
        """atom type"""
        mmtype = self._type or "{}1".format(self.element.symbol)
        return mmtype

    @type.setter
    def type(self, new):
        """set atom type"""
        self._type = new

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return "<Atom> {}".format(self.name)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    @classmethod
    def from_string(cls, xyzline):
        attrs = xyzline.split()
        assert len(attrs) >= 4, "not enough fields: {}".format(xyzline)

        symbol, x, y, z = attrs[:4]

        if symbol.isdigit():
            symbol = int(symbol)

        return cls(symbol, (float(x), float(y), float(z)))

    def to_string(self):
        return "%-6s%18.6f%18.6f%18.6f" % (self.element.symbol, self.position.x, self.position.y, self.position.z)
# 58ad1935-58aa-46b6-ab3c-823302d97b32 ends here
