#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gpus=rtx_6000:1
#SBATCH --time=2-00:00:00
#SBATCH --mem=48G
#SBATCH --mail-type=FAIL
#SBATCH --mail-user={email}
#SBATCH --job-name=bm3
#SBATCH --output={output_path}/%x-%j.out
#SBATCH --error={output_path}/%x-%j.err

set -euo pipefail

# -------------------------------
# Arguments
# -------------------------------
DATASET="$1"
N_LAYERS="$2"
REG_WEIGHT="$3"
DROPOUT="$4"
MM_WEIGHT="$5"
SEED="$6"

if [[ -z "${SEED:-}" ]]; then
    echo "ERROR: missing arguments"
    echo "Usage: sbatch bm3_single_run.sbatch <dataset> <n_layers> <reg_weight> <dropout> <mm_weight> <seed>"
    exit 1
fi

echo "======================================"
echo "BM3 SINGLE RUN"
echo "Dataset     : ${DATASET}"
echo "n_layers    : ${N_LAYERS}"
echo "reg_weight  : ${REG_WEIGHT}"
echo "dropout     : ${DROPOUT}"
echo "mm_weight   : ${MM_WEIGHT}"
echo "seed        : ${SEED}"
echo "Host        : $(hostname)"
echo "Job ID      : ${SLURM_JOB_ID}"
echo "Start time  : $(date)"
echo "======================================"

# -------------------------------
# Environment setup (CRITICAL)
# -------------------------------
module load anaconda

# Proper conda init for non-interactive shells
source "$(conda info --base)/etc/profile.d/conda.sh"

conda activate RecSys_Project

echo "Using python: $(which python)"
python - << 'EOF'
import torch
print("Torch OK:", torch.__version__)
EOF

# -------------------------------
# Run BM3
# -------------------------------
cd /home/hersco/RecSys_Project/BM3/src/

python main.py -m BM3 -d "${DATASET}" \
  --n_layers "${N_LAYERS}" \
  --reg_weight "${REG_WEIGHT}" \
  --dropout "${DROPOUT}" \
  --mm_weight "${MM_WEIGHT}" \
  --seed "${SEED}"

echo "======================================"
echo "Finished at $(date)"
echo "======================================"
