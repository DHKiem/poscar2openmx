#!/usr/bin/env python3
##########################
# This code is written for generation of K-meshes for VASP, i.e. KPOINTS
# To generate openmx input, the kpoint will be made as Monkhorst-Pack scheme
# Developer : Do Hoon Kiem
# Last update as a module : 2025-Feb-27
version = "v0.1.4_kgen"
##########################

import numpy as np
from numpy import linalg as LA
import sys
import os 

def generate_kmesh(inputfile, LK):
  # reead poscar file lines
  F = open(inputfile,"r")
  L = F.readlines()
  F.close()
  #### poscar file format ####
  # sysmtemname
  # 1.0     #volumetric_parameter
  #4.18 2.09 2.09 #a lattice vec
  #2.09 4.18 2.09 #b
  #2.09 2.09 4.18 #c
  #   Ni  O  #elements
  #### poscar file format ####
  
  #lattice parameter in Angstrom
  a=np.array(L[2].split()[0:3]).astype(np.float64)
  b=np.array(L[3].split()[0:3]).astype(np.float64)
  c=np.array(L[4].split()[0:3]).astype(np.float64)
  
  #print("Your lattice parameters: ")
  #LK = float(input("How many K points in a unit length of reciprocal space? (# per 2π/Angstrom)\n=> ")) 
  ## Brillouin zone unitcell (1/Angstrom)^-1 \n=> "))
  
  #print("Do not use this code for slab calculation.\n")
  
  ka = LK/LA.norm(a) / np.cos(np.arctan2(LA.norm(np.cross(a,np.cross(b,c))),np.dot(a,np.cross(b,c))))
  kb = LK/LA.norm(b) / np.cos(np.arctan2(LA.norm(np.cross(b,np.cross(c,a))),np.dot(b,np.cross(c,a))))
  kc = LK/LA.norm(c) / np.cos(np.arctan2(LA.norm(np.cross(c,np.cross(a,b))),np.dot(c,np.cross(a,b))))
  
  ka=int(round(ka,0))
  kb=int(round(kb,0))
  kc=int(round(kc,0))
  save_kpoints(ka,kb,kc)

  #print("The K-mesh:")
  #print(ka, kb, kc)
  #if 'Y' == input("Do you want write 'KPOINTS' file? [y/N]\n=> ").upper():
  #  if os.path.isfile("KPOINTS"):
  #    if 'Y' == input("There exist ALREADY KPOINTS file. Do you want really rewrite KPOINTS? [y/N]\n=> ").upper():
  #      save_kpoints(ka,kb,kc)
  #  else:
  #    save_kpoints(ka,kb,kc)
  
  #print("Finished. Thanks, See you again.")
  

#saving kpoints?
def save_kpoints(ka,kb,kc):
  #GM = input("Choose K-mesh type of 'G' (gamma-centered) or 'M' (Monkhorst-Pack scheme)\n=> ")
  #if not(GM == "G" or GM == "M"):
  #  print("Please check your type.")
  #  exit() 
  GM = "M"
  F_kpoint=open("KPOINTS","w") 
  F_kpoint.write("normal\n0\n")
  F_kpoint.write(GM+"\n")
  kline=str(ka)+" "+str(kb)+" "+str(kc)+"\n"
  F_kpoint.write(kline)
  F_kpoint.write("0 0 0")
  F_kpoint.close()
  #print("KPOINTS created.\n")


########## START MAIN ############
#print("Hello! Thanks for using this code.")
print("KP-gen VERSION:",version)
#print("How to use: 'python THISCODE poscar.vasp[default=POSCAR]'\n")

#inputfile = 'POSCAR'
#if len(sys.argv) > 1:
#    inputfile = sys.argv[1]
#else:
#    inputfile = 'POSCAR'
#
#
#print("Your input file= ", inputfile,"\n")
#
#filecheck = os.path.isfile(inputfile)
#
#if filecheck:
#   generate_kmesh(inputfile)
#else:
#   print("No input structure file. Check your input. The default input is 'POSCAR'")
#   exit()
  
########## Finish MAIN ############
  
