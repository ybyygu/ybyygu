#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::66e4879d-9a1b-4038-925b-ae8b8d838935][66e4879d-9a1b-4038-925b-ae8b8d838935]]
#===============================================================================#
#   DESCRIPTION:  molecular entity repsented by networkx graph object
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2017-11-21 Tue 16:00>
#       UPDATED:  <2017-11-21 Tue 17:16>
#===============================================================================#
# 66e4879d-9a1b-4038-925b-ae8b8d838935 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024][3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024]]
from collections import namedtuple, Counter, OrderedDict
from itertools import count

from .lib import graph
from .lib import attr

Graph = graph.OrderedGraph
# 3c5dcd20-6b5f-45f8-b7f0-a90acd3d9024 ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::24dd16f2-0889-454d-8264-cc8838f72318][24dd16f2-0889-454d-8264-cc8838f72318]]
@attr.s(slots=True)
class MolecularEntity(object):
    """repsents any singular entity, irrespective of its nature, in order
    to concisely express any type of chemical particle: atom,
    molecule, ion, ion pair, radical, radical ion, complex, conformer,
    etc.

    References
    ----------
    1. http://goldbook.iupac.org/M03986.html
    2. https://en.wikipedia.org/wiki/Molecular_entity
    """

    # core structure: networkx Graph
    _graph = attr.ib(default=attr.Factory(Graph), init=False)

    # the title for molecule/atoms
    title = attr.ib(default="molecular entity", validator=attr.validators.instance_of(str))

    # molecular charge
    charge = attr.ib(default=0, init=False)

    # molecular multiplicy
    multiplicity = attr.ib(default=1, init=False)
# 24dd16f2-0889-454d-8264-cc8838f72318 ends here
