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
#       UPDATED:  <2017-11-27 Mon 09:22>
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

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::1fe1da74-2e5f-4999-9e6b-ac674946a305][1fe1da74-2e5f-4999-9e6b-ac674946a305]]
import re
from .atom import Atom

mol2_bond_orders = {
    "1" : 1.0,
    "2" : 2.0,
    "3" : 3.0,
    "ar": 1.5,
    "du": 0.5,
    "dm": 2.0,
    "am": 1.2,
    "un": 0.0,
    "nc": 0.0
}

def graph_from_mol2file(filename, trajectory=False):
    """a quick and dirty way to store molecular data in networkx graph object

    Parameters
    ---------
    filename: the path to a tripos mol2 file
    trajectory: read all trajectory or not.

    Return
    ------
    a networkx graph object or a list of graph objects (trajectory)
    """

    data_atoms, data_bonds = None, None
    with open(filename) as fp:
        line = next(fp)
        while line and not '@<TRIPOS>MOLECULE' in line:
            line = next(fp)
        assert line, "could not find MOLECULE tag"

        ##
        # get natoms and nbonds
        # -----------------------------------------------------------------------------
        # skip one line and get the next line
        _, line = next(fp), next(fp)
        natoms, nbonds = line.split()[:2]
        natoms, nbonds = int(natoms), int(nbonds)
        print("got {} atoms and {} bonds".format(natoms, nbonds))

        ##
        # read in atoms
        # -----------------------------------------------------------------------------
        while line and not "@<TRIPOS>ATOM" in line:
            line = next(fp)
        assert line, "could not find ATOM tag"

        # atom_id element_symbol, x, y, z
        data_atoms = (next(fp).split()[:5] for _ in range(natoms))
        # remove any numbers after element symbol: e.g. N39
        data_atoms = [(int(a), re.split('\d+', sym.capitalize())[0], (float(x), float(y), float(z))) for a, sym, x, y, z in data_atoms]

        ##
        # read in bonds
        # -----------------------------------------------------------------------------
        while line and not "@<TRIPOS>BOND" in line:
            line = next(fp)
        assert line, "could not find BOND tag"

        # atom1 atom2 bond_order
        data_bonds = (next(fp).split()[1:] for _ in range(nbonds))
        data_bonds = [(int(a1), int(a2), mol2_bond_orders[bo.lower()]) for a1, a2, bo in data_bonds]

    assert data_atoms, "no atoms data found!"
    assert data_bonds, "no bonds data found!"

    G = Graph()
    ##
    # store atom attributes in graph nodes
    # -----------------------------------------------------------------------------
    # map symbol and position
    nodes = ((atom_id, {'element':symbol,
                        "position":position}) for atom_id, symbol, position in data_atoms)
    # map bond order
    edges = ((atom_id1, atom_id2, {'weight': float(bo)}) for atom_id1, atom_id2, bo in data_bonds)
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

def get_symbols_from_graph(graph):
    """extract atomic symbols from graph node attributes"""

    syms = (sym for _, sym in graph.nodes(data='element'))
    return syms

def get_positions_from_graph(graph):
    """extract atomic positions from graph node attributes"""
    positions = (pos for _, pos in graph.nodes(data='position'))
    return positions

def get_atom_from_graph(graph, index):
    """get a atom from graph with index"""

    assert type(index) == int, index
    d = graph.nodes[index]
    return Atom(data=d)

def get_atoms_from_graph(graph):
    """extract atom objects from graph nodes"""

    atoms = []
    for index, d in graph.nodes(data=True):
        symbol, position = d.get('element'), d.get('position')
        assert symbol is not None and position is not None
        a = Atom(symbol, position, index=index)
        atoms.append(a)

    return atoms
# 1fe1da74-2e5f-4999-9e6b-ac674946a305 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::16beb290-95c4-4fdf-9510-5d2bdb0c560c][16beb290-95c4-4fdf-9510-5d2bdb0c560c]]
from collections import Mapping, Set

class AtomView(Mapping, Set):
    """A AtomView class to act as mol.atoms for a Molecule
    """
    __slots__ = '_nodes',

    def __init__(self, graph):
        self._nodes = graph._node

    # Mapping methods
    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def __getitem__(self, n):
        d = self._nodes[n]
        return Atom(data=d)

    # Set methods
    def __contains__(self, n):
        return n in self._nodes

    # AtomView method
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, tuple(self))
# 16beb290-95c4-4fdf-9510-5d2bdb0c560c ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::24dd16f2-0889-454d-8264-cc8838f72318][24dd16f2-0889-454d-8264-cc8838f72318]]
@attr.s()
class MolecularEntity(object):
    """repsents any singular entity, irrespective of its nature, in order
    to concisely express any type of chemical particle: atom,
    molecule, ion, ion pair, radical, radical ion, complex, conformer,
    etc.

    References
    ----------
    1. http://goldbook.iupac.org/M03986.html
    2. https://en.wikipedia.org/wiki/Molecular_entity


    Examples
    --------
    >>> M = Molecule()
    >>> M.add_atom(1, element="C", position=(0, 0, 0))
    >>> M.add_atoms_from([...])
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
        atoms = AtomView(self._graph)
        self.__dict__['atoms'] = atoms
        return atoms

    @property
    def bonds(self):
        pass

    def add_atom(self, index, *args, **kwargs):
        """add a atom into molecule. if the atom already exists,
        atomic attributes will be updated.

        Parameters
        ----------
        index: atomic index, 1-based
        """
        self._graph.add_node(index)
        atom = Atom(index=index, *args, **kwargs)
        # set a reference
        self._graph.nodes[index] = atom.data

    def remove_atom(self, index):
        """remove the indexed atom from molecule

        Parameters
        ----------
        index: atom index, int type, 1-based
        """
        assert type(index) is int, index
        self._graph.remove_node(index)

    def add_atoms_from(self):
        pass

    def remove_atoms_from(self, indices):
        """remove atoms by indices

        Parameters
        ----------
        indices: atom index, 1-based
        """
        self._graph.remove_nodes_from(indices)

    def add_bond(self):
        pass

    def remove_bond(self):
        pass

    def add_bonds_from(self):
        pass

    def remove_bonds_from(self):
        pass
# 24dd16f2-0889-454d-8264-cc8838f72318 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::c0a96813-be11-47c2-aee4-3d7cd7a39acf][c0a96813-be11-47c2-aee4-3d7cd7a39acf]]
Molecule = MolecularEntity
# c0a96813-be11-47c2-aee4-3d7cd7a39acf ends here
