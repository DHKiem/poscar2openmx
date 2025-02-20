#! /usr/bin/env python3
import os
import toml
from ase.io import read
#from ase.units import Ha
from ase.units import Ry
from ase.calculators.openmx import OpenMX

# Load TOML config
config = toml.load("config.toml")

general_env_path = os.getenv("VASP2OPENMX_PATH")
if general_env_path is None:
    raise EnvironmentError("'VASP2OPENMX_PATH' was not generated or configured. : 'export VASP2OPENMX_PATH=\"/path/to/config_general.toml\"")
print(general_env_path+"/config_general.toml")

config_general = toml.load(general_env_path+"/config_general.toml")

# Load structure file
atoms = read("POSCAR") # default: POSCAR

# Atomic basis
basis_list = config_general["definition_of_atomic_species"]["definition_of_atomic_species"]
basis_dict = {entry[0]: entry[1:] for entry in basis_list}  # {Element: [Quick, Standard, Precise, VPS]}

selected_basis_type = "Standard"  #  "Quick" | "Standard" | "Precise"

basis_index = {"Quick": 0, "Standard": 1, "Precise": 2}.get(selected_basis_type, 1)
## basis information from POSCAR
atomic_species = [[symbol, basis_dict[symbol][basis_index], basis_dict[symbol][-1]]
                  for symbol in set(atoms.get_chemical_symbols()) if symbol in basis_dict]

# Load magnetic moments from TOML
default_magnetic_moments = config_general.get("default_magnetic_moments", {})
custom_magnetic_moments = config.get("magnetic_moments", {}).get("magmom", [])

magmom_list = [
    custom_magnetic_moments[i] if i < len(custom_magnetic_moments) else default_magnetic_moments.get(symbol, 0.0)
    for i, symbol in enumerate(atoms.get_chemical_symbols())
]
#magmom_dict = config_general.get("magmom", {})  
#magmom_list = [magmom_dict.get(symbol, 0.0) for symbol in atoms.get_chemical_symbols()]  

# magnetic moments
atoms.set_initial_magnetic_moments(magmom_list)

# OpenMX settings
calc = OpenMX(
    label         = config.get("label", "openmx"),
    xc            = config.get("xc",    "PBE"),
    energy_cutoff = config.get("energycutoff", 400 *Ry),
    scf_kgrid     = tuple(config.get("scf_kgrid", [9, 9, 9])),
    eigensolver   = config.get("scf_eigensolver", "Band"),
    scf_criterion = config.get("scf_criterion", 1e-7),
    maxiter       = config.get("scf_maxiter", 300),
    mixer         = config.get("scf_mixer",  "Rmm-Diish"),
    definition_of_atomic_species=atomic_species,  
)
##

# SAVE openmx.dat 
atoms.calc = calc
calc.write_input(atoms)

print(f"INPUT file: '{config.get('label', 'openmx')}.dat' created. ")

# Adding some keywords
dat_filename  = f"{config.get('label', 'openmx')}.dat"
hs_fileout    = config.get("hs_fileout", "on") #HS.fileout                
scf_hubbard_u = config.get("scf_hubbard_u", "off") #HS.fileout                  off
scf_init_mixing = config.get("scf_init_mixing_weight", "0.03")
scf_min_mixing = config.get("scf_min_mixing_weight", "0.001")
scf_max_mixing = config.get("scf_max_mixing_weight", "0.08")
scf_minxing_history = config.get("scf_mixing_history", "25")
scf_mixing_start = config.get("scf_mixing_startpulay", "26")
scf_mixing_every = config.get("scf_mixing_everypulay", "1")


with open(dat_filename, "a") as f:  # append mode
    f.write("\n#outside of ase\n")
    #f.write(f"\nscf.maxIter {scf_maxIter}\n")
    f.write(f"HS.fileout {hs_fileout}\n")   
    f.write(f"scf.Hubbard.U {scf_hubbard_u}\n")    
    f.write(f"scf.Init.Mixing.Weight    {scf_init_mixing}        # default=0.30\n")
    f.write(f"scf.Min.Mixing.Weight     {scf_min_mixing}        # default=0.001\n")
    f.write(f"scf.Max.Mixing.Weight     {scf_max_mixing}        # default=0.40\n")
    f.write(f"scf.Mixing.History        {scf_minxing_history}         # default=5\n")
    f.write(f"scf.Mixing.StartPulay     {scf_mixing_start}        # default=6\n")
    f.write(f"scf.Mixing.EveryPulay     {scf_mixing_every}        \n")


# To be Added
# Band
#band.dispersion  on

# DFT+U
#scf.Hubbard.U    off
#scf.DFTU.Type    off




