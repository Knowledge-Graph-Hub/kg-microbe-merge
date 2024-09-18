#!/bin/bash
#SBATCH --account=m4689
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --time=1200
#SBATCH --mem=200GB
#SBATCH --ntasks=1
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -N 1

# conda activate kg-microbe-merge
module load python/3.10
cd kg-microbe-merge
python -m venv venv-merge
source venv-merge/bin/activate
pip install poetry
poetry install

time make kg-microbe-function