#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#  REQUIREMENTS:  python
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  2006-8-30 
#      REVISION:  2006-8-31
#===============================================================================#
import sys
from sys import stdin, stderr
from os.path import expanduser, join, exists, isdir, isfile
import glob

DefaultWD = expanduser("~/gjf/work")
DefaultLogfiles = glob.glob(join(DefaultWD, "*.log"))

def SummaryGassianlogFromFiles(gaussian_log_files):
    for log in gaussian_log_files:
        try:
            flog = open(log, 'r')
        except IOError:
            print >>stderr, "Can't open %s to read!" %(log)
            continue

        walklog(flog)
        flog.close()

def SummaryGaussianlogFromStdin():
    return walklog(sys.stdin)

def walklog(flog):
    import re
    
    LineLength = 72

    line = flog.readline()
    
    freq_count = 0
    while line:
        if re.compile(r'^ %').match(line):
            print ' ' + '='*LineLength
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
            print  ' ' + '='*LineLength
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
# print the first line of Eigenvalues
        elif line.find("Eigenvalues ---") >= 0:
            print line,
            while line and line.find("Eigenvalues ---") >=0:
                line = flog.readline()
# print converged information and the next 5 lines
        elif line.find("Converged?") >= 0:
            print " " + '-'*LineLength
            print line, 
            for i in range(5):
                line = flog.readline()
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

def usage(program):
    print 'Usage:'
    print ' %s' % program
    print '   summary ~/gjf/work/*.log'
    print ' %s dir' % program
    print '   summary dir/*.log and dir/*.out'
    print ' %s -h | --help' % program
    print '   show this help screen.'


#==========================================================================
# MAIN PROGRAM
#==========================================================================
def main (argv=None):
    import getopt

    if argv is None:  argv = sys.argv
    
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'h', ['help'])
    except:
        print >>stderr, "Can't parse argument options."
        sys.exit(1)
    
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit(0)

    
    if len(args)>0:
# try to read from stdin
        if args[0] == '-':
            SummaryGaussianlogFromStdin()
        elif isdir(args[0]):
           GaussianLogfiles = glob.glob(join(args[0], "*.log")) + glob.glob(join(args[0], "*.out"))
        else:
            GaussianLogfiles = args
    else:
# try to read from default gaussian output directory if no argv specified
        GaussianLogfiles = DefaultLogfiles
    SummaryGassianlogFromFiles(GaussianLogfiles)

if (__name__ == "__main__"):
    result = main()
    # Comment the next line to use the debugger
    sys.exit(result)
