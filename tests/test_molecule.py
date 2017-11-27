# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f79546aa-456d-406d-9378-9e3223b608b4][f79546aa-456d-406d-9378-9e3223b608b4]]
from go import Molecule

def test_molecule():
    mol = Molecule()
    mol = Molecule(title='test', charge=1, multiplicity=0)
    assert mol.charge == 1

    for x in mol.atoms:
        pass

    mol.add_atom(1, element="H")

    assert len(mol.atoms) == 1

    d = ((1, dict(element="H", position=(1, 1, 1))),
         (2, dict(element="C", position=(2, 2, 2)))
    )
    mol.add_atoms_from(d)
    assert len(mol.atoms) == 2
# f79546aa-456d-406d-9378-9e3223b608b4 ends here
