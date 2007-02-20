#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#       OPTIONS:  --fix the terminal or low layer atoms during ONIOM optimization
#  REQUIREMENTS:  ---
#         NOTES:  write for liyan
#                 use this for special purpose
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.2
#       CREATED:  x-12-2006 
#      REVISION:  23-1-2007
#===============================================================================#

import sys
import getopt
import re
from os.path import basename
from math import sqrt
from math import cos
from math import sin
from math import acos   
#===============================================================================#
#
#  Class
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
#  Functions
#
#===============================================================================#

def findTermAtomByConn(atom_num):
    """
    find terminal atom by querying connectivity table
    """
    count = 0
    global mol_conn
    for line in mol_conn:
        lst = line.split()
        if len(lst) == 1:
            continue
        try:
            if lst.index(atom_num) >= 0:
                if lst.index(atom_num) == 0:
                    count += (len(lst) - 1)/2
                    number = lst[1]
                else:
                    count += 1
                    number = lst[0]
        except ValueError:
            pass
    if count == 1:
        return number
    else:
        raise ValueError

def contractTermBond(atom1, atom2, length = 1.47):
    old_length = atom1.distance(atom2)
    v21 = atom2 - atom1
    scale = length / old_length
    x = atom1.x + (atom2.x - atom1.x) * scale
    y = atom1.y + (atom2.y - atom1.y) * scale
    z = atom1.z + (atom2.z - atom1.z) * scale
    return vector(x, y, z)

def usage(program):
    print "%s " % (program)
    print "-f, --fixonly: not try to terminate O atoms with H and not try to contract Si-H bond length"
    print "-l, --fixlow: only try to fix low layer atoms"
    print "-k, --keeplinks: keep link atoms related information"
    print "-m, --appendmod: append modredundant information(use opt=modredundant to fix lowlayer atoms)"

def parseCmdOptions(argv):
    if argv is None:  argv = sys.argv
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'hflkm', ['help', 'fixonly', 'fixlow', 'keeplinks', 'appendmod'])
    except:
        print "Can't parse argument options!"
        sys.exit(1)
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit(0)
        elif o in ('-f', '--fixonly'):
            global fix_only
            fix_only = True
        elif o in ('-l', '--fixlow'):
            global fix_low
            fix_low = True
        elif o in ('-k', '--keeplinks'):
            global rm_link
            rm_link = False
        elif o in ('-m', '--appendmod'):
            global append_mod
            append_mod = True
    if argv:
        # use the first one
        global gaussian_log
        gaussian_log= args[0]
    else:
        print "A correct gjf file must be given."
        sys.exit(1)

def output(filename):
    global sections
    try:
        fp = open(filename, 'w')
        fp.writelines('\n\n'.join(sections))
        fp.close()
    except:
        print "Cannot open %s to write." % filename
        sys.exit(1)
    
#===============================================================================#
#
#  Main routine
#
#===============================================================================#

gaussian_log = None
fix_only = False
fix_low = False
append_mod = False
rm_link = True
parseCmdOptions(sys.argv)

try:
    txt = open(gaussian_log).read()
except:
    print "Cannot open %s to read." % gaussian_log
    sys.exit(1)

txt = txt.replace('\r', '').strip()
sections = txt.split('\n\n')
mol_spec = sections[2].split('\n')

done = False
mol_conn = ()
if not fix_low:
    if sections[0].find('connectivity') < 0 or len(sections) < 4:
	print "Are you sure the connectivity information included in this file?"
        sys.exit(1)
    else:
        mol_conn = sections[3].split('\n')

if fix_only:
    rex_atom = re.compile(r'^ H\s+.*L$')
else:
    rex_atom = re.compile(r'^ O\s+.*L$')

rex_low = re.compile(r'(^ *[^\s]+\s+)-*\d+(\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+\s+L$)')
rex_xyz = re.compile(r'(\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+\s+[-0-9]+\.[0-9]+)')
low_ids = []
ok = False
for atom in mol_spec:
    p = rex_xyz.search(atom)
    if p:
        id = mol_spec.index(atom)
        p = rex_low.match(atom)
        if p:
            if fix_low:
            # fix low layer atoms
                low_ids.append(id)
                mol_spec[id] = atom.replace(' 0 ', '-1 ')
            else:
                if not fix_only:
                # try to replace terminal O atoms by H atoms and contract terminal Si-H bond
                    try:
                        Si_num = findTermAtomByConn(str(id)) 
                        mol_spec[int(id)] = mol_spec[int(id)].replace(' O ', ' H ')
                        xyz = rex_xyz.search(mol_spec[int(Si_num)]).group(1).split()
                        atom1 = vector(float(xyz[0]), float(xyz[1]), float(xyz[2]))
                        xyz = rex_xyz.search(mol_spec[int(id)]).group(1).split()
                        atom2 = vector(float(xyz[0]), float(xyz[1]), float(xyz[2]))
                        atom2 = contractTermBond(atom1, atom2)
                        xyz_str = rex_xyz.search(mol_spec[int(id)]).group(1)
                        mol_spec[int(id)] = mol_spec[int(id)].replace(xyz_str, "%12.6f%12.6f%12.6f" % (atom2.x, atom2.y, atom2.z))
                    except ValueError:
                        pass
                  # fix terminal atoms
                try:
                    Si_num = findTermAtomByConn(str(id)) 
                    ok = True
                    mol_spec[int(id)] = mol_spec[int(id)].replace(' 0 ', '-1 ')
                    mol_spec[int(Si_num)] = mol_spec[int(Si_num)].replace(' 0 ', '-1 ')
                except ValueError:
                    pass
        if rm_link:
        # remove link atoms related information
            p = re.compile(r'(^.*(L|M)\s+H)(.*$)').match(atom)
            if p:
                mol_spec[id] = p.group(1)
if not fix_low and not ok:
    print "Too bad! I fail to do that for you."

if fix_low and append_mod:
    mod_txt = ["X " + str(i) + " F" for i in low_ids]
    mod_txt = '\n'.join(mod_txt)
    try:
        sections[3] = mod_txt
    except:
        sections.append(mod_txt)
    sections[0] = sections[0].replace('geom=connectivity', 'geom=modredundant')
    try:
       del sections[4]
    except:
        pass
else:
    # Liyan: Please add your customed link1 command here
    sections[0] = sections[0].replace('geom=connectivity', '')
    link1_txt = '--Link1--\n' + sections[0].split('\n')[0] + '\n%mem=96MW\n%nproc=2\n'
    link1_txt += '%rwf=a,245MW,b,245MW,c,245MW,d,245MW,e,245MW,f,245MW\n'
    link1_txt += '%nosave\n#p rb3lyp/6-31G(d) scf=tight geom=allcheck test'
    try:
        sections[3] = link1_txt
    except IndexError:
        sections.append(link1_txt)

sections[2] = '\n'.join(mol_spec)
output(gaussian_log)
print "Liyan: %s has been successfully updated!" % basename(gaussian_log)

