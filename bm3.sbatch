#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gpus=rtx_6000:1
#SBATCH --time=5-00:00:00
#SBATCH --mem=48G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hersco@post.bgu.ac.il
#SBATCH --job-name=bm3_PLACEHOLDER
#SBATCH --output=slurm-bm3_PLACEHOLDER-%j.out
#SBATCH --error=slurm-bm3_PLACEHOLDER-%j.err

set -euo pipefail

# -------------------------------
# Arguments
# -------------------------------
DATASET="$1"

if [[ -z "${DATASET}" ]]; then
    echo "ERROR: Dataset name not provided"
    exit 1
fi

echo "=== BM3 Job Started ==="
echo "Dataset      : ${DATASET}"
echo "Host         : $(hostname)"
echo "SLURM Job ID : ${SLURM_JOB_ID}"
echo "Start time   : $(date)"

# -------------------------------
# Environment setup
# -------------------------------
module load anaconda
source activate RecSys_Project

# (optional but recommended on cluster)
export CUDA_VISIBLE_DEVICES=0

# -------------------------------
# Run BM3
# -------------------------------
cd /home/hersco/RecSys_Project/BM3/src/

python main.py -m BM3 -d "${DATASET}"

echo "=== Job Finished at $(date) ==="
