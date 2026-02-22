#!/bin/bash
set -euo pipefail

# -------------------------------------------------
# Seeds (EDIT FREELY)
# -------------------------------------------------
SEEDS=(999 0 123 42 420 82 2026 1337 31415 1111999)

SBATCH_FILE="/home/hersco/RecSys_Project/BM3/bm3_single_run.sbatch"

# -------------------------------------------------
# ELEC – top 3 configs
# -------------------------------------------------
ELEC_CONFIGS=(
  "2 0.1 0.3 1.0"
  "1 0.01 0.3 1.0"
  "2 0.01 0.3 1.0"
)

ELEC_CONFIGS_RESTORED=(
  "2 0.1 0.5 0.0"
)

# -------------------------------------------------
# SPORTS – top 3 configs
# -------------------------------------------------
SPORTS_CONFIGS=(
  "1 0.01 0.3 1.0"
  "1 0.1 0.3 1.0"
  "2 0.1 0.3 1.0"
)

SPORTS_CONFIGS_RESTORED=(
  "1 0.01 0.5 0.0"
)

# -------------------------------------------------
# BABY – top 3 configs
# -------------------------------------------------
BABY_CONFIGS=(
  "1 0.1 0.5 0.3"
  "1 0.1 0.3 1.0"
  "1 0.01 0.3 1.0"
)

BABY_CONFIGS_RESTORED=(
  "1 0.1 0.3 0.0"
)

# -------------------------------------------------
# CLOTHING – top 3 configs
# -------------------------------------------------
CLOTHING_CONFIGS=(
  "1 0.1 0.5 1.0"
  "1 0.01 0.3 1.0"
  "1 0.01 0.5 1.0"
)

CLOTHING_CONFIGS_RESTORED=(
  "1 0.01 0.3 0.0"
)

# -------------------------------------------------
# Submission helper
# -------------------------------------------------
submit_group () {
  local DATASET="$1"
  shift
  local CONFIGS=("$@")

  for i in "${!CONFIGS[@]}"; do
    CFG_ID=$((i + 1))
    read -r N_LAYERS REG_WEIGHT DROPOUT MM_WEIGHT <<< "${CONFIGS[$i]}"

    for SEED in "${SEEDS[@]}"; do
      JOB_NAME="bm3_${DATASET}_cfg${CFG_ID}_seed${SEED}"

      echo "Submitting ${JOB_NAME}"

      sbatch \
        --job-name="${JOB_NAME}" \
        "${SBATCH_FILE}" \
        "${DATASET}" \
        "${N_LAYERS}" \
        "${REG_WEIGHT}" \
        "${DROPOUT}" \
        "${MM_WEIGHT}" \
        "${SEED}"
    done
  done
}

# -------------------------------------------------
# Launch all seed sweeps
# -------------------------------------------------
submit_group elec   "${ELEC_CONFIGS[@]}"
submit_group sports "${SPORTS_CONFIGS[@]}"
submit_group baby  "${BABY_CONFIGS[@]}"
submit_group clothing  "${CLOTHING_CONFIGS[@]}"

#submit_group elec   "${ELEC_CONFIGS_RESTORED[@]}"
#submit_group sports "${SPORTS_CONFIGS_RESTORED[@]}"
#submit_group baby  "${BABY_CONFIGS_RESTORED[@]}"
#submit_group clothing  "${CLOTHING_CONFIGS_RESTORED[@]}"

echo "======================================"
echo "Seed sweep submission complete"
echo "======================================"
