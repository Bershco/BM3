#!/bin/bash
set -euo pipefail

DATASETS=(
  baby
  elec
  sports
)

SBATCH_FILE="bm3.sbatch"

for DATASET in "${DATASETS[@]}"; do
    JOB_NAME="bm3_${DATASET}"

    echo "Submitting BM3 job for dataset: ${DATASET}"

    sbatch \
        --job-name="${JOB_NAME}" \
        --output="slurm-${JOB_NAME}-%j.out" \
        --error="slurm-${JOB_NAME}-%j.err" \
        "${SBATCH_FILE}" "${DATASET}"
done
