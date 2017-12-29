#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::go-header][go-header]]
#===============================================================================#
#   DESCRIPTION:  GO: a Graph-based chemical Objects library
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  rewrite from scratch, for the 4th time
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2006-08-30 Wed 16:51>
#       UPDATED:  <2017-12-29 Fri 10:10>
#===============================================================================#
# go-header ends here

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::902db43a-44b3-483c-9c70-fbd221f6d4b3][902db43a-44b3-483c-9c70-fbd221f6d4b3]]
def toplevel(o):
    __all__.append(o.__name__)
    return o

__all__ = []

from .element import *
from .atom import *
from .bond import *
from .molecule import *
# 902db43a-44b3-483c-9c70-fbd221f6d4b3 ends here
