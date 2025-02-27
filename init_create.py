#! /usr/bin/env python3

## AUTHOR: DH Kiem
## Last date: 2025-Feb-23

import os, sys
from pathlib import Path
import shutil
import subprocess
import numpy as np

current_direc = os.getcwd()

base_env_direc = Path(os.getenv("VASP2OPENMX_PATH", current_direc))
openmx_dft_data_path = Path(os.getenv("OPENMX_DFT_DATA_PATH", current_direc))
src_direc = base_env_direc / "src"
sys.path.append(str(src_direc))

import kp_gen


# Loading existing files
structure_direc = Path("./structures/")  
vasp_files = list(structure_direc.glob("*.vasp"))  #
print([file.name for file in vasp_files])

# Makding calculation directories
calculation_direc = Path("./calculation/")
calculation_direc.mkdir(parents=True, exist_ok=True)
config_direc = Path("./configfile/")
config_file = config_direc / "config.toml"


def ch_kgrid(config, kpoints):

    configfile = Path(config)  
    kpfile = Path(kpoints)  

    with kpfile.open("r") as f:
        lines = f.readlines()

    kgrid_values = [int(x) for x in lines[3].strip().split()]  

    with configfile.open("r") as f:
        config_lines = f.readlines()

    new_lines = [
        f"scf_kgrid = {kgrid_values}\n" if "scf_kgrid = 'autogen'" in line else line
        for line in config_lines
    ]

    with configfile.open("w") as f:
        f.writelines(new_lines)

    #print(f"Updated scf_kgrid to: {kgrid_values} in {file1_path}")
    
    return kgrid_values

def make_mft_toml(filename, kgrid_values):
    mft_tomlfile = Path(filename)
    kgrids = np.array(kgrid_values)
    mft_kgrids = np.ceil(kgrids / 2).astype(int) 

    with mft_tomlfile.open("w") as f:
        f.writelines("HamiltonianType = \"OpenMX\" \n")
        f.writelines("spintype = \"co_spin\" \n")
        f.writelines("result_file = \"openmx.scfout\" \n")
        f.writelines("atom12 = [ \n")
        f.writelines("[4,4], [4,5], [4,6], \n")
        f.writelines("[5,4], [5,5], [5,6], \n")
        f.writelines("[6,4], [6,5], [6,6], \n")
        f.writelines("] \n")
        f.writelines(f"k_point_num = [{','.join(map(str, mft_kgrids))}]\n")
        f.writelines(f"q_point_num = [{','.join(map(str, mft_kgrids))}]\n")


for vasp_file in vasp_files:
    cal_direc = calculation_direc / vasp_file.stem
    cal_direc.mkdir(parents=True, exist_ok=True)

    destination_file = cal_direc / "POSCAR"  # POSCAR
    shutil.copy(vasp_file, destination_file)

    destination_file2 = cal_direc / "config.toml" # config.toml
    shutil.copy(config_file, destination_file2)

    print(f"Created directory: {cal_direc} & POSCAR file copied")
    
    # Create K-grids when 'autogen'
    os.chdir(cal_direc)
    kp_gen.generate_kmesh("POSCAR", 60.0)    
    kgrid_values = ch_kgrid("config.toml", "KPOINTS")

    # Create K-path using vaspkit
    process = subprocess.Popen(["vaspkit"], stdin=subprocess.PIPE, text=True)
    process.communicate("303\n")  

    kpath_file = Path("KPATH.in")
    with kpath_file.open("r") as file:
        lines = file.readlines()

    kpath_lines = lines[4:] # from vasp format
    formatted_openmx_lines = [] # for openmx format

    for i in range(0, len(kpath_lines), 3):
        if i+1 < len(kpath_lines):
            line1 = kpath_lines[i].strip().split()
            line2 = kpath_lines[i+1].strip().split()

            k1 = "  ".join(line1[:3])
            k2 = "  ".join(line2[:3])
            klabel1 = line1[-1]
            klabel2 = line2[-1]

            formatted_openmx_lines.append(f"20 {k1}   {k2}   {klabel1} {klabel2}")

    # vasp2openmx
    vasp2openmx = "vasp2openmx.py"  

    # This part should be imported in this python process in the future. !!!!
    try:
        subprocess.run([vasp2openmx], check=True)
        #print("Converted to openmx file")
    except subprocess.CalledProcessError as e:
    
        print(f"Execution failed: {e}")

    
    
    #kpath_openmx = Path("kpath_openmx.dat")
    # appending kpath to openmx.dat
    #with kpath_openmx.open("w") as f:
    openmx_inputfile = Path("openmx.dat")
    with openmx_inputfile.open("a") as f:
        f.writelines("\n\nband.dispersion        on\n")
        f.writelines(f"Band.Nkpath  {len(formatted_openmx_lines)}\n")
        f.writelines("<Band.kpath\n")
        f.writelines("\n".join(formatted_openmx_lines))
        f.writelines("\nBand.kpath>")

    #kpath_openmx.write_text(f"Band.Nkpath  {len(formatted_openmx_lines)}\n")
    #kpath_openmx.write_text("<Band.kpath\n")
    #kpath_openmx.write_text("\n".join(formatted_openmx_lines))
    #kpath_openmx.write_text("Band.kpath>")

    replacement_directorypath = "System.CurrrentDirectory         ./    # default=./"
    with openmx_inputfile.open("r") as f:
        lines = f.readlines()
    new_lines = [replacement_directorypath + "\n" if "System.CurrentDirectory" in line else line for line in lines]
    with openmx_inputfile.open("w") as f:
        f.writelines(new_lines) 
        

    make_mft_toml("MFT.toml", kgrid_values)

    
        
        
    # vasp2openmx
    #vasp2openmx = "vasp2openmx.py"  




    os.chdir(current_direc)

