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

xyz_file = sys.argv[1]
txt = open(xyz_file).read()
txt = txt.replace('\r', '')
txt = txt.strip()
txt = txt.split('\n')
num = len(txt) / 2
mol1 = txt[0:num]
mol2 = txt[num:]

ele = {}
for m in mol2[2:]:
    t = m.split()
    if ele.has_key(t[0]):
        ele[t[0]].append(t[1:])
    else:
        ele[t[0]] = []
        ele[t[0]].append(t[1:])

sum = 0
def getNeighboringAtomXYZ(xyz, list):
    global sum
    min = 5000.0
    xx = xyz[0]
    yy = xyz[1]
    zz = xyz[2]
    for x,y,z in list:
        xx = float(xx)
        yy = float(yy)
        zz = float(zz)
        x = float(x)
        y = float(y)
        z = float(z)
        t = (xx - x)**2 + (yy - y)**2 + (zz -z)**2
        if t < min:
            min = t
            res = str(x), str(y), str(z)
    sum += min
    return res

def getEquivalentAtom(m1):
    t = m1.split()
    list = ele[t[0]]
    xyz = getNeighboringAtomXYZ(t[1:], list)
    return t[0], xyz[0], xyz[1], xyz[2]

mol2 = mol2[:2]
for m1 in mol1[2:]:
    m2 = getEquivalentAtom(m1)
    mol2.append('  '.join(m2))

print "RMS = %.1f" % sum 
fp = open(xyz_file, 'w')
fp.writelines('\n'.join(mol1))
fp.writelines('\n')
fp.writelines('\n'.join(mol2))
fp.close()
