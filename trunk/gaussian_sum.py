#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  extract the most important informations from gaussian log files 
# 
#  REQUIREMENTS:  python
#         NOTES:  ---
#        AUTHOR:  win.png@gmail.com (ybyygu) 
#       LICENCE:  GPL version 2 or upper
#       CREATED:  2006-8-30 
#       UPDATED:  2007-08-01 16:27
#===============================================================================#
__VERSION__ = "0.3"

#===============================================================================#
#
#  importing
#
#===============================================================================#
import sys
from sys import stdin, stderr
import os
from os.path import expanduser, join, exists, isdir, isfile, basename, dirname
import glob
from stat import *
import time
import re

#===============================================================================#
#
#  constants
#
#===============================================================================#
LINELENGTH = 72

#===============================================================================#
#
#  functions
#
#===============================================================================#

def centerWithStr(str, char, length):
    nl = (length - len(str))/2
    if nl <= 0:
        str = " ... %s" % str[length + 10:]
        nl = (length - len(str))/2
    return char * nl + str + char * nl

def summary_files(gaussian_log_files, output_steps=5, show_all=False, warn_old=False):
    global LINELENGTH
    
    def log_cmp(x, y):
        x = os.stat(x)[ST_MTIME]
        y = os.stat(y)[ST_MTIME]
        return cmp(x,y)

    gaussian_log_files.sort(log_cmp)

    for log in gaussian_log_files:
        try:
            flog = open(log, 'rb')
        except IOError:
            print >>stderr, "Can't open %s to read!" %(log)
            continue
        hint = " %s " % basename(log)
        print "[" + centerWithStr(hint, '=', LINELENGTH) + "]"
        if not show_all:
            if read_backwards(flog, output_steps):
                print " " + ":"* LINELENGTH
        walklog(flog)
        flog.close()
        hint1 = " %s " % dirname(log)
        hint2 = " %s " % basename(log)
        print "[" + centerWithStr(hint1, '=', LINELENGTH) + "]"
        print "[" + centerWithStr(hint2, '=', LINELENGTH) + "]"

        # warn outdated log 
        span = (time.time() - os.stat(log)[ST_MTIME]) / 3600
        if warn_old and span > 4:
            print " ** WARNING! THIS FILE HAS NO CHANGE MORE THAN %d HOURS. **" % span

def walklog(flog):
    import re
    
    global LINELENGTH
    line = flog.readline()
    freq_count = 0
    # gaussian log file begins with a space
    if not line or not line[0] == ' ':
        print ' ' + '*'*LINELENGTH
        print ' this is not a gaussian log file...'
        return

    while line:
        if re.compile(r'^ %').match(line):
            while line and re.compile(r'^ %').match(line):
                print line,
                line = flog.readline()
        elif re.compile(r'^ #').match(line):
            print  ' ' + '-'*LINELENGTH
            print line,
            for i in range(3):
                line = flog.readline()
                if re.compile(r'^ -').match(line):
                    break
                else:
                    print line,
            print  ' ' + '-'*LINELENGTH
        elif line.find("Number of steps in this run=") >= 0:
            print line,
        # print SCF information and the next two lines
        elif line.find("SCF Done") >= 0:
            print line,
            for i in range(2):
                line = flog.readline()
                print line,
            print " " + '-'*LINELENGTH
        elif line.find("Step number") >= 0:
            print line,
        elif line.find("exceeded") >= 0:
            print line,
        # print energy 
        elif line.find('energy =') >=0:
            print line,
        elif re.compile(r'^ Cycle ').match(line):
            print line,
        elif re.compile(r'^ E=').match(line):
            print line,
        # print the first line of Eigenvalues
        elif line.find("Eigenvalues ---") >= 0:
            print line,
            while line and line.find("Eigenvalues ---") >=0:
                line = flog.readline()
        # print converged information
        elif line.find("Converged?") >= 0:
            print " " + '-'*LINELENGTH
            print line, 
            for i in range(7):
                line = flog.readline()
                if line.find('GradGradGrad') >=0:
                    break
                print line,
            print  " " + '-'*LINELENGTH
        # WARNING may be important!
        elif line.find("WARNING") >=0:
            print line,
        elif line.find("Frequencies --") >= 0:
            freq_count += 1
            if freq_count == 1:
                print line,
        elif line.find("Zero-point correction=") >= 0:
            print line,
        elif line.find("Sum of electronic and zero-point Energies=") >= 0:
            print line,
            print " " + '-'*LINELENGTH
        elif line.find("termination") >= 0:
            print line,
        elif line.find("Job cpu time:") >= 0:
            print line,

        line = flog.readline()

def read_backwards(fp, maxrounds = 5, sizehint = 20000):
    """
     Step number n-4 out of ... # stop here
     ...
     Step number n-1 out of ...
     Step number n out of ...
    """
    # jump to the end of the file
    fp.seek(0, 2)

    round = 0
    while round < maxrounds: 
        try:
            fp.seek(-sizehint, 1)
        except IOError: # hit the top of file
            fp.seek(0, 0)
            return False
        fpos = fp.tell()
        pos = fp.read(sizehint).rfind(' Step number')
        fp.seek(fpos, 0)
        if pos != -1:
            fp.seek(pos, 1)
            round += 1
        elif fp.tell() == 0:
            return False
        else:
            continue
    return True

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
#  Main Program
#
#===============================================================================#
def main (argv=None):
    import optparse

    # parse commandline options
    cmdl_version = "%prog " + __VERSION__
    cmdl_usage = "Usage: %prog [options] [file or directory]" 
    cmdl_parser = optparse.OptionParser(usage=cmdl_usage, version=cmdl_version, conflict_handler='resolve')
    cmdl_parser.add_option('-h', '--help', 
                            action='help',
                            help='print this help text and exit')
    cmdl_parser.add_option('-v', '--version', 
                            action='version',
                            help='print program version and exit')
    cmdl_parser.add_option('-a', '--show-all',
                            action='store_true',
                            dest='show_all', 
                            default=False,
                            help='output all available optimization steps of each gaussian file.')
    (cmdl_opts, cmdl_args) = cmdl_parser.parse_args()

    output_steps = 5
    warn_old = False
    show_all = True
    # try to read from default gaussian output directory if no argv specified
    logfiles = []
    if not cmdl_args:
        warn_old = True
        # figure out the most possible working log file
        txt = os.popen('/usr/bin/pgrep -u $USER "g03|g98"').read().strip()
        if not txt:
            print "No working gaussian log file found."
            sys.exit(0)
        pids = txt.split('\n')
        for pid in pids:
            fenv = "/proc/" + pid + "/environ"
            txt = open(fenv).read()
            p = re.compile('\x00PWD=([^\x00]+)').search(txt)
            if p:
                work_dir = p.group(1)
                logs = glob.glob(join(work_dir, "*.log"))
                logfiles = logfiles + logs
    else:
        for a in cmdl_args:
            if isdir(a):
                logfiles = glob.glob(join(a, "*.log")) + glob.glob(join(a, "*.out"))
            else:
                logfiles.append(a)

    # if show all, pipe output into file perusal filter (pager/less/more)
    if show_all and sys.platform != "win32":
        lesser = "/usr/bin/less"
        if os.path.exists(lesser):
            sys.stdout = os.popen(lesser, "w")

    summary_files(logfiles, output_steps = output_steps, show_all = show_all, warn_old = warn_old)

if (__name__ == "__main__"):
    result = main(sys.argv)
    sys.exit(result)

