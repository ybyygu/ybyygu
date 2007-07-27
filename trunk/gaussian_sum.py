#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  extract the most important informations from gaussian log files 
# 
#  REQUIREMENTS:  python
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  2006-8-30 
#      REVISION:  2007-07-23
#===============================================================================#
import sys
from sys import stdin, stderr
import os
from os.path import expanduser, join, exists, isdir, isfile, basename, dirname
import glob
from stat import *
import time
import re

LineLength = 72

def centerWithStr(str, char, length):
    nl = (length - len(str))/2
    if nl <= 0:
        str = " ... %s" % str[length + 10:]
        nl = (length - len(str))/2
    return char * nl + str + char * nl

def SummaryGassianlogFromFiles(gaussian_log_files, output_steps=8, show_all=False, warn_old=False):
    global LineLength
    
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
        print "[" + centerWithStr(hint, '=', LineLength) + "]"
        if not show_all:
            if read_backwards(flog, output_steps):
                print " " + ":"* LineLength
        walklog(flog)
        flog.close()
        hint1 = " %s " % dirname(log)
        hint2 = " %s " % basename(log)
        print "[" + centerWithStr(hint1, '=', LineLength) + "]"
        print "[" + centerWithStr(hint2, '=', LineLength) + "]"

        # check outdated log 

        span = (time.time() - os.stat(log)[ST_MTIME]) / 3600
        if warn_old and span > 4:
            print " ** WARNING! THIS FILE HAS NO CHANGE MORE THAN %d HOURS. **" % span

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
        
def usage(program):
    print 'Usage:'
    print ' %s -h | --help' % program
    print '   show this help screen.'
    print ' %s' % program
    print '   summary ~/gjf/work/*.log'
    print ' %s dir' % program
    print '   summary dir/*.log and dir/*.out'


#==========================================================================
# MAIN PROGRAM
#==========================================================================
def main (argv=None):
    import getopt

    if argv is None:  argv = sys.argv
    
    # parse commandline options
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'hn:a', ['help', 'step=', 'showall'])
    except AttributeError:
        try:
            opts, args = getopt.getopt(argv[1:], 'hn:a', ['help', 'step=', 'showall'])
        except:
            print >>stderr, "Can't parse argument options."
            sys.exit(1)
    show_all = False 
    output_steps = 8
    warn_old = False
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit(0)
        elif o in ('-n', '--step'):
            try:
                output_steps = int(a)
            except:
                pass
        elif o in ('-a', '--showall'):
            show_all = True
   # try to read from default gaussian output directory if no argv specified
    logfiles = []
    if not args:
        warn_old = True
        # figure out the most possible working log file
        txt = os.popen('pgrep "g03"').read().strip()
        if not txt:
            txt = os.popen('pgrep "g98"').read().strip()
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
        for a in args:
            if isdir(a):
                logfiles = glob.glob(join(a, "*.log")) + glob.glob(join(a, "*.out"))
            else:
                logfiles.append(a)
    SummaryGassianlogFromFiles(logfiles, output_steps = output_steps, show_all = show_all, warn_old = warn_old)

if (__name__ == "__main__"):
    result = main()
    # Comment the next line to use the debugger
    sys.exit(result)

