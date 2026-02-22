import re
import csv
import math
from pathlib import Path
from collections import defaultdict

# =================================================
# Configuration
# =================================================
LOG_DIR = Path("/home/hersco/RecSys_Project/bm3_experiments/logs_seeds_2")
OUT_FILE = "bm3_seed_2_aggregated_results.csv"

METRICS = [
    "recall@10",
    "recall@20",
    "ndcg@10",
    "ndcg@20",
]

# =================================================
# Regex
# =================================================

# Matches:
# bm3_<dataset>_cfg<id>_seed<seed>-<jobid>.out / .err
FILENAME_RE = re.compile(
    r"(bm3_([^_]+)_cfg(\d+)_seed(\d+)).*\.(out|err)$"
)

BEST_BLOCK_RE = re.compile(
    r"█████████████ BEST ████████████████(.*?)(?:\n\n|\Z)",
    re.S
)

# =================================================
# Helpers
# =================================================
def mean(xs):
    return sum(xs) / len(xs)

def std(xs):
    if len(xs) <= 1:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

# =================================================
# Group log files by job (prefer .err)
# =================================================
jobs = defaultdict(dict)

for log_file in LOG_DIR.glob("bm3_*.*"):
    m = FILENAME_RE.match(log_file.name)
    if not m:
        continue

    job_key, dataset, cfg_id, seed, ext = m.groups()
    jobs[job_key][ext] = log_file

print(f"Detected {len(jobs)} job(s)")

# =================================================
# Parse logs
# =================================================
results = defaultdict(lambda: defaultdict(list))
seeds_seen = defaultdict(set)

for job_key, files in jobs.items():
    # Prefer stderr
    log_file = files.get("err") or files.get("out")
    if log_file is None:
        continue

    m = FILENAME_RE.match(log_file.name)
    _, dataset, cfg_id, seed, _ = m.groups()

    text = log_file.read_text(errors="ignore")
    blocks = BEST_BLOCK_RE.findall(text)
    if not blocks:
        continue

    # Use LAST BEST block (BM3-safe)
    block = blocks[-1]

    # TEST metrics ONLY
    test_match = re.search(r"Test:(.*)", block, re.S)
    if not test_match:
        continue

    test_block = test_match.group(1)

    for metric in METRICS:
        mm = re.search(rf"{metric}:\s*([0-9.]+)", test_block)
        if not mm:
            break
        results[(dataset, cfg_id)][metric].append(float(mm.group(1)))
    else:
        seeds_seen[(dataset, cfg_id)].add(int(seed))

# =================================================
# Write CSV
# =================================================
fieldnames = (
    ["dataset", "config_id", "num_seeds"]
    + [f"{m}_mean" for m in METRICS]
    + [f"{m}_std" for m in METRICS]
    + [f"{m}_mean_pm" for m in METRICS]
)

with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for (dataset, cfg_id), metric_dict in sorted(results.items()):
        row = {
            "dataset": dataset,
            "config_id": cfg_id,
            "num_seeds": len(seeds_seen[(dataset, cfg_id)]),
        }

        for m in METRICS:
            vals = metric_dict[m]
            m_mean = mean(vals)
            m_std = std(vals)

            row[f"{m}_mean"] = m_mean
            row[f"{m}_std"] = m_std
            row[f"{m}_mean_pm"] = f"{m_mean:.4f} ± {m_std:.4f}"

        writer.writerow(row)

# =================================================
# Terminal summary
# =================================================
print("\nAggregated TEST results (mean ± std)\n")

for (dataset, cfg_id), metric_dict in sorted(results.items()):
    print(f"Dataset: {dataset}, Config {cfg_id}, Seeds: {len(seeds_seen[(dataset, cfg_id)])}")
    for m in METRICS:
        vals = metric_dict[m]
        print(f"  {m}: {mean(vals):.4f} ± {std(vals):.4f}")
    print()

print(f"Wrote {OUT_FILE}")
