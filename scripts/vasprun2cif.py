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
#       CREATED:  
#      REVISION:  ---
#===============================================================================#
import sys

pi = 3.1415926

#===============================================================================#
#
#  Functions
#
#===============================================================================#

def output_fract(xyz_info, foutput):
    ele_count = 1
    ele_state = ''
    for ele,xyz in xyz_info:
        label = ''
        if ele == ele_state:
            ele_count += 1
        else:
            ele_count = 1
        label = ele.strip() + str(ele_count)
        foutput.writelines('%s  %s %4.5f %4.5f %4.5f\n' % (label, ele, xyz[0], xyz[1], xyz[2]))
        ele_state = ele
    

#===============================================================================#
#
#  Main
#
#===============================================================================#

from p4vasp.SystemPM import *
s=XMLSystemPM(sys.argv[1])
p=s.FINAL_STRUCTURE
p.comment=s.NAME
p.setDirect()

va = p.basis[0]
vb = p.basis[1]
vc = p.basis[2]

a = va.length()
b = vb.length()
c = vc.length()

alpha = vb.angle(vc) / pi * 180.0
beta = va.angle(vc) / pi * 180.0
gamma = va.angle(vb) / pi * 180.0

xyz_info = p.getXYZstructure()
###
# output
#

fcif = open('vasprun.cif', 'w')
fcif.writelines("data_o\n")
fcif.writelines("_audit_creation_method            'vasp2cif'\n")
fcif.writelines("_symmetry_space_group_name_H-M    'P1'\n")
fcif.writelines("loop_\n")
fcif.writelines("_symmetry_equiv_pos_as_xyz\n")
fcif.writelines("  x,y,z\n")
fcif.writelines("_cell_length_a       %10.4f\n" % a)
fcif.writelines("_cell_length_b       %10.4f\n" % b)
fcif.writelines("_cell_length_c       %10.4f\n" % c)
fcif.writelines("_cell_angle_alpha    %10.4f\n" % alpha)
fcif.writelines("_cell_angle_beta     %10.4f\n" % beta)
fcif.writelines("_cell_angle_gamma    %10.4f\n" % gamma)
fcif.writelines("loop_\n")
fcif.writelines("_atom_site_label\n")
fcif.writelines("_atom_site_type_symbol\n")
fcif.writelines("_atom_site_fract_x\n")
fcif.writelines("_atom_site_fract_y\n")
fcif.writelines("_atom_site_fract_z\n")
output_fract(xyz_info, fcif)
fcif.close()

