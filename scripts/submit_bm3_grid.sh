#!/bin/bash
set -euo pipefail

# -------------------------------
# Grid definition
# -------------------------------
DATASETS=(baby elec sports clothing)
#DATASETS=(clothing)
N_LAYERS=(1 2)
REG_WEIGHT=(0.1 0.01)
DROPOUT=(0.3 0.5)
MM_WEIGHT=(0)
#MM_WEIGHT=(0 0.3 0.7 1.0)
SEED=999

SBATCH_FILE="/home/hersco/RecSys_Project/BM3/bm3_single_run.sbatch"

TOTAL=0

for DATASET in "${DATASETS[@]}"; do
  for NL in "${N_LAYERS[@]}"; do
    for REG in "${REG_WEIGHT[@]}"; do
      for DR in "${DROPOUT[@]}"; do
        for MM in "${MM_WEIGHT[@]}"; do

          JOB_NAME="bm3_${DATASET}_L${NL}_R${REG}_D${DR}_M${MM}"

          echo "Submitting ${JOB_NAME}"

          sbatch \
            --job-name="${JOB_NAME}" \
            "${SBATCH_FILE}" \
            "${DATASET}" "${NL}" "${REG}" "${DR}" "${MM}" "${SEED}"

          TOTAL=$((TOTAL + 1))

        done
      done
    done
  done
done

echo "======================================"
echo "Submitted ${TOTAL} BM3 jobs"
echo "======================================"
