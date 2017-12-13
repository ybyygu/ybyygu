#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::66e4879d-9a1b-4038-925b-ae8b8d838935][66e4879d-9a1b-4038-925b-ae8b8d838935]]
#===============================================================================#
#   DESCRIPTION:  represents high level structures of a molecule
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2017-12-13 Wed 16:00>
#       UPDATED:  <2017-12-13 Wed 21:10>
#===============================================================================#
# 66e4879d-9a1b-4038-925b-ae8b8d838935 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::734e2c1f-0702-4f6f-87f4-b5edb83b125d][734e2c1f-0702-4f6f-87f4-b5edb83b125d]]
import itertools

from .atom import Atom
from .molecule import Molecule
# 734e2c1f-0702-4f6f-87f4-b5edb83b125d ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::36fca8f9-00bf-43e5-a717-a6a420eea614][36fca8f9-00bf-43e5-a717-a6a420eea614]]
class Group(object):
    """A defined linked collection of atoms or a single atom within a molecular entity. -- IUPAC GoldBook"""
    def __init__(self, parent, index, name, atoms):
        """
        Parameters
        ----------
        parent: parent molecule object
        """
        self._parent = parent
        self._name = name
        self._atoms = atoms
        self._index = index

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    @property
    def atoms(self):
        return self._atoms
# 36fca8f9-00bf-43e5-a717-a6a420eea614 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::b1292b17-4a1f-4816-b6f9-b152c01a9ae1][b1292b17-4a1f-4816-b6f9-b152c01a9ae1]]
class Substructure(object):
    GroupNameLabel  = ".subst/name"
    GroupIndexLabel = ".subst/index"

    @classmethod
    def set_name(cls, atom, name):
        """store substructure's name in atom's data dict

        :param atom: an instance of Atom object
        :param name: fragment name
        """
        assert isinstance(atom, Atom), "not a real atom: {}".format(atom)

        atom.data[cls.GroupNameLabel] = name

    @classmethod
    def get_name(cls, atom):
        """get substructure's name from atom's data

        Returns
        --------
        return substructure's name stored in atom. return None if failed to get
        """
        assert isinstance(atom, Atom), "not a real atom: {}".format(atom)
        name = atom.data.get(cls.GroupNameLabel)
        return name

    @classmethod
    def get_index(cls, atom):
        """get substructure's index from atoms's data

        return None if failed
        """

        assert isinstance(atom, Atom), "not a real atom: {}".format(atom)
        index = atom.data.get(cls.GroupIndexLabel)
        return index

    @classmethod
    def set_index(cls, atom, index):
        """store substructure index in atom's data"""

        assert isinstance(atom, Atom), "not a real atom: {}".format(atom)
        atom.data[cls.GroupIndexLabel] = index

    @classmethod
    def define(cls, atoms, name):
        """name atoms as substructure `name'

        Parameters
        ----------
        atoms: iterable containers of Atom instances
        name : substructure name in str type
        """

        for a in atoms:
            a.data[cls.GroupNameLabel] = name

    @classmethod
    def extract(cls, molecule):
        """extract substructures from molecule"""
        d = {}

        for a in molecule.atoms:
            name = a.data.get(cls.GroupNameLabel)
            if name:
                d.setdefault(name, []).append(a)

        groups = []
        ic = itertools.count(1)
        for name, atoms in d.items():
            group = Group(parent=molecule, name=name, index=next(ic), atoms=atoms)
            groups.append(group)
        return groups

class Frozen(Substructure):
    GroupNameLabel  = ".frozen/name"
    GroupIndexLabel = ".frozen/index"
# b1292b17-4a1f-4816-b6f9-b152c01a9ae1 ends here
