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

from p4vasp.SystemPM import *
from string import split


s = XMLSystemPM("vasprun.xml")

e = s.E_FERMI
tdos = s.TOTAL_DOS  

f = open("tdos.csv","w")
for v in tdos[0]:
    line = "%f" % (v[0] - e) + ','
    for i in v[1:]:
        line = line + "%f" % i + ','
    line = line[:-1]
    f.write(line + '\n')
f.close()

