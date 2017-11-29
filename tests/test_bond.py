# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::bd6eb98c-99c7-4722-9cf3-a7747d6be795][bd6eb98c-99c7-4722-9cf3-a7747d6be795]]
from go import Atom
from go import Bond, BondOrder

def test_bond():
    a1 = Atom("C", (-3.3383459, 0.6842105, 0.0000000))
    a2 = Atom("H", (-2.9816914, -0.3245995, 0.0000000))

    # initialize with default bond order
    b = Bond(a1, a2)
    assert b.order == BondOrder.single
    b = Bond(a1, a2, order=2)
    assert b.order == BondOrder.double
    # unpack bond
    a1, a2, bo = b
    assert bo == BondOrder.double
    assert a1.element == "C"

    assert b.atom1.element == "C"
    assert b.atom2.element == "H"

    # atom1, atom2 in bond are bounded references
    a1.element = "Si"
    assert b.atom1.element == "Si"
# bd6eb98c-99c7-4722-9cf3-a7747d6be795 ends here
