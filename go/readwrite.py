#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::66e4879d-9a1b-4038-925b-ae8b8d838935][66e4879d-9a1b-4038-925b-ae8b8d838935]]
#===============================================================================#
#   DESCRIPTION:  basic read & write support for molecular file
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2017-12-14 Thu 10:19>
#       UPDATED:  <2017-12-17 Sun 16:53>
#===============================================================================#
# 66e4879d-9a1b-4038-925b-ae8b8d838935 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::54026ccd-add6-46eb-be92-7494d4ab742a][54026ccd-add6-46eb-be92-7494d4ab742a]]
import itertools
import re

from .molecule import Molecule

__all__ = ["from_xyzfile", "from_coordfile", "from_mol2file", "to_xyzfile", "to_mol2file"]
# 54026ccd-add6-46eb-be92-7494d4ab742a ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1][f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1]]
def from_xyzfile(filename):
    """a quick and dirty way to create a molecule from xyz file

    Parameter
    ---------
    filename: path to a xyz file

    Reference
    ---------
    https://en.wikipedia.org/wiki/XYZ_file_format
    """

    with open(filename) as fp:
        # line = '' or line = '\n'
        line = fp.readline().strip()
        assert line, line
        na = int(line)
        title = fp.readline().strip()
        ic = itertools.count(start=1)
        mol = Molecule(title)
        for _ in range(na):
            line = fp.readline()
            sym, x, y, z = line.split()
            mol.add_atom(index=next(ic), element=sym, position=(float(x), float(y), float(z)))
        return mol

def from_coordfile(filename):
    """create a molecule from plain coordinates file"""
    with open(filename) as fp:
        mol = Molecule("from {}".format(filename))
        ic = itertools.count(start=1)
        for line in fp:
            sym, x, y, z = line.split()[:4]
            mol.add_atom(index=next(ic), element=sym, position=(float(x), float(y), float(z)))
        return mol
# f7d75dd8-16e3-47b4-aa7b-70e3ce06f2f1 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::6b83e92c-fd6c-42a4-8723-13f3b89a54f8][6b83e92c-fd6c-42a4-8723-13f3b89a54f8]]
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

def from_mol2file(filename, trajectory=False):
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
        # print("got {} atoms and {} bonds".format(natoms, nbonds))

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

    ##
    # store atom attributes in graph nodes
    # -----------------------------------------------------------------------------
    # map symbol and position
    atoms = {index: {'element':symbol, "position":position} for index, symbol, position in data_atoms}
    # map bond order
    bonds = {(index1, index2): {'order': float(bo)} for index1, index2, bo in data_bonds}
    mol = Molecule()
    mol.add_atoms_from(atoms)
    mol.add_bonds_from(bonds)
    return mol
# 6b83e92c-fd6c-42a4-8723-13f3b89a54f8 ends here
