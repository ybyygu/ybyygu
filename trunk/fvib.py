#!/usr/bin/env python
# written by ybyygu at 2006 6/12
# last updated at: 2006 9/1

import re
import getopt
import sys

# default parameters
INDEX = "1"
SCALE = 0.5
OUTPUTFILENAME = ''

def usage(progname):
    print 'Usage:', progname, ' [-i index] [-s scale] [-o output.gjf] gauss_logfile'
    print '    gauss_logfile: The gaussian log file which will be parsed'
    print '    -i index: Which freq will be used? The default is the first one.'
    print '    -s scale: Use this value to scale the displacement. The default value is %s.' % SCALE
    print '    -o output.gjf: Use this option to specify an output file.'

ATOMS = ('H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S',
         'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge',
         'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
         'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
         'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
         'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm',
         'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt')

PROGNAME = sys.argv[0]
# parse command line options
if len(sys.argv)>1:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:s:o:", ['help', 'index=', 'scale=', 'output='])
    except :
        print >> sys.stderr, "Can't parse command line option."
        sys.exit(2)
else:
    usage(PROGNAME)
    sys.exit(0)

for o, a in opts:
    if o in ['-h', '--help']:
        usage(PROGNAME)
        sys.exit(0)
    elif o in ['-i', '--index']:
        INDEX = a
    elif o in ['-s', '--scale']:
        try:
            SCALE = float(a)
        except:
            print "Wrong scale value."
            sys.exit(2)
    elif o in ['-f', '--frames']:
        try:
            FRAMES = int(a)
        except:
            print "Wrong frames value."
            sys.exit(2)
    elif o in ['-o', '--output']:
        OUTPUTFILENAME = a
    else:
        usage(PROGNAME)
        sys.exit(2)

if len(args) == 1:
    GAUSSLOGFILE = args[0]
else:
    print >> sys.stderr, "You must specify a gaussian log file."
    sys.exit(2)
try:
    INPUT = open(GAUSSLOGFILE, 'r')
except:
    print >> sys.stderr, "Can not open %s to read." %(GAUSSLOGFILE)
    sys.exit(2)

##########################################################################
# parse the gaussian log file
##########################################################################

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
line = INPUT.readline()
while line:
    if rexSTDOrientationLabel.match(line):
        fp = INPUT.tell()
    line = INPUT.readline()

# reset the position
INPUT.seek(fp)

# skip 5 lines
for i in range(5):
    line = INPUT.readline()

x = []; y = []; z = []
atoms = []
while line and rexSTDCoordinates.match(line):
    atoms.append(ATOMS[int(rexSTDCoordinates.match(line).group("atom_num"))-1])
    x.append(float(rexSTDCoordinates.match(line).group("x")))
    y.append(float(rexSTDCoordinates.match(line).group("y")))
    z.append(float(rexSTDCoordinates.match(line).group("z")))
    line = INPUT.readline()

## collect vibration displacement information
while line and line.find("Harmonic freq")==-1:
    line = INPUT.readline()
if len(line)==0:
    INPUT.close()
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
        if str(INDEX) in rexFreqNum.match(line).group().split():
            pos = rexFreqNum.match(line).group().split().index(INDEX)
            break
    line = INPUT.readline()
if pos<0:
    print "No this freq (%s) info" %(INDEX)
    sys.exit(2)

while line and not rexXYZLabel.match(line):
    line = INPUT.readline()

dx = []; dy = []; dz = []
line = INPUT.readline()
while line and rexXYZ.match(line):
    n = str(int(INDEX)%3)
    dxn = "dx" + n; dyn = "dy" + n; dzn = "dz" + n
    dx.append(float(rexXYZ.match(line).group(dxn)))
    dy.append(float(rexXYZ.match(line).group(dyn)))
    dz.append(float(rexXYZ.match(line).group(dzn)))
    line = INPUT.readline()

INPUT.close()

## output everything
if OUTPUTFILENAME == '':
    OUTPUTFILENAME = "%s-index_%s-scale_%s.gjf" %(GAUSSLOGFILE, INDEX, SCALE)
try:
    output = open(OUTPUTFILENAME, 'w')
except :
    print >> sys.stderr, "Can not open file to write."
    sys.exit(2)

output.writelines("#Put Keywords Here, check Charge and Multiplicity\n")
output.writelines("\n")
output.writelines("%s; index: %s; scale: %s\n" % (GAUSSLOGFILE, INDEX, SCALE))
output.writelines("\n")
output.writelines("0 1\n")

for i in range(len(x)):
    nx = x[i] + dx[i]*SCALE
    ny = y[i] + dy[i]*SCALE
    nz = z[i] + dz[i]*SCALE
    output.writelines("%3s %11.5f %11.5f %11.5f\n" %(atoms[i], nx, ny, nz))

output.close()
print "done." 
