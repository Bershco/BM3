#!/bin/bash
set -euo pipefail

# Directory containing .pth files
CHECKPOINT_DIR="$1"

if [ ! -d "$CHECKPOINT_DIR" ]; then
    echo "Directory does not exist: $CHECKPOINT_DIR"
    exit 1
fi

LOG_DIR="{output_path}/mgod_logs"
mkdir -p "$LOG_DIR"

SBATCH_FILE="{scripts_path}/bm3_retrieve_mgod.sbatch"

echo "Scanning directory: $CHECKPOINT_DIR"
echo

for CKPT in "$CHECKPOINT_DIR"/*.pth; do

    FNAME=$(basename "$CKPT")

    # Example:
    # stacking-BM3-baby-n_layers=1-reg_weight=0.01-dropout=0.3-mm_weight=1.0-seed=42-....pth

    DATASET=$(echo "$FNAME" | sed -n 's/.*-BM3-\([^-]*\)-.*/\1/p')
    N_LAYERS=$(echo "$FNAME" | sed -n 's/.*n_layers=\([0-9]*\).*/\1/p')
    REG_WEIGHT=$(echo "$FNAME" | sed -n 's/.*reg_weight=\([0-9.]*\).*/\1/p')
    DROPOUT=$(echo "$FNAME" | sed -n 's/.*dropout=\([0-9.]*\).*/\1/p')
    MM_WEIGHT=$(echo "$FNAME" | sed -n 's/.*mm_weight=\([0-9.]*\).*/\1/p')
    SEED=$(echo "$FNAME" | sed -n 's/.*seed=\([0-9]*\).*/\1/p')

    if [ -z "$DATASET" ]; then
        echo "Skipping $FNAME (could not parse)"
        continue
    fi

    echo "Submitting: $FNAME"
    echo "  Dataset: $DATASET | L=$N_LAYERS R=$REG_WEIGHT D=$DROPOUT M=$MM_WEIGHT S=$SEED"

    sbatch \
        --export=ALL,CKPT_PATH="$CKPT",DATASET="$DATASET",N_LAYERS="$N_LAYERS",REG_WEIGHT="$REG_WEIGHT",DROPOUT="$DROPOUT",MM_WEIGHT="$MM_WEIGHT",SEED="$SEED" \
        --job-name="mgod_${DATASET}_L${N_LAYERS}_M${MM_WEIGHT}_S${SEED}" \
        "$SBATCH_FILE"
    echo
done

echo "All jobs submitted."
