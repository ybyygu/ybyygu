#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::66e4879d-9a1b-4038-925b-ae8b8d838935][66e4879d-9a1b-4038-925b-ae8b8d838935]]
#===============================================================================#
#   DESCRIPTION:  molecular entity repsented by networkx graph object
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2017-11-21 Tue 16:00>
#       UPDATED:  <2017-11-22 Wed 15:48>
#===============================================================================#
# 66e4879d-9a1b-4038-925b-ae8b8d838935 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024][3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024]]
from collections import namedtuple, Counter, OrderedDict
from itertools import count
from functools import lru_cache  # required python >= 3.2

from .lib import graph
from .lib import attr

Graph = graph.OrderedGraph
# 3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::80950ee5-6f82-4271-8124-f7fa820aef53][80950ee5-6f82-4271-8124-f7fa820aef53]]
@lru_cache(maxsize=1)
def get_reduced_formula(symbols):
    """return chemical formula: C2H4

    Parameters
    ----------
    symbols: element symbols, should be iterable and hashable to make cache to work
    """

    reduced = Counter(symbols) # [("H", 4), ("C", 1)]

    formula = []
    syms = sorted(reduced.keys())

    if "C" in syms:
        syms.remove("C")
        syms.insert(0, "C")

    if "H" in syms:
        syms.remove("H")
        syms.append("H")

    for sym in syms:
        n = reduced[sym]
        if n > 1:
            formula.append("{}{}".format(sym, n))
        else:
            formula.append("{}".format(sym))

    return "".join(formula)
# 80950ee5-6f82-4271-8124-f7fa820aef53 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::24dd16f2-0889-454d-8264-cc8838f72318][24dd16f2-0889-454d-8264-cc8838f72318]]
@attr.s(slots=True)
class MolecularEntity(object):
    """repsents any singular entity, irrespective of its nature, in order
    to concisely express any type of chemical particle: atom,
    molecule, ion, ion pair, radical, radical ion, complex, conformer,
    etc.

    References
    ----------
    1. http://goldbook.iupac.org/M03986.html
    2. https://en.wikipedia.org/wiki/Molecular_entity
    """

    # core structure: networkx Graph
    _graph = attr.ib(default=attr.Factory(Graph), init=False)

    # the title for molecule/atoms
    title = attr.ib(default="molecular entity", validator=attr.validators.instance_of(str))

    # molecular charge
    charge = attr.ib(default=0, init=False)

    # molecular multiplicy
    multiplicity = attr.ib(default=1, init=False)

    @property
    def atoms(self):
        return get_atoms_from_graph(self._graph)

    @property
    def formula(self):
        return get_reduced_formula(self.atoms)
# 24dd16f2-0889-454d-8264-cc8838f72318 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::c0a96813-be11-47c2-aee4-3d7cd7a39acf][c0a96813-be11-47c2-aee4-3d7cd7a39acf]]
Molecule = MolecularEntity
# c0a96813-be11-47c2-aee4-3d7cd7a39acf ends here
