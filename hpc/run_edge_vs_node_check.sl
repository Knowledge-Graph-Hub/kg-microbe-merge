#!/bin/bash
#SBATCH --account=m4689
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --time=360
#SBATCH --mem=470GB
#SBATCH --ntasks=1
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -N 1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=MJoachimiak@lbl.gov

module load python/3.10

cd /global/cfs/cdirs/m4689/master/kg-microbe-merge
source venv-merge/bin/activate

time poetry run python kg_microbe_merge/utils/edge_vs_node_check.py

