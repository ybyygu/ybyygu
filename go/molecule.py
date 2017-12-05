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
#       UPDATED:  <2017-12-05 Tue 08:54>
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

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::02cb9c34-f76b-4e6c-8411-9e55ef729274][02cb9c34-f76b-4e6c-8411-9e55ef729274]]
class _IlocWrapper(object):
    """positional indexing support for AtomsView object.

    Adopted from: https://github.com/grantjenks/sorted_containers/blob/master/sortedcontainers/sorteddict.py
    """
    __slots__ = ("_view")

    def __init__(self, view):
        self._view = view

    def __len__(self):
        return len(self._view)

    def __getitem__(self, index):
        """return the key at index *index* in iteration. Supports negative indices
        and slice notation. Raises IndexError on invalid *index*.
        """
        d = self._view._mapping_nodes
        indices = (k for k in sorted(d.keys()))

        if not isinstance(index, slice):
            if index < 0:
                maxn = len(self._view)
                index += maxn
            k = next(itertools.islice(indices, index, index+1))
            return self._view[k]

        # negative stop
        start, stop = index.start, index.stop
        if stop is not None and stop < 0 :
            maxn = len(self._view)
            stop += maxn
            print(maxn, start, stop)
        print(start, stop)

        selected = itertools.islice(indices, start, stop, index.step)
        return [self._view[k] for k in selected]
# 02cb9c34-f76b-4e6c-8411-9e55ef729274 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::b01be335-9caa-42b7-aa35-38fddebfc2b9][b01be335-9caa-42b7-aa35-38fddebfc2b9]]
class AtomsView(KeysView):
    """An AtomsView class to act as molecule.atoms for a Molecule instance

    Parameters
    ----------
    AtomsView(molecule._graph)

    Examples
    --------
    >>> atoms[5]
    >>> len(atoms)
    >>> atoms.iloc[1:5]
    >>> atoms.iloc[-1]
    >>> atoms.iloc[:-1]
    """

    __slots__ = ("_mapping", "_mapping_nodes", "iloc")

    def __init__(self, graph):
        self._mapping_nodes = graph.graph['indices']  # mapping index ==> atom.id
        self._mapping = graph._node       # graph.add_node(atom.id, ...)
        self.iloc = _IlocWrapper(self)

    def __iter__(self):
        yield from (self[k] for k in self._mapping_nodes)

    def __getitem__(self, n):
        atom_id = self._mapping_nodes[n]
        atom = Atom(data=self._mapping[atom_id])
        return atom

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, tuple(self._mapping_nodes.keys()))
# b01be335-9caa-42b7-aa35-38fddebfc2b9 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::a04302b0-282b-4af1-aa0b-aa30df4faf87][a04302b0-282b-4af1-aa0b-aa30df4faf87]]
class BondsView(KeysView):
    """A BondsView class to act as molecule.bonds for a Molecule instance

    Parameters
    ----------
    BondsView(molecule._graph)

    Examples
    --------
    >>> bonds[(1, 2)]
    >>> len(bonds)
    """

    __slots__ = ("_mapping", "_mapping_nodes")

    def __init__(self, graph):
        self._mapping = graph.edges
        self._mapping_nodes = graph.graph['indices']  # mapping index ==> atom.id

    def __iter__(self):
        yield from (self[e] for e in self._mapping)

    def __getitem__(self, e):
        u, v = e
        atom_id1, atom_id2 = self._mapping_nodes[u], self._mapping_nodes[v]
        d = self._mapping[(atom_id1, atom_id2)]
        bond = Bond(atom_id1, atom_id2, order=d.get('order', 1))
        return bond

    def __contains__(self, e):
        u, v = e
        e = self._mapping_nodes[u], self._mapping_nodes[v]
        return e in self._mapping

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, tuple(self._mapping.keys()))
# a04302b0-282b-4af1-aa0b-aa30df4faf87 ends here

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

    __slots__ = ("_graph", "_atoms", "_bonds", "_mapping_nodes")

    def __init__(self, title="molecular entity", charge=0, multiplicity=1):
        # core structure: networkx Graph
        self._graph = Graph(title=title, charge=charge, multiplicity=multiplicity, indices={})
        self._mapping_nodes = self._graph.graph['indices']  # mapping atomic index to atom instance id

        self._atoms = AtomsView(self._graph)
        self._bonds = BondsView(self._graph)

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
        return self._bonds

    @property
    def formula(self):
        """the brute formula of the Molecule. i.e. 'H2O'"""

        symbols = tuple(a.element.symbol for a in self.atoms)
        return get_reduced_formula(symbols)

    def add_atom(self, index, *args, **kwargs):
        """add a atom into molecule. if the atom already exists,
        atomic attributes will be updated.

        Parameters
        ----------
        index: atomic index, 1-based
        """
        atom_id = self._mapping_nodes.get(index)
        atom = Atom(index=index, *args, **kwargs)
        if atom_id is None:
            atom_id = atom.id
            self._mapping_nodes[index] = atom_id
        self._graph.add_node(atom_id, **atom.data)

    def add_atoms_from(self, atoms):
        """add multiple atoms.

        Parameters
        ----------
        atoms: dict of dict type, key: atom index, value: dict of atom data
        """
        assert type(atoms) is dict, atoms
        assert len(atoms) > 0, atoms

        nodes = {}
        mapping = self._mapping_nodes
        for index, d in atoms.items():
            atom_id = mapping.get(index)
            atom = Atom(index=index, data=d)
            print(atom.data)
            if atom_id is None:
                atom_id = atom.id
                mapping[index] = atom_id
            nodes[atom_id] = atom.data
        self._graph.add_nodes_from(nodes.items())

    def remove_atom(self, index):
        """remove the atom *index* from molecule

        Parameters
        ----------
        index: atom index, int type, 1-based
        """
        assert type(index) is int, index
        atom_id = self._mapping_nodes.get(index)
        if atom_id:
            self._mapping_nodes.pop(index)
            self._graph.remove_node(atom_id)
        else:
            raise KeyError("index not found: {}".format(index))

    def remove_atoms_from(self, indices):
        """remove atoms by indices

        Parameters
        ----------
        indices: iterable atom indices, 1-based
        """
        atom_ids = (self._mapping_nodes[x] for x in indices)
        self._graph.remove_nodes_from(atom_ids)

    def reorder(self):
        """reorder the atoms by renumbering atomic index attributes"""

        ic = itertools.count(start=1)
        new_indices = {}
        for k in sorted(self._mapping_nodes.keys()):
            index = next(ic)
            node = self._mapping_nodes[k]
            new_indices[index] = node
            self._graph.nodes[node]['index'] = index

        # update indices
        self._mapping_nodes.clear()
        self._mapping_nodes.update(new_indices)

    def add_bond(self, index1, index2, order=1):
        """Add a bond between two atoms.

        Parameters
        ----------
        index1, index2: atom indices of atom1 and atom2
        order: bond order

        Raises
        ------
        If there is no atom index1 or index2 in molecule, raise KeyError.
        """
        n1, n2 = self._mapping_nodes[index1], self._mapping_nodes[index2]
        self._graph.add_edge(n1, n2, order=order)

    def add_bonds_from(self, bonds):
        """add bonds in molecule

        Parameters
        ----------
        bonds: iterable container of bonds

        Example
        -------
        >>> mol.add_bonds_from({(1,2):{order=1}, (2,3):{order=2}})
        """
        edges = {}
        for e, d in bonds.items():
            u, v = e
            atom_id1, atom_id2 = self._mapping_nodes[u], self._mapping_nodes[v]
            edges[(atom_id1, atom_id2)] = Bond(atom_id1, atom_id2, d.get('order', 1))
        self._graph.add_edges_from(edges.items())

    def remove_bond(self, index1, index2):
        """remove a bond between two atoms

        Parameters
        ----------
        index1, index2: atom indices of atom1 and atom2

        Raises
        ------
        If there is no atom *index1* or *index2* in molecule, raise KeyError
        If there is no bond between *index1* and *index2*, raise NetworkXError
        """
        n1, n2 = self._mapping_nodes[index1], self._mapping_nodes[index2]
        self._graph.remove_edge(n1, n2)


    def remove_bonds_from(self, bonds):
        """remove all specified bonds

        Parameters
        ----------
        bonds: iterable container of bonds (in tuple)

        Example
        -------
        >>> mol.remove_bonds_from([(1,2), (2,3)])
        """
        for b in bonds:
            self.remove_bonds(*b)
# 24dd16f2-0889-454d-8264-cc8838f72318 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::c0a96813-be11-47c2-aee4-3d7cd7a39acf][c0a96813-be11-47c2-aee4-3d7cd7a39acf]]
Molecule = MolecularEntity
# c0a96813-be11-47c2-aee4-3d7cd7a39acf ends here
