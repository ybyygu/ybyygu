#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  generate a restarted gjf file for your gaussian log file.
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.11
#       CREATED:  28-11-06
#      REVISION:  15-12-06
#===============================================================================#
import sys
import re
import getopt
from math import sqrt
from math import cos
from math import sin
from math import acos

#===============================================================================#
#
#  Class related
#
#===============================================================================#

class vector:
    """
    Class that represents a atom space vector.
    """    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        """
        return the length of vector
        """
        return sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def distance(self, avector):
        """
        return the distance of the two vectors
        """
        return sqrt((self.x - avector.x)**2 + (self.y - avector.y)**2 + (self.z - avector.z)**2)

    def dot(self, avector):
        """
        dot product
        """
        return self.x * avector.x + self.y * avector.y + self.z * avector.z

    def cross(self, avector):
        """
        cross product
        """
        nx = self.y * avector.z - self.z * avector.y
        ny = self.z * avector.x - self.x * avector.z
        nz = self.x * avector.y - self.y * avector.x
        return vector(nx, ny, nz)

    def __sub__(self, avector):
        x = self.x - avector.x
        y = self.y - avector.y
        z = self.z - avector.z
        return vector(x, y, z)

    def angle(self, vb, vc):
        """
        return the angle between the tree vector points: va(self), vb, vc
        """
        vba = self - vb
        vbc = vc - vb
        arg = acos(vba.dot(vbc)/vba.length()/vbc.length()) * 180.0 / 3.1415926
        return arg

    def torsion(self, vb, vc, vd):
        """
        return the torsion angle between the four vector points: va, vb, vc, vd
        """
        vba = self - vb
        vbc = vc - vb
        vcb = vb - vc
        vcd = vd - vc
        vbaxbc = vba.cross(vbc)
        vcbxcd = vcb.cross(vcd)
        arg = acos(vbaxbc.dot(vcbxcd) / vbaxbc.length() / vcbxcd.length()) * 180.0 /3.1415926
        
        if vba.cross(vbc).dot(vcd) > 0:
            sign = -1
        else:
            sign = 1
        return arg * sign

class gaussian_log_parser:
    def __init__(self, filename):
        try:
            self.fp = open(filename)
        except IOError:
            print "Cannot open %s" % filename
            raise

        self.cur_pos = 0
        self.cur_step = 0
        self.start_pos = 0
        self.start_step = 0
        self.end_pos = 0
        self.end_step = 0

        fp.seek(0,2)
        self._fp_size = fp.tell()

    def getxyz_str(self, opt_step = -1):
        pass

    def getxyz(self, opt_step = -1):
        xyz = self.getxyz_str(opt_step)

    def move2opt_step(self, opt_step = -1, strollsize = 10000):
        """\
        search and locate the opt_step position
        """

        if opt_step == 0:
            fp.seek(0, 0)
            return True

        rex = re.compile(r'^ Step number\s+(\d+)\s+out of')
        key = ' Step number '

        if self.start_step == 0:
            self.fp.seek(0,0)
            if self._move_forward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.start_step = int(rex.search(line).group(1))
                    self.start_pos = self.fp.tell()
                else:
                    raise
            else:
                raise
            if opt_step == 1:
                self.fp.seek(self.cur_pos, 0)
                return True

        if self.end_step == 0:
            self.fp.seek(0, 2)
            if self._move_backward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.end_step = int(rex.search(line).group(1))
                    self.end_pos = self.fp.tell()
                else:
                    raise
            else:
                raise
            if opt_step == -1:
                self.fp.seek(self.cur_pos, 0)
                return True

        # minus step number mean step backwardly from the end
        if opt_step < 0:
            opt_step = opt_step + self.end_step -1
        
        if opt_step >0 and opt_step < self.end_step:
            pos = float(self.opt_step - self.start_step) / (self.end_step - self.start_step) \
                  * (self.end_pos - self.start_pos) + self.start_pos
            pos = int(pos - 2)
            self.fp.seek(pos, 1)

            if self._move_forward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.cur_step = int(rex.search(line).group(1))
                    if self.cur_step == opt_step:
                        self.cur_pos = self.fp.tell()
                        return True
                    else:
                        self.move2opt_step(opt_step)
            # TODO
        else:
            print "The step number is invalid."
            return 1
            
    
    def _move_backward(self, search_key, strollsize = 10000):
        """\
        move backwardly by search_key, return true if successful, else return false
        """
        # search_key sould be less than 100 bytes 
        while self.fp.tell() >= 0:
            fp.seek(-strollsize, 1)
            pos = fp.tell()
            # we have to read a bit more 
            buffer = fp.read(strollsize + 100)
            # restore position
            fp.seek(pos, 0)
             
            pos_key = buffer.find(key)
            if pos_key >=0:
                self.cur_pos = pos + pos_key -1
                fp.seek(self.cur_pos)
                return True
        return False

    def _move_forward(self, search_key, strollsize = 10000):
        """\
        move forwardly by search_key, return true if successful, else return false
        """
        # search_key sould be less than 100 bytes
        # strollsize should be more than 100 bytes
        while self.fp.tell() <= self._fp_size:
            pos = self.fp.tell()
            # we have to read a bit more 
            buffer = fp.read(strollsize + 100)
            # restore position
            self.fp.seek(-100, 1)
            
            pos_key = buffer.find(key)
            if pos_key >=0:
                self.cur_pos = pos + pos_key -1
                self.fp.seek(self.cur_pos, 0)
                return True
        return False

class atoms:
    def __init__(self):
        self.atoms = []

    def addAtom(self, x, y, z):
        atom = vector(x, y, z)
        self.atoms.append(atom)
    
    def bond(self, id1, id2):
        """
        return the length of the bond specified by the two atom index numbers
        """
        return self.atoms[id1].distance(self.atoms[id2])

    def angle(self, id1, id2, id3):
        """
        return the angel of the tree atoms specified by atoms index
        """
        return self.atoms[id1].angle(self.atoms[id2], self.atoms[id3])

    def torsion(self, id1, id2, id3, id4):
        """
        return the torsion angle of for atoms specified by atoms index
        """
        return self.atoms[id1].torsion(self.atoms[id2], self.atoms[id3], self.atoms[id4])

#===============================================================================#
#
#  Public functions
#
#===============================================================================#

def generate_filename(filename):
    """
    filename = aaa-rn, not aaa-rn.gjf
    """
    inc = 1
    pat = re.compile(r'^(r|R)(\d+)$').match(filename.split('-')[-1])
    if pat:
        inc = int(pat.group(2)) + 1
        inc = "%s" % inc 
        filename = filename[:-(len(inc)+1)] + '%s%s' % (pat.group(1), inc)
    else:
        filename = filename + '-r%s' % inc

    return filename

#===============================================================================#
#
#  Main Section
#
#===============================================================================#

###
# parse command line options
#

if len(sys.argv) == 2:
    log = sys.argv[1]

    if log[-4:] in ('.log', '.out'):
        gjf = log[:-4]
    else:
        gjf = log
    gjf = gjf + ".gjf"
elif len(sys.argv) == 3:
    log = sys.argv[1]
    gjf = sys.argv[2]
else:
    print "Too many or too few arguments!"
    sys.exit(1)

###
# parse gaussian log file
#
# TODO: combile with gaussian_log_parser class

fp = open(log)

# read the last line and do a test
fp.seek(-100, 2)
line = fp.readlines()[-1]

#  Number     Number      Type              X           Y           Z
# ---------------------------------------------------------------------
#    1          8             0       -0.453584   -3.860986    5.501901
key = 'Standard orientation:'
rex_xyz = re.compile(r'^\s*\d+\s+\d+\s+\d+\s+([-0-9.]+\s+[-0-9.]+\s+[-0-9.]+)$')
round = False  #  True : use the next to last the position of the key
               #  False: use the last position of the key

if rex_xyz.match(line.strip()):
    # rare case: the standard xyz lines may be not complete.
    round = True
pos = 0
strollsize = 5000
c = 2
while fp.tell() != 0:   # should not be the begin of the file
    fp.seek(-strollsize, 1)
    pos = fp.tell()
    # need consider the situation when current position between the key
    # to read a bit more will not cause exception, even when stay in the end of the file
    buffer = fp.read(strollsize + len(key))
    if buffer.rfind(key) >= 0:
        if not round:
            pos += buffer.rfind(key) - 1
            break
        else:
            c -= 1
            if c <= 0:
                pos += buffer.rfind(key) - 1
                break
    fp.seek(pos, 0)
fp.seek(pos, 0)

line = fp.readline()
# deal with the big strollsize, which may catain more than one standard orientation entries
if round:
    line = fp.readline()
    while line:
        if rex_xyz.match(line.strip()):
            break
        line = fp.readline()

while line and not rex_xyz.match(line.strip()):
    line = fp.readline()

mol = atoms()
while rex_xyz.match(line.strip()):
    xyz = rex_xyz.match(line.strip()).group(1).split()
    xyz = [float(v) for v in xyz]
    mol.addAtom(xyz[0], xyz[1], xyz[2])
    line = fp.readline()
fp.close()


###
# now process the gjf file
#
txt = open(gjf).read().replace('\r', '')
sections = txt.split('\n\n')

# the atoms from out file should be same as from gjf file
# TODO: to compare the atom symbol is safer
lines = sections[2].split('\n')
if len(lines[1:]) != len(mol.atoms):
    print "The log file and gjf file are mismatch."
    sys.exit(1)
if len(lines[1].split()) == 1:
    ###
    # zmatrix style
    #
    BAD = {}    # BAD is not bad
    for line in lines[1:]:
        # zmatrix:
        # C 3 B3 2 A2 1 D1
        # TODO: how about constant number in cord_info?
        # TODO: how about oniom style zmatrix cord_info?
        try:
            cord_info = line.split()
            # bonds
            id1 = lines.index(line) - 1
            id2 = int(cord_info[1]) - 1
            var = cord_info[2]
            value = mol.bond(id1, id2)
            BAD[var] = value
            # angles
            id3 = int(cord_info[3]) - 1
            var = cord_info[4]
            value = mol.angle(id1, id2, id3)
            BAD[var] = value
            # torsion angles
            id4 = int(cord_info[5]) - 1
            var = cord_info[6]
            value = mol.torsion(id1, id2, id3, id4)
            BAD[var] = value
        except IndexError:
            pass
    # update zmatrix variable in sections[3] with the new value
    list = []
    lines = sections[3].split('\n')
    for line in lines:
        var = line.split()[0]
        list.append("%4s%20.8f" % (var, BAD[var]))
    sections[3] = '\n'.join(list)
else:
    ###
    # XYZ style
    #
    list = []
    list.append(lines[0])
    rex_xyz = re.compile(r'(\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+)')
    for line, atom in zip(lines[1:], mol.atoms):
        str = rex_xyz.search(line).group(1)
        line = line.replace(str, "%20.8f%20.8f%20.8f" % (atom.x, atom.y, atom.z))
        list.append(line)
    sections[2] = '\n'.join(list)

###
# Output
#
output = generate_filename(gjf[:-4]) + ".gjf"
fp = open(output, 'w')
newlines = '\n\n'.join(sections)
fp.writelines(newlines)
fp.close()
print "Successful!"
