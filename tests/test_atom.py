# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::9be685e3-d7fd-4bae-bf51-3b9de9cf3634][9be685e3-d7fd-4bae-bf51-3b9de9cf3634]]
from go import Point3D, Coord, Atom

def test_point3d():
    p1 = Point3D(1, 2, 3)
    assert p1.x == 1 and p1.y == 2 and p1.z == 3

    p2 = Point3D(x=1, y=2, z=3)
    assert p1 == p2

    x, y, z = p1
    assert x == 1 and y == 2 and z == 3

def test_atom_init():
    a = Atom()
    assert a.element == "X"

    a = Atom('H')
    assert a.element == "H"
    assert a.element.symbol == "H"
    assert a.element.number == 1

    a = Atom('H', (1,1,1))
    assert a.position.x == 1

    a = Atom(position=(1,1,1))
    assert a.position.x == 1
    assert a.element == "X"

    a = Atom(element="H")
    assert a.element == "H"

    a = Atom(element=1)
    assert a.element == "H"

    d = dict(element="H", name="H12", index=12)
    a = Atom(data=d)
    assert a.element == "H"
    assert a.name == "H12"
    assert a.index == 12
    a = Atom(element="C", data=d)
    assert a.element == "C"

    a = Atom(data=d, name="H13")
    assert a.name == "H13"
    a.name = "H14"
    assert a.name == "H14"

    pos = Coord(1.0, 2.3, 8.9, unit='bohr')
    a = Atom("H", pos)
    assert a.position.x == 0.529177

    a.position = (1, 1, 1)
    assert a.position.x == 1

    a.position = Coord(1, 1, 1)
    assert a.position.x == 1

def test_atom_conversion():
    d = dict(element=12, index=9, position=(1.2, 1.1, 1.0))
    a = Atom()
    a.update(d)
    id1 = id(a)
    assert a.data['index'] == 9
    assert a.index == 9
    assert a.element == "Mg"

    d['index'] = 10
    assert a.index == 9

    b = Atom(index=1, name='good')
    a.update(b, other=4, name='ok')
    assert a.index == 1
    assert a.name == 'ok'
    assert a.data['other'] == 4


    dd = a.to_dict()
    assert dd['name'] == 'ok'
    assert id1 != id(dd)
# 9be685e3-d7fd-4bae-bf51-3b9de9cf3634 ends here
