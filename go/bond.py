#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f48ba944-02bd-4ac0-bc39-6713aa91f65f][f48ba944-02bd-4ac0-bc39-6713aa91f65f]]
from enum import Enum
from collections import namedtuple

from .atom import Atom

class BondOrder(Enum):
    """https://en.wikipedia.org/wiki/Bond_order"""
    disconnected =  0.0
    partial      =  0.5
    single       =  1.0
    aromatic     =  1.5
    double       =  2.0
    tripple      =  3.0
    quadruple    =  4.0

class _Bond(namedtuple("Bond", "atom1 atom2 order".split())):
    """basic bond definition"""
    __slots__ = ()

    def __str__(self):
        return "{}-{}: {}".format(self.atom1.name, self.atom2.name, self.order.name)

    def __eq__(self, other):
        if self.atom1 == other.atom1 and self.atom2 == other.atom2:
            return True
        if self.atom1 == other.atom2 and self.atom2 == other.atom1:
            return True
        return False

# make simple thing simple
def Bond(atom1, atom2, order=BondOrder.single):
    return _Bond(atom1, atom2, BondOrder(order))
# f48ba944-02bd-4ac0-bc39-6713aa91f65f ends here
