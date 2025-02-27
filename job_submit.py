#! /usr/bin/env python3

## AUTHOR: DH Kiem
## Last date: 2025-Feb-27

import os, sys
from pathlib import Path
import shutil
import subprocess
#import numpy as np

current_direc = os.getcwd()

base_env_direc = Path(os.getenv("VASP2OPENMX_PATH", current_direc))
openmx_dft_data_path = Path(os.getenv("OPENMX_DFT_DATA_PATH", current_direc))
src_direc = base_env_direc / "src"
sys.path.append(str(src_direc))

#import kp_gen


# Loading existing files
structure_direc = Path("./structures/")  
current_direc = Path(current_direc)
vasp_files = list(structure_direc.glob("*.vasp"))  #
print([file.name for file in vasp_files])

calculation_direc = Path("./calculation/")


run_script = "run_openmx_jx.sbatch"

for vasp_file in vasp_files:
    cal_direc = calculation_direc / vasp_file.stem
        
    run_file = current_direc /  run_script  # run script
    destination_run_file = cal_direc / run_script  # run script
    shutil.copy(run_file, destination_run_file)
    os.chdir(cal_direc)

    result = subprocess.run(["sbatch", run_script], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Submission successful! Job ID: {result.stdout.strip()}")
    else:
        print(f"❌ Submission failed!\nError: {result.stderr.strip()}")    

    os.chdir(current_direc)

