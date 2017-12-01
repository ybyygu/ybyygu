# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f79546aa-456d-406d-9378-9e3223b608b4][f79546aa-456d-406d-9378-9e3223b608b4]]
from go import Molecule

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

    # update atom attributes
    mol.add_atom(1, element='Fe')
    assert len(mol.atoms) == 2
    assert mol.atoms[1].element == 'Fe'

    # iteration
    for x in mol.atoms:
        pass

    # remove atom
    mol.remove_atom(1)
    assert len(mol.atoms) == 1
    assert mol.atoms[2].element == "C"
    assert mol.atoms[2].index == 2

def test_molecule_reorder():
    mol = Molecule()
    mol.add_atom(1, element='H')
    mol.add_atom(5, element='Fe')
    mol.add_atom(2, element='H')
    assert mol.atoms[5].index == 5
    assert mol.atoms[5].element == 'Fe'

    mol.reorder()
    assert mol.atoms[3].element == "Fe"

def test_molecule_add_atoms_from():
    d = ((1, dict(element="H", position=(1, 1, 1))),
         (2, dict(element="C", position=(2, 2, 2)))
    )

    mol = Molecule()
    mol.add_atoms_from(d)
# f79546aa-456d-406d-9378-9e3223b608b4 ends here
