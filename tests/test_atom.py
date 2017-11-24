# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::9be685e3-d7fd-4bae-bf51-3b9de9cf3634][9be685e3-d7fd-4bae-bf51-3b9de9cf3634]]
from go import Point3D, Coord, Atom

def test_point3d():
    p1 = Point3D(1, 2, 3)
    assert p1.x == 1 and p1.y == 2 and p1.z == 3

    p2 = Point3D(x=1, y=2, z=3)
    assert p1 == p2

    x, y, z = p1
    assert x == 1 and y == 2 and z == 3

def test_atom():
    a = Atom()
    assert a.element == "C"

    a = Atom('H')
    assert a.element == "H"
    assert a.element.symbol == "H"
    assert a.element.number == 1

    a = Atom('H', (1,1,1))
    assert a.position.x == 1

    a = Atom(position=(1,1,1))
    assert a.position.x == 1

    pos = Coord(1.0, 2.3, 8.9, unit='bohr')
    a = Atom("H", pos)
    assert a.position.x == 0.529177

    a.position = (1, 1, 1)
    assert a.position.x == 1

    a.position = Coord(1, 1, 1)
    assert a.position.x == 1

    assert a.index == 0
    assert a.name == "H0"

    a.name = "H12"
    assert a.name == "H12"

    a.index = 12
    assert a.index == 12
# 9be685e3-d7fd-4bae-bf51-3b9de9cf3634 ends here
