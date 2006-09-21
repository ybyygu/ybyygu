#!/usr/bin/env python
# written by ybyygu at 2006 6/12
# last updated at: 2006 9/2

import re
from math import sin, cos, pi
import sys
from os.path import basename

ATOMS = ('H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S',
         'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge',
         'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
         'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
         'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
         'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm',
         'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt')

class xvib:
    """\
    """
    GaussLogFileName = ''
    FreqVibInfo = []
    AtomsCoordinateInfo = []
    TotalAtomNums = 0
    TotalFreqNums = 0

    def parseGassianLogFile(self, filename):
        """\
        """
        try:
            INPUT = open( filename )
        except IOError:
            print "Can not open %s to read." %( self.GaussLogFileName )
            return 1
        
        self.GaussLogFileName = filename
        # collect standard coordinates information
        # eg.
    
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
    
        while line:
            pattern = rexSTDCoordinates.match(line)
            if pattern:
                self.AtomsCoordinateInfo.append(pattern.groupdict())
            else:
                break
            line = INPUT.readline()
        self.TotalAtomNums = len(self.AtomsCoordinateInfo)
         
        ## collect vibration displacement information
        # eg.
        #                    28                     29                     30
        #                    ?A                     ?A                     ?A
        # Frequencies --  3374.9193              3374.9296              3389.3471
        #  Atom AN      X      Y      Z        X      Y      Z        X      Y      Z
        #    1   6     0.00   0.01   0.00     0.01   0.05   0.00    -0.01  -0.04   0.00
        rexFreqLabel = re.compile(r'^ Frequencies --\s+[\d.-]+')
        rexXYZLabel = re.compile(r'^ Atom AN\s+X\s+Y\s+Z')
        rexXYZ = re.compile(r'^   \d+\s+\d+(\s+(?P<dx>[\d.-]+)\s+(?P<dy>[\d.-]+)\s+(?P<dz>[\d.-]+)){1,3}\s*$')
         
        while line:
            if rexFreqLabel.match(line):
                # jumpt to "Atom AN" line
                while line and not rexXYZLabel.match(line):
                    line = INPUT.readline()
                # collect Atom freq_vib_info
                # We should read Total_Atom_Nums lines, but there alwasy has exception
                temp = ([], [], [])
                for i in range( self.TotalAtomNums ):
                    line = INPUT.readline()
                    pattern = rexXYZ.match(line)
                    if line and pattern:
                        axyz3 = line.split()[2:]
    
                        # from 1 to 3, or else 
                        for j in range(len(axyz3)/3):
                            axyz = axyz3[3*j:3*j+3]
                            temp[j].append( axyz )
                        pattern = rexXYZ.match(line)
                    else:
                        print "?"
                        return
                # sort temp[] with reasonable order
                for j in range( len(axyz3)/3 ):
                    self.FreqVibInfo.append(temp[j])
                
            line = INPUT.readline()
        self.TotalFreqNums = len( self.FreqVibInfo )
        INPUT.close()

    def output2File(self, type = 'xyz', index = 1, scale = 0.5, frames = 10):
        """\
        """
        if index > self.TotalFreqNums :
            print "Freq index %d out of range." % index
            return 1

        if type == 'xyz':
            filename = "%s-freq_index_%s.xyz" %( basename(self.GaussLogFileName), index)
            try:
                OUTPUT = open(filename, 'w')
            except IOError:
                print "Can not open %s to write." % filename
                return 2
         
            for i in range(frames):
                OUTPUT.writelines("%d\n" %( self.TotalAtomNums ))
                OUTPUT.writelines("frame %02d of %s; index: %s, scale: %s\n" % (i+1, frames, index, scale))

                factor = cos(2*pi*i/frames)*scale
                for i in range( self.TotalAtomNums ):
                    nx = float(self.AtomsCoordinateInfo[i]["x"]) + float(self.FreqVibInfo[index-1][i][0])*factor
                    ny = float(self.AtomsCoordinateInfo[i]["y"]) + float(self.FreqVibInfo[index-1][i][1])*factor
                    nz = float(self.AtomsCoordinateInfo[i]["z"]) + float(self.FreqVibInfo[index-1][i][2])*factor
                    OUTPUT.writelines("%3s %11.5f %11.5f %11.5f\n" %( ATOMS[int(self.AtomsCoordinateInfo[i]["atom_num"])-1], nx, ny, nz))

            OUTPUT.close()
            print "Please check %s." % filename 

def usage(progname):
    print 'Usage:', progname, ' [-i index] [-s scale] [-f frames] gauss_logfile'
    print '    gauss_logfile: The gaussian log file which will be parsed'
    print '    -i index: Which freq will be used? you can use this style: 1-3 or 1,3,2'
    print '    -s scale: Use this value to scale the displacement.'
    print '    -f frames: The total frames of output.'

def parseCmdline(argv):
    # default parameters
    INDEX = '1'
    SCALE = 0.5
    FRAMES = 10

    """\
     parse command line options
    """
    import getopt
    
    PROGNAME = argv[0]
    if len(argv)>1:
        try:
            opts, args = getopt.gnu_getopt(argv[1:], "hi:s:f:o:", ['help', 'index=', 'scale=', 'frames=', 'output='])
        except :
            print "Can't parse command line option."
            sys.exit(2)
    else:
        usage(PROGNAME)
        sys.exit(0)

    for o, a in opts:
        if o in ['-h', '--help']:
            usage(PROGNAME)
            sys.exit(0)
        elif o in ['-i', '--index']:
            try:
                if int(a) < 0:
                    print "index should be a positive number."
                    sys.exit(1)
                else:
                    INDEX = [int(a)]
            except ValueError:
                # eg. 2-5
                if re.compile(r'^\d+-(\d+)*$').match(a):
                    INDEX = range(int(a.split('-')[0]), int(a.split('-')[1])+1)
                # eg. 1,3,2,5
                elif re.compile(r'^\d+(,\d+)+$').match(a):
                    INDEX = [ int(f) for f in a.split(',') ]
                else:
                    print "sorry, but I can't recognize your index synatex."
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
        filename = args[0]
        axvib = xvib()
        axvib.parseGassianLogFile(filename)
        if axvib.TotalFreqNums > 0:
            for i in INDEX:
                axvib.output2File(index = i, scale = SCALE, frames = FRAMES)
    else:
        print "You must specify a gaussian log file."
        sys.exit(2)

def main(argv = None):
    """
    """
    if argv == None: argv = sys.argv
    
    parseCmdline(argv)
#------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv)

    
