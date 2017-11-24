#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::ba7b02d8-af81-4e53-8695-833d9b411246][ba7b02d8-af81-4e53-8695-833d9b411246]]
from go import Element

def test_element():
    assert Element('H') == Element(1) == Element.hydrogen == "H"
    assert Element('H').symbol == "H"
    assert Element('H').number == 1
    assert Element.hydrogen.number == 1
    assert Element.hydrogen.symbol == "H"
# ba7b02d8-af81-4e53-8695-833d9b411246 ends here
