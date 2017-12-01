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
#       UPDATED:  <2017-11-30 Thu 16:38>
#===============================================================================#
# 66e4879d-9a1b-4038-925b-ae8b8d838935 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024][3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024]]
import itertools

from collections import namedtuple, Counter, OrderedDict, KeysView
from functools import lru_cache  # required python >= 3.2

from .lib import graph
from .atom import Atom

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

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::b01be335-9caa-42b7-aa35-38fddebfc2b9][b01be335-9caa-42b7-aa35-38fddebfc2b9]]
class AtomsView(KeysView):
    """A AtomsView class to act as molecule.atoms for a Molecule instance

    Parameters
    ----------

    Examples
    --------
    """

    __slots__ = ("_mapping", "_mapping_nodes")

    def __init__(self, graph):
        self._mapping = graph.graph['indices']  # mapping index ==> atom.id
        self._mapping_nodes = graph._node       # graph.add_node(atom.id, ...)

    def __getitem__(self, n):
        atom_id = self._mapping[n]
        atom = Atom(data=self._mapping_nodes[atom_id])
        return atom

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, tuple(self._mapping.keys()))
# b01be335-9caa-42b7-aa35-38fddebfc2b9 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::24dd16f2-0889-454d-8264-cc8838f72318][24dd16f2-0889-454d-8264-cc8838f72318]]
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

    __slots__ = ("_graph", "_atoms", "_mapping")

    def __init__(self, title="molecular entity", charge=0, multiplicity=1):
        # core structure: networkx Graph
        self._graph = Graph(title=title, charge=charge, multiplicity=multiplicity, indices={})
        self._atoms = AtomsView(self._graph)
        self._mapping = self._graph.graph['indices']  # mapping atomic index to atom instance id

    @property
    def charge(self):
        return self._graph.graph.get('charge', 0)

    @charge.setter
    def charge(self, value):
        self._graph.graph['charge'] = value

    @property
    def multiplicity(self):
        return self._graph.graph.get('multiplicity', 1)

    @multiplicity.setter
    def multiplicity(self, value):
        self._graph.graph['multiplicity'] = value

    @property
    def title(self):
        return self._graph.graph.get('title')

    @title.setter
    def title(self, value):
        self._graph.graph['title'] = value

    @property
    def atoms(self):
        return self._atoms

    @property
    def bonds(self):
        return self._graph.edges()

    def add_atom(self, index, *args, **kwargs):
        """add a atom into molecule. if the atom already exists,
        atomic attributes will be updated.

        Parameters
        ----------
        index: atomic index, 1-based
        """
        atom_id = self._mapping.get(index)
        atom = Atom(index=index, *args, **kwargs)
        if atom_id is None:
            atom_id = atom.id
            self._mapping[index] = atom_id
        self._graph.add_node(atom_id, **atom.data)

    def remove_atom(self, index):
        """remove the indexed atom from molecule

        Parameters
        ----------
        index: atom index, int type, 1-based
        """
        assert type(index) is int, index
        atom_id = self._mapping.get(index)
        if atom_id:
            self._mapping.pop(index)
            self._graph.remove_node(atom_id)
        else:
            raise KeyError("index not found: {}".format(index))

    def reorder(self):
        """reorder the atoms by renumbering atomic index attributes"""

        ic = itertools.count(start=1)
        new_indices = {}
        for k in sorted(self._mapping.keys()):
            index = next(ic)
            node = self._mapping[k]
            new_indices[index] = node
            self._graph.nodes[node]['index'] = index

        # update indices
        self._mapping.clear()
        self._mapping.update(new_indices)


    def add_atoms_from(self, atoms):
        """add multiple atoms.

        Parameters
        ----------
        atoms: iterable container of (index, dict) tuples
        """
        assert len(atoms) > 0, atoms
        assert len(atoms[0]) == 2, atoms[0]

    def remove_atoms_from(self, indices):
        """remove atoms by indices

        Parameters
        ----------
        indices: atom index, 1-based
        """
        atom_ids = (self._mapping[x] for x in indices)
        raise NotImplementedError

    def add_bond(self, index1, index2):
        pass

    def remove_bond(self, index1, index2):
        pass

    def add_bonds_from(self):
        pass

    def remove_bonds_from(self):
        pass
# 24dd16f2-0889-454d-8264-cc8838f72318 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::c0a96813-be11-47c2-aee4-3d7cd7a39acf][c0a96813-be11-47c2-aee4-3d7cd7a39acf]]
Molecule = MolecularEntity
# c0a96813-be11-47c2-aee4-3d7cd7a39acf ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1][f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1]]
def molecule_from_xyzfile(filename):
    """a quick and dirty way to create molecule graph from xyz file"""

    ic = itertools.count(start=1)
    mol = Molecule('origin file: {}'.format(filename))
    with open(filename) as fp:
        for line in fp:
            attrs = line.split()
            if len(attrs) == 4:
                symbol, x, y, z = attrs
                position = [float(a) for a in (x, y, z)]
                mol.add_atom(index=next(ic), element=symbol, position=position)
    return mol
# f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::6b83e92c-fd6c-42a4-8723-13f3b89a54f8][6b83e92c-fd6c-42a4-8723-13f3b89a54f8]]
import re

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
# 6b83e92c-fd6c-42a4-8723-13f3b89a54f8 ends here
