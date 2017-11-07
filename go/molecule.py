#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024][3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024]]
#===============================================================================#
#   DESCRIPTION:  GO: a Graph-based chemical Objects library
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2006-08-30 Wed 16:51>
#       UPDATED:  <2017-11-03 Fri 16:51>
#===============================================================================#

import attr

from collections import namedtuple, Counter, OrderedDict
from itertools import count

from .atom import Atom, Element
from .bond import BondOrder, Bond, guess_bonds
from gosh.graph import Graph
from gosh.logger import get_logger

logger = get_logger(__name__)

class OrderedGraph(Graph):
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict

@attr.s(slots=True)
class Properties(object):
    """store molecular properties"""

    energy = attr.ib(default=None)
    dipole = attr.ib(default=True)
    gradients = attr.ib(default=attr.Factory(list))
    force_constants = attr.ib(default=attr.Factory(list))
    polarizability = attr.ib(default=attr.Factory(list))
    polarizability_derivatives = attr.ib(default=attr.Factory(list))

    # APTs
    dipole_derivatives = attr.ib(default=attr.Factory(list))
    # AATs
    atomic_axial_tensors = attr.ib(default=attr.Factory(list))

    # any other properties
    others = attr.ib(default=attr.Factory(dict))

@attr.s(slots=True)
class MolecularEntity(object):
    """repsents any singular entity, irrespective of its nature, in order
    to concisely express any type of chemical particle: atom,
    molecule, ion, ion pair, radical, radical ion, complex, conformer,
    etc.

    Reference
    ---------
    1. http://goldbook.iupac.org/M03986.html
    2. https://en.wikipedia.org/wiki/Molecular_entity
    """
    # for maintaining atoms' order
    _atoms = attr.ib(default=attr.Factory(list), init=False)

    # core structure: networkx Graph
    _graph = attr.ib(default=attr.Factory(OrderedGraph), init=False)

    # the title for molecule/atoms
    title = attr.ib(default="molecular entity", validator=attr.validators.instance_of(str))

    # for crystal data with periodic boundary condition(PBC)
    cell = attr.ib(default=None)

    # molecular charge
    charge = attr.ib(default=0, init=False)

    # molecular multiplicy
    multiplicity = attr.ib(default=1, init=False)

    # store molecule properties such as energy, gradients
    properties = attr.ib(default=attr.Factory(Properties), init=False)

    ##
    # general interfaces
    # --------------------------------------------------------------------
    @property
    def atoms(self):
        return self._atoms

    @atoms.setter
    def atoms(self, _atoms):
        # reset graph
        self._atoms = _atoms
        self._graph = OrderedGraph()
        self._store_atoms_in_graph(_atoms)
        self.reorder()

    @property
    def bonds(self):
        return self._get_bonds()

    @property
    def electrons(self):
        """return the counts of total electrons in molecule"""

        electrons = 0
        for a in self.atoms:
            electrons += a.element.number
        electrons -= self.charge
        return electrons

    @property
    def formula(self):
        return self._get_reduced_formula()

    def __str__(self):
        """output xyz coordinates"""

        lines = ["%s" % a for a in self.atoms]
        return "\n".join(lines)

    def get_reduced_formula(self):
        """return chemical formula: C2H4"""

        reduced = Counter([a.element.symbol for a in self.atoms]) # [("H", 4), ("C", 1)]

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

    ##
    # manipulation atoms
    # --------------------------------------------------------------------
    def get_atom(self, index):
        """get atom by index

        :param index: atom index is an integer counting from 1
        """
        assert index <= len(self._atoms), "atom index out of range"
        return self._atoms[index-1]

    def reorder(self):
        """rename the indices of atoms to match their order in atom list"""
        ic = count(start=1)
        for a in self._atoms:
            a.index = next(ic)

    def remove_atom(self, atom):
        """remove atom from molecule and all its related bonds

        :param index: an integer of atom index

        Example
        -------
        >>> molecule.remove(atom)
        """

        assert isinstance(atom, Atom), "{} is not a real atom".format(atom)
        assert atom in self.atoms, "{} is not in molecule".format(atom)

        self._remove_atoms_from_graph([atom])

    def __len__(self):
        """return the count of atoms"""
        return len(self._atoms)

    def _get_atoms_from_graph(self):
        """get atoms from graph"""
        atoms = list(self._graph)
        return atoms

    def _from_atoms(self, atoms):
        """construct Molecule from atom list

        :param atoms: [atom1, atom2, ... ]
        """
        self._store_atoms_in_graph(atoms)

    def _from_graph(self, graph):
        """construct Molecule from graph"""

        assert isinstance(graph, Graph), "{} is not instanced from Graph".format(graph)

        self.title = graph.name
        self._graph = graph     # FIXME: copy or not?

    def _store_atoms_in_graph(self, atoms):
        """store atoms as graph nodes"""

        self._graph.add_nodes_from(atoms)
        assert len(atoms) == self._graph.order(), "atoms were not correctly stored."

    def _remove_atoms_from_graph(self, atoms):
        """remove atom nodes from graph"""
        self._graph.remove_nodes_from(atoms)

    ##
    # manipulation bonds
    # --------------------------------------------------------------------
    def bond(self, atom1, atom2, order=1.0):
        """define bond between atom1 and atom2

        Parameters
        ----------
        atom1, atom2: an instance of Atom or an index of in int
        order: bond order

        Example
        -------
        bond atom 1 and 2:
        >>> mol.bond(1, 2)
        """
        if isinstance(atom1, int):
            atom1 = self.get_atom(atom1)
        if isinstance(atom2, int):
            atom2 = self.get_atom(atom2)

        bond = Bond(atom1, atom2, order)
        self._store_bonds_in_graph([bond])

    def rebond(self, atoms=None):
        """detect bonds based on predefined bonding lengths"""
        bonds = guess_bonds(self._atoms)
        self._store_bonds_in_graph(bonds)

    def unbond(self, atoms=None):
        """removes all bonds between atoms"""
        if atoms is None:
            bonds = self._get_bonds_from_graph()
        else:
            bonds = [Bond(a, b) for a in atoms for b in self._graph[a]]
        self._remove_bonds_from_graph(bonds)

    def adjacent(self, atom1):
        """return bonds connected to atom1

        :param atom1: an instance of Atom or an index in int

        Return
        ------
        [(atom1, atom2, bond_order), ....]
        """

        if isinstance(atom1, int):
            atom1 = self.Atom(atom1)

        # pick up edge data connected with node
        # d = {<Atom>: {weight=BondOrder.single}, <Atom>: {weight=BondOrder.single}, ...}
        d = self._graph[atom1]
        bonds = []
        for atom2, b in d.items():
            bonds.append(Bond(atom1, atom2, b["weight"]))
        return bonds

    def _store_bonds_in_graph(self, bonds):
        """store bonds as graph edges"""
        self._graph.add_weighted_edges_from(bonds)

    def _get_bonds(self):
        """get bonds from graph edges"""
        bonds = []
        for a1, a2, order in self._graph.edges(data="weight"):
            bonds.append(Bond(a1, a2, order))
        return bonds

    def _remove_bonds(self, bonds):
        """remove bonds from graph edges"""
        _bonds = [(a, b) for a, b, _ in bonds]
        self._graph.remove_nodes_from(_bonds)


##
# convenient function for making molecule
# --------------------------------------------------------------------
def Molecule(atoms=[], *, title="", cell=None, charge=0, multiplicity=1):
    """
    Example
    -------
    initialize atoms
    >>> mol = Molecule(atoms)

    set atoms attribute
    >>> mol.atoms = [a1, a2, ...]

    add a single atom
    >>> mol.add_atom(("H", (1.0, 1.0, 1.0)))

    set molecular properties
    >>> mol.properties.energy = 0.1

    Notes
    -----
    user-visible entry points:
    0. molecule.title
    1. molecule.rebond
    2. molecule.unbond
    3. molecule.formula
    4. molecule.atoms
    """

    mol = MolecularEntity(title=title, cell=cell)
    mol.charge = charge
    mol.multiplicity = multiplicity
    mol.atoms = atoms
    return mol
# 3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024 ends here
