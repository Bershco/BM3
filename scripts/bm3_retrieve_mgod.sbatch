#!/bin/bash
#SBATCH --job-name=bm3_mgod
#SBATCH --gpus=rtx_6000:1
#SBATCH --time=0-04:00:00
#SBATCH --mem=24G
#SBATCH --mail-type=FAIL
#SBATCH --mail-user={email}
#SBATCH --output={output_path}/mgod_logs/%x-%j.out
#SBATCH --error={output_path}/mgod_logs/%x-%j.err

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
source activate {conda_env_name}

cd {main.py_path}

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
