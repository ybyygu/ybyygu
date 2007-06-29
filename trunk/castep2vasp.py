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
#       CREATED:  2007-4-15
#      REVISION:  2007-5-20
#===============================================================================#

import sys
from os.path import basename, splitext
from os import mkdir, chdir
from glob import glob
#===============================================================================#
#
#  Functions
#
#===============================================================================#
def  kpt2kpoints(filename):
    """
    convert file.kptaux (castep based) into KPOINTS(vasp based)
    """
    txt = open(filename).read().replace('\r', '')
    txts = txt.split('\n')

    mp_grid = []
    mp_offset = []
    for s in txts:
        s = s.strip().split()
        if not s:
            continue
        if s[0].startswith('MP_GRID'):
            mp_grid = s[-3:]
        elif s[0].startswith('MP_OFFSET'):
            mp_offset = s[-3:]

    fkpoints = open('KPOINTS', 'w')
    fkpoints.writelines('Automatic generation\n')
    fkpoints.writelines('0\n')
    fkpoints.writelines('Monhkorst-Pack\n')
    if mp_grid and mp_offset:
        fkpoints.writelines(' '.join(mp_grid) + '\n')
        fkpoints.writelines(' '.join(mp_offset) + '\n')
    fkpoints.close()

def generate_potcar(elements_list):
    """
    generate POTCAR file for vasp calculation
    """
    print 'generate POTCAR in this order: ' + ' '.join(elements_list)

def param2incar(filename):
    """
    convert file.param into INCAR file
    """
    txt = open(filename).read().replace('\r', '')
    txts = txt.split('\n')
    
    fincar = open('INCAR', 'w')
    for line in txts:
        s = line.strip().split()
        if not s:
            continue
        name = s[0] 
        value = ' '.join(s[2:])
        if name == 'task':
            fincar.writelines('SYSTEM = %s\n' % value)
            if value == 'GeometryOptimization':
                fincar.writelines('IBRION = 2')
                fincar.writelines('ISIF = 2')
        elif name == 'cut_off_energy':
            fincar.writelines('ENCUT = %s\n' % value)
        elif name == 'smearing_width':
            fincar.writelines('ISMEAR = 0; SIGMA = %s\n' % value)
        elif name == 'xc_functional':
            if value == 'PBE':
                fincar.writelines('GGA = PE\n')
            elif value == 'PW91':
                fincar.writelines('GGA = 91\n')
                fincar.writelines('VOSKNOWN = 1\n')
        elif name == 'spin_polarized' and value:
            fincar.writelines('ISPIN = 2')
    fincar.close()

def cell2poscar(filename):
    """
    convert cell (vasp based) into INCAR (vasp based)
    """
    txt = open(filename).read()
    txt = txt.replace('\r', '')
    txts = txt.split('%BLOCK ')
    sections = {}

    for s in txts:
        s = s.strip().split('\n')
        name = s[0]
        if s[-1].startswith('%ENDBLOCK'):
            value = s[1:-1]
        else:
            value = []
        if name and value:
            sections[name] = value

    elements_information = {}
    element_information = {'POSITION':[0.0, 0.0, 0.0], 'CONSTRAIN':['T', 'T', 'T']}
    for line in sections['POSITIONS_FRAC']:
        exyz = line.split()
        ele = exyz[0]
        xyz = ['%16.10f' % float(l) for l in exyz[1:]]
        element_information['POSITION'] = xyz
        if not elements_information.has_key(ele):
            elements_information[ele] = []
        elements_information[ele].append(element_information.copy())
    x_constrain = [1, 0, 0]
    y_constrain = [0, 1, 0]
    z_constrain = [0, 0, 1]

    is_constrain = True
    try:
        constrain_info = sections['IONIC_CONSTRAINTS']
    except:
        is_constrain = False
        constrain_info = []

    for line in constrain_info:
        s = line.split()
        ele = s[1]
        ele_index = int(s[2]) - 1
        constrain = [float(l) for l in s[3:]]
        xyz_constrain = elements_information[ele][ele_index]['CONSTRAIN'][:]
        if constrain == x_constrain:
            xyz_constrain[0] = 'F'
        elif constrain == y_constrain:
            xyz_constrain[1] = 'F'
        elif constrain == z_constrain:
            xyz_constrain[2] = 'F'

        elements_information[ele][ele_index]['CONSTRAIN'] = xyz_constrain[:]

    ###
    # output
    #
    system = splitext(basename(filename))[0]
    elements_list = elements_information.keys()
    fincar = open('POSCAR', 'w')
    fincar.writelines('%s # Please generate POTCAR in this order: %s\n' % (system, '\t'.join(elements_list)))
    fincar.writelines('1.0\n')
    fincar.writelines('\n'.join(sections['LATTICE_CART']) + '\n')
    fincar.writelines(' '.join([str(len(elements_information[k])) for k in elements_list]) + '\n')
    if is_constrain:
        fincar.writelines('Selective dynamics\n')
    fincar.writelines('Direct\n')
    if is_constrain:
        for ele in elements_information:
            fincar.writelines('\n'.join([' '.join(p['POSITION'] + p['CONSTRAIN']) for p in elements_information[ele]]) + '\n')
    else:
        for ele in elements_information:
            fincar.writelines('\n'.join([' '.join(p['POSITION']) for p in elements_information[ele]]) + '\n')
    fincar.writelines('\n')
    fincar.close()
    generate_potcar(elements_list)

#===============================================================================#
#
#  Main
#
#===============================================================================#
cellfile = glob('*.cell')[0]
paramfile = glob('*.param')[0]
kptfile = glob('*.kptaux')[0]

print "Never trust this tool! Trust your experience instead!"

if cellfile:
    cell2poscar(cellfile)
else:
    print "WARNING! NO *.cell FILE FOUND IN CURRENT DIRECOTRY!"
if paramfile:
    param2incar(paramfile)
else:
    print "WARNING! NO *.param FILE FOUND IN CURRENT DIRECOTRY!"
if kptfile:
    kpt2kpoints(kptfile)
else:
    print "WARNING! NO *.kptaux FILE FOUND IN CURRENT DIRECOTRY!"
