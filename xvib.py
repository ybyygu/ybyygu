#!/usr/bin/env python
# written by ybyygu at 2006 6/12
# last updated at: 2006 6/13

import re
import getopt
from math import sin, cos, pi
import sys

def usage(progname):
    print 'Usage:', progname, ' gauss_logfile [-n freq_num] [-s scale_value] [-f total_frames]'
    print '    gauss_logfile: The gaussian log file which will be parsed'
    print '    -n freq_num: Which freq will be used?'
    print '    -s scale_value: Use this value to scale the displacement'
    print '    -f total_frames: To specify the total frames of output'

# default parameters
freq_num = "1"
scale_value = 0.8
total_frames = 10

ATOMS = ('H ', 'He',
          'Li', 'Be', 'B ', 'C ', 'N ', 'O ', 'F ', 'Ne',
          'Na', 'Mg', 'Al', 'Si', 'P ', 'S ', 'Cl', 'Ar',
          'K ', 'Ca', 'Ti', 'V ', 'Cr', 'Mn', 'Fe', 'Co',
          'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 
          'Kr', 'X ')

progname = sys.argv[0].split('/')[-1]
if len(sys.argv)<=1:
    print "No gaussian output file specified."
    usage(progname)
    sys.exit(2)

gauss_logfile = sys.argv[1]
try:
    input = open(gauss_logfile, 'r')
except:
    print "Can not open %s to read." %(gauss_logfile)
    sys.exit(2)

# parse command line options
try:
    if len(sys.argv)>1:
        opts, args = getopt.getopt(sys.argv[2:], "n:s:f:")
except:
    usage(progname)
    sys.exit(2)

for o, a in opts:
    if o == '-n':
        freq_num = a
    elif o == '-s':
        try:
            scale_value = float(a)
        except:
            print "Wrong scale_value."
            sys.exit(2)
    elif o == '-f':
        try:
            total_frames = int(a)
        except:
            print "Wrong total_frames."
            sys.exit(2)
    else:
        usage(progname)
        sys.exit(2)

### parse the gaussian log file

## collect standard coordinates information

#                          Standard orientation:                          
# ---------------------------------------------------------------------
# Center     Atomic     Atomic              Coordinates (Angstroms)
# Number     Number      Type              X           Y           Z
# ---------------------------------------------------------------------
#    1          6             0       -1.199187    0.000547   -0.692474
#    2          6             0       -1.199260    0.001030    0.692361

rexSTDOrientationLabel = re.compile(r'\s+Standard\s+orientation:\s*$')
rexSTDCoordinates = re.compile(r'\s+\d+\s+(?P<atom_num>\d+)\s+\d+\s+(?P<x>[\d.-]+)\s+(?P<y>[\d.-]+)\s+(?P<z>[\d.-]+)\s*$')

# search for "Standard orientation:" line
# there may be more than one "Standard orientation:" entries
# but only the last one will be taked
line = input.readline()
while line:
    if rexSTDOrientationLabel.match(line):
        fp = input.tell()
    line = input.readline()

# reset the position
input.seek(fp)

# skip 5 lines
line = input.readline()
line = input.readline()
line = input.readline()
line = input.readline()
line = input.readline()

x = []; y = []; z = []
atoms = []
while line and rexSTDCoordinates.match(line):
    atoms.append(ATOMS[int(rexSTDCoordinates.match(line).group("atom_num"))-1])
    x.append(float(rexSTDCoordinates.match(line).group("x")))
    y.append(float(rexSTDCoordinates.match(line).group("y")))
    z.append(float(rexSTDCoordinates.match(line).group("z")))
    line = input.readline()

## collect vibration displacement information
while line and line.find("Harmonic freq")==-1:
    line = input.readline()
if len(line)==0:
    input.close()
    print "No freq info found."
    sys.exit(2)

#                    28                     29                     30
#                    ?A                     ?A                     ?A
# Frequencies --  3374.9193              3374.9296              3389.3471
#  Atom AN      X      Y      Z        X      Y      Z        X      Y      Z
#    1   6     0.00   0.01   0.00     0.01   0.05   0.00    -0.01  -0.04   0.00
rexFreqNum = re.compile(r'\s+(\d+)\s+(\d+)\s+(\d+)\s*$')
rexFreqLabel = re.compile(r'\s*Frequencies --\s+[\d.-]+')
rexXYZLabel = re.compile(r'\s*Atom\s+AN\s+X\s+Y\s+Z')
rexXYZ = re.compile(
                r"""\s*\d+\s+\d+\s+
                    (?P<dx1>[\d.-]+)\s+(?P<dy1>[\d.-]+)\s+(?P<dz1>[\d.-]+)\s+
                    (?P<dx2>[\d.-]+)\s+(?P<dy2>[\d.-]+)\s+(?P<dz2>[\d.-]+)\s+
                    (?P<dx0>[\d.-]+)\s+(?P<dy0>[\d.-]+)\s+(?P<dz0>[\d.-]+)\s*$""",
                    re.VERBOSE)
pos = -1
while line:
    if rexFreqNum.match(line):
        if str(freq_num) in rexFreqNum.match(line).group().split():
            pos = rexFreqNum.match(line).group().split().index(freq_num)
            break
    line = input.readline()
if pos<0:
    print "No this freq (%s) info" %(freq_num)
    sys.exit(2)


while line and not rexXYZLabel.match(line):
    line = input.readline()

dx = []; dy = []; dz = []
line = input.readline()
while line and rexXYZ.match(line):
    n = str(int(freq_num)%3)
    dxn = "dx" + n; dyn = "dy" + n; dzn = "dz" + n
    dx.append(float(rexXYZ.match(line).group(dxn)))
    dy.append(float(rexXYZ.match(line).group(dyn)))
    dz.append(float(rexXYZ.match(line).group(dzn)))
    line = input.readline()

input.close()

## output everythings
try:
    output = open("%s-freq_%s.xyz" %(gauss_logfile, freq_num), 'w')
except:
    print "Can not open file to write."
    sys.exit(2)

for f in range(total_frames):

    output.writelines("%d\n" %(len(atoms)))
    output.writelines("frame %02d of %s; freq_num: %s, scale_value: %s\n" % (f, gauss_logfile, freq_num, scale_value))

    factor = cos(2*pi*f/total_frames)*scale_value
    for i in range(len(x)):
        nx = x[i] + dx[i]*factor
        ny = y[i] + dy[i]*factor
        nz = z[i] + dz[i]*factor
        output.writelines("%3s %11.5f %11.5f %11.5f\n" %(atoms[i], nx, ny, nz))

output.close()
print "done." 
