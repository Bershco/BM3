#!/bin/bash
set -euo pipefail

SBATCH_FILE="{scripts_path}/bm3_single_run.sbatch"

# -------------------------------------------------
# Config tables (MUST match seed sweep script)
# -------------------------------------------------
declare -A ELEC_CFG
ELEC_CFG[1]="2 0.1 0.3 1.0"
ELEC_CFG[2]="1 0.01 0.3 1.0"
ELEC_CFG[3]="2 0.01 0.3 1.0"

declare -A SPORTS_CFG
SPORTS_CFG[1]="1 0.01 0.3 1.0"
SPORTS_CFG[2]="1 0.1 0.3 1.0"
SPORTS_CFG[3]="2 0.1 0.3 1.0"

declare -A BABY_CFG
BABY_CFG[1]="1 0.1 0.5 0.3"
BABY_CFG[2]="1 0.1 0.3 1.0"
BABY_CFG[3]="1 0.01 0.3 1.0"

declare -A CLOTHING_CFG
CLOTHING_CFG[1]="1 0.1 0.5 1.0"
CLOTHING_CFG[2]="1 0.01 0.3 1.0"
CLOTHING_CFG[3]="1 0.01 0.5 1.0"

# -------------------------------------------------
# Helpers
# -------------------------------------------------
get_cfg () {
  local DATASET="$1"
  local ID="$2"

  case "$DATASET" in
    elec)     echo "${ELEC_CFG[$ID]:-}";;
    sports)   echo "${SPORTS_CFG[$ID]:-}";;
    baby)     echo "${BABY_CFG[$ID]:-}";;
    clothing) echo "${CLOTHING_CFG[$ID]:-}";;
    *)        echo "";;
  esac
}

# -------------------------------------------------
# Main loop
# -------------------------------------------------
for JOB in "$@"; do
  echo "======================================"
  echo "Re-running ${JOB}"

  # Case 1: grid search
  if [[ "$JOB" =~ ^bm3_([^_]+)_L([^_]+)_R([^_]+)_D([^_]+)_M([^_]+)$ ]]; then
    DATASET="${BASH_REMATCH[1]}"
    N_LAYERS="${BASH_REMATCH[2]}"
    REG="${BASH_REMATCH[3]}"
    DR="${BASH_REMATCH[4]}"
    MM="${BASH_REMATCH[5]}"
    SEED=999

  # Case 2: seed sweep
  elif [[ "$JOB" =~ ^bm3_([^_]+)_cfg([0-9]+)_seed([0-9]+)$ ]]; then
    DATASET="${BASH_REMATCH[1]}"
    CFG_ID="${BASH_REMATCH[2]}"
    SEED="${BASH_REMATCH[3]}"

    CFG="$(get_cfg "$DATASET" "$CFG_ID")"
    if [[ -z "$CFG" ]]; then
      echo "ERROR: unknown config ${DATASET} cfg${CFG_ID}"
      continue
    fi

    read -r N_LAYERS REG DR MM <<< "$CFG"

  else
    echo "ERROR: unrecognized job name format"
    continue
  fi

  echo "Parsed:"
  echo "  dataset=$DATASET layers=$N_LAYERS reg=$REG drop=$DR mm=$MM seed=$SEED"

  sbatch \
    --job-name="${JOB}_rerun" \
    "${SBATCH_FILE}" \
    "$DATASET" "$N_LAYERS" "$REG" "$DR" "$MM" "$SEED"
done

echo "======================================"
echo "Done"
