#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright © 2005 ybyygu
#
# This file is part of gaussian_sum.py.
#
# gaussian_sum.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# gaussian_sum.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gaussian_sum.py; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  
# USA

#===============================================================================#
#   DESCRIPTION:  
# 
#  REQUIREMENTS:  python
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  2006-8-30 
#      REVISION:  2006-11-30
#===============================================================================#

import sys
from sys import stdin, stderr
import os
from os.path import expanduser, join, exists, isdir, isfile, basename
import glob
from stat import *
import time

default_logfiles = glob.glob(expanduser("~/gjf/work/*.log"))
LineLength = 72

def SummaryGassianlogFromFiles(gaussian_log_files, output_steps, warn_old = False):
    global LineLength
    
    def log_cmp(x, y):
        x = os.stat(x)[ST_MTIME]
        y = os.stat(y)[ST_MTIME]
        return cmp(x,y)

    gaussian_log_files.sort(log_cmp)

    for log in gaussian_log_files:
        try:
            flog = open(log, 'r')
        except IOError:
            print >>stderr, "Can't open %s to read!" %(log)
            continue
        hint = " %s " % basename(log)
        print "[" + "="*((LineLength - len(hint))/2) + hint + "="*((LineLength - len(hint))/2) + "]"
        if read_backwards(flog, output_steps):
            print " " + ":"* LineLength
        walklog(flog)
        flog.close()
        hint = " %s " % basename(log)
        print "[" + "="*((LineLength - len(hint))/2) + hint + "="*((LineLength - len(hint))/2) + "]"

        # check outdated log 

        span = (time.time() - os.stat(log)[ST_MTIME]) / 3600
        if warn_old and span > 4:
            print " ** WARNING! THIS FILE HAS NO CHANGE MORE THAN %d H. **" % span

def SummaryGaussianlogFromStdin():
    return walklog(sys.stdin)

def walklog(flog):
    import re
    
    global LineLength
    line = flog.readline()
    freq_count = 0
# gaussian log file begins with a space
    if not line or not line[0] == ' ':
        print ' ' + '*'*LineLength
        print ' this is not a gaussian log file...'
        return

    while line:
        if re.compile(r'^ %').match(line):
            while line and re.compile(r'^ %').match(line):
                print line,
                line = flog.readline()
        elif re.compile(r'^ #').match(line):
            print  ' ' + '-'*LineLength
            print line,
            for i in range(3):
                line = flog.readline()
                if re.compile(r'^ -').match(line):
                    break
                else:
                    print line,
            print  ' ' + '-'*LineLength
        elif line.find("Number of steps in this run=") >= 0:
            print line,
# print SCF information and the next two lines
        elif line.find("SCF Done") >= 0:
            print line,
            for i in range(2):
                line = flog.readline()
                print line,
            print " " + '-'*LineLength
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
            print " " + '-'*LineLength
            print line, 
            for i in range(7):
                line = flog.readline()
                if line.find('GradGradGrad') >=0:
                    break
                print line,
            print  " " + '-'*LineLength
        elif line.find("Frequencies --") >= 0:
            freq_count += 1
            if freq_count == 1:
                print line,
        elif line.find("Zero-point correction=") >= 0:
            print line,
        elif line.find("Sum of electronic and zero-point Energies=") >= 0:
            print line,
            print " " + '-'*LineLength
        elif line.find("termination") >= 0:
            print line,
        elif line.find("Job cpu time:") >= 0:
            print line,
        line = flog.readline()

def read_backwards(fp, maxrounds = 5, sizehint = 20000):
    """\
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
        except:
            fp.seek(0, 0)
            return False

        pos = fp.read(sizehint).rfind(' Step number')
        fp.seek(-sizehint, 1)
        if pos != -1:
            fp.seek(pos, 1)
            round += 1
        elif fp.tell() == 0:
            return False
        else:
            continue

    return True
        
def usage(program):
    print 'Usage:'
    print ' %s' % program
    print '   summary ~/gjf/work/*.log'
    print ' %s dir' % program
    print '   summary dir/*.log and dir/*.out'
    print ' %s -h | --help' % program
    print '   show this help screen.'

################################################################################
#
#	Main Program
#
################################################################################

def main (argv=None):
    import getopt

    if argv is None:  argv = sys.argv
    
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'hin:', ['help', 'install', 'step='])
    except AttributeError:
        try:
            opts, args = getopt.getopt(argv[1:], 'hin:', ['help', 'install', 'step='])
        except:
            print >>stderr, "Can't parse argument options."
            sys.exit(1)
   
    output_steps = 5 
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit(0)
        elif o in ('-i', '--install'):
            if args:
                for s in args:
                    os.system("scp %s %s:%s/bin/" % (argv[0], s, os.getenv('HOME')))
            else:
                print "No sites specified."
            sys.exit(0)
        elif o in ('-n', '--step'):
            try:
                output_steps = int(a)
            except:
                output_steps = 5
            

# try to read from default gaussian output directory if no argv specified
    if len(argv)==1:
        SummaryGassianlogFromFiles(default_logfiles, output_steps, warn_old = True)
        return 0
# try to read from stdin
    elif argv[1] == '-':
        SummaryGaussianlogFromStdin()
        return 0
    elif args:
        if isdir(args[0]):
            GaussianLogfiles = glob.glob(join(args[0], "*.log")) + glob.glob(join(args[0], "*.out"))
        else:
            GaussianLogfiles = args
        SummaryGassianlogFromFiles(GaussianLogfiles, output_steps)
        return 0

if (__name__ == "__main__"):
    result = main()
    # Comment the next line to use the debugger
    sys.exit(result)
