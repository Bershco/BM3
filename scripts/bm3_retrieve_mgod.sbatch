#!/bin/bash
#SBATCH --job-name=bm3_mgod
#SBATCH --gpus=rtx_6000:1
#SBATCH --time=0-04:00:00
#SBATCH --mem=24G
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=hersco@post.bgu.ac.il
#SBATCH --output=/home/hersco/RecSys_Project/bm3_experiments/mgod_logs/%x-%j.out
#SBATCH --error=/home/hersco/RecSys_Project/bm3_experiments/mgod_logs/%x-%j.err

set -euo pipefail

echo "=== MGOD Retrieval Job ==="
echo "Host: $(hostname)"
echo "Checkpoint: $CKPT_PATH"
echo "Dataset: $DATASET"
echo "Layers: $N_LAYERS"
echo "Reg: $REG_WEIGHT"
echo "Dropout: $DROPOUT"
echo "MM: $MM_WEIGHT"
echo "Seed: $SEED"
echo "=========================="

module load anaconda
source activate RecSys_Project

cd /home/hersco/RecSys_Project/BM3/src/

python main.py \
  --retrieve_mgod \
  --inference_only \
  --load_model True \
  --load_model_path "$CKPT_PATH" \
  -d "$DATASET" \
  --n_layers "$N_LAYERS" \
  --reg_weight "$REG_WEIGHT" \
  --dropout "$DROPOUT" \
  --mm_weight "$MM_WEIGHT" \
  --seed "$SEED"

echo "=== Finished $(date) ==="
