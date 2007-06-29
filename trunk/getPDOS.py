#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  
#      REVISION:  ---
#===============================================================================#

import sys
from p4vasp.SystemPM import *


s = XMLSystemPM("vasprun.xml")

e = s.E_FERMI
pdos = s.PARTIAL_DOS  


try:
    atom_index = int(sys.argv[1])
except:
    print "You must give me a integer to index the atom."
    sys.exit(0)

atom_nums = len(pdos)
if atom_index > atom_nums or atom_index <= 0:
    print "Invalid atom number. Please try again."
    sys.exit(0)

f = open("pdos-%s.csv" % atom_index,"w")
for v in pdos[atom_index - 1][0]:
    line = "%f" % (v[0] - e) + ','
    for i in v[1:]:
        line = line + "%f" % i + ','
    line = line[:-1]
    f.write(line + '\n')
f.close()

