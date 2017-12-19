#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::53ee220f-ad71-4c35-9ec2-1fcae345257e][53ee220f-ad71-4c35-9ec2-1fcae345257e]]
from pathlib import Path

import go.readwrite as rw

txt_xyz = """12
Molecule 1  0.000000
C -11.4286  1.7645  0.0000
C -10.0949  0.9945  0.0000
C -10.0949 -0.5455  0.0000
C -11.4286 -1.3155  0.0000
C -12.7623 -0.5455  0.0000
C -12.7623  0.9945  0.0000
H -11.4286  2.8545  0.0000
H -9.1509  1.5395  0.0000
H -9.1509 -1.0905  0.0000
H -11.4286 -2.4055  0.0000
H -13.7062 -1.0905  0.0000
H -13.7062  1.5395  0.0000
"""


def test_xyzfile_readwrite(tmpdir):
    xyzfile = Path(tmpdir).joinpath('test.xyz')
    with open(xyzfile, "w") as fp:
        fp.write(txt_xyz)

    mol = rw.from_xyzfile(xyzfile)
    assert mol.atoms[1].element == "C"
    assert mol.atoms[2].position.x == -10.0949

    mol.atoms[1].position = (9, 9, 9)

    rw.to_xyzfile(mol, xyzfile)
    with open(xyzfile) as fp:
        fp.readline()
        fp.readline()
        line = fp.readline()
        attrs = line.split()
        assert float(attrs[1]) == 9.

txt_mol2 = """@<TRIPOS>MOLECULE
mol1
16 15
SMALL
NO_CHARGES


@<TRIPOS>ATOM
1 C1     0.0000     0.0000     0.0000 C
2 O2     0.0000     0.0000     1.2115 O
3 C3     1.3022     0.0000    -0.7974 C
4 H4     1.4501     1.0258    -1.1586 H
5 H5     1.1812    -0.6252    -1.6860 H
6 C6    -1.2802     0.0121    -0.8050 C
7 H7    -1.2233     0.7254    -1.6324 H
8 H8    -1.4261    -0.9809    -1.2440 H
9 H9    -2.1271     0.2465    -0.1614 H
10 C10     2.5086    -0.4393     0.0227 C
11 C11     2.4919    -1.9222     0.3156 C
12 H12     2.5504     0.0939     0.9749 H
13 H13     3.4434    -0.2201    -0.5033 H
14 O14     1.7263    -2.7265    -0.1554 O
15 O15     3.4769    -2.2706     1.1763 O
16 H16     3.4112    -3.2272     1.3165 H
@<TRIPOS>BOND
1 1 3 1
2 1 6 1
3 1 2 2
4 3 5 1
5 3 4 1
6 3 10 1
7 6 7 1
8 6 8 1
9 6 9 1
10 10 13 1
11 10 11 1
12 10 12 1
13 11 14 2
14 11 15 1
15 15 16 1
"""

def test_mol2file_readwrite(tmpdir):
    mol2file = Path(tmpdir).joinpath('test.mol2')
    with open(mol2file, "w") as fp:
        fp.write(txt_mol2)

    mol = rw.from_mol2file(mol2file)
    assert len(mol.atoms) == 16
    assert mol.atoms[1].element == "C"
    b = mol.bonds[(1, 3)]
    assert b.order.value == 1.
    assert len(mol.bonds) == 15

    # writing
    mol.remove_bond(15, 16)
    rw.to_mol2file(mol, mol2file)
    mol2 = rw.from_mol2file(mol2file)
    assert len(mol2.bonds) == 14
# 53ee220f-ad71-4c35-9ec2-1fcae345257e ends here
