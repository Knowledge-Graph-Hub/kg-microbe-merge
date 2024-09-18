#!/bin/bash
#SBATCH --account=m4689
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --time=60
#SBATCH --ntasks=1
#SBATCH --mem=10GB
#SBATCH --job-name=parallel_merge
#SBATCH --output=parallel_merge_%A_%a.out
#SBATCH --error=parallel_merge_%A_%a.err
#SBATCH --array=0-1
#SBATCH -N 1

module load python/3.10
# conda activate kg-microbe-merge

cd kg-microbe-merge
python -m venv venv-merge
source venv-merge/bin/activate
pip install poetry
poetry install

# Array of merged graph names
merges=(
    kg-microbe-core
    kg-microbe-biomedical
)

# Get the merge for this job array task
merge=${merges[$SLURM_ARRAY_TASK_ID]}

echo "Starting $merge"
time poetry run make $merge
echo "Finished $merge"
