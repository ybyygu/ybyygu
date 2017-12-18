# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f79546aa-456d-406d-9378-9e3223b608b4][f79546aa-456d-406d-9378-9e3223b608b4]]
from go import Molecule
from go import BondOrder

def test_molecule_attributes():
    mol = Molecule()
    mol = Molecule(title='test', charge=1, multiplicity=0)
    assert mol.charge == 1
    assert mol.title == 'test'
    assert mol.multiplicity == 0

def test_molecule_add_atom():
    mol = Molecule('good')

    mol.add_atom(1, element="H")
    mol.add_atom(2, element='C', position=(1, 1, 1))
    assert len(mol.atoms) == 2

    # add atom
    assert mol.atoms[1].element == "H"
    assert mol.atoms[2].position.x == 1
    assert mol.atoms[1].index == 1

    assert 1 in mol.atoms
    assert 2 in mol.atoms

    # update atom attributes
    mol.add_atom(1, element='Fe')
    assert len(mol.atoms) == 2
    assert mol.atoms[1].element == 'Fe'

    # iteration
    for a in mol.atoms:
        assert a.element == "Fe"
        break

    # remove atom
    mol.remove_atom(1)
    assert len(mol.atoms) == 1
    assert mol.atoms[2].element == "C"
    assert mol.atoms[2].index == 2

def test_molecule_add_remove_atoms():
    mol = Molecule('test')
    d = {1: dict(element='H', position=(0, 0, 0)),
         2: dict(element='B', position=(1, 1, 1)),
         3: dict(element='Fe', position=(2, 2, 2))}

    mol.add_atoms_from(d)
    assert len(mol.atoms) == 3
    assert mol.atoms[2].element == "B"
    assert mol.atoms[3].element == "Fe"

    mol.remove_atoms_from((1,3))
    assert len(mol.atoms) == 1
    assert mol.atoms[2].element == "B"

def test_molecule_reorder():
    mol = Molecule()
    mol.add_atom(1, element='H')
    mol.add_atom(5, element='Fe')
    mol.add_atom(2, element='H')
    assert mol.atoms[5].index == 5
    assert mol.atoms[5].element == 'Fe'

    mol.reorder()
    assert mol.atoms[3].element == "Fe"

def test_molecule_atoms_iloc():
    mol = Molecule()
    mol.add_atom(1, element='H')
    mol.add_atom(5, element='Fe')
    mol.add_atom(2, element='H')
    mol.add_atom(3, element='B')
    assert mol.atoms.iloc[0].element == "H"
    assert mol.atoms.iloc[-1].element == "Fe"
    atoms = mol.atoms.iloc[:-1]
    assert atoms[-1].element == "B"

def test_molecule_add_bond():
    mol = Molecule('test')
    elements = ("H", "C", "C", "H")
    for i, e in enumerate(elements):
        mol.add_atom(i+1, element=e)
    mol.add_bond(1, 2)
    mol.add_bond(3, 4, 2.0)

    assert (1, 2) in mol.bonds
    assert (2, 1) in mol.bonds
    assert (3, 4) in mol.bonds

    assert len(mol.bonds) == 2
    b = mol.bonds[(1,2)]
    assert b.order == BondOrder.single
    b = mol.bonds[(3,4)]
    assert b.order == BondOrder.double

def test_molecule_add_bonds():
    mol = Molecule('test')
    elements = ("H", "C", "C", "H")
    for i, e in enumerate(elements):
        mol.add_atom(i+1, element=e)

    d = {
        (1, 2): dict(order=1),
        (3, 4): dict(order=2)
    }

    mol.add_bonds_from(d)
    assert len(mol.bonds) == 2
    b34 = mol.bonds[(3, 4)]
    b43 = mol.bonds[(4, 3)]
    assert b34 == b43
    assert b34.order == BondOrder.double
    assert b43.order == BondOrder.double
    assert b34.atom1.element.symbol == "C"
    assert b43.atom1.element.symbol == "H"

    for b in mol.bonds:
        assert b.order == BondOrder.single
        assert b.atom1.element.symbol == "H"
        assert b.atom2.element.symbol == "C"
        break
# f79546aa-456d-406d-9378-9e3223b608b4 ends here
