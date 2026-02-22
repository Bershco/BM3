import re
import csv
from pathlib import Path
from collections import defaultdict

# -------------------------------------------------
# Configuration
# -------------------------------------------------
LOG_DIR = Path("/home/hersco/RecSys_Project/bm3_experiments/logs_v2_0")
OUT_FILE = "bm3_top3_config_by_dataset_make_sure.csv"

METRICS = [
    "recall@10",
    "recall@20",
    "ndcg@10",
    "ndcg@20",
]

SELECT_METRIC = "recall@10"
TOP_K = 3

# -------------------------------------------------
# Regex
# -------------------------------------------------
FILENAME_RE = re.compile(r"(bm3_([^_]+)_.*)\.(out|err)$")

BEST_BLOCK_RE = re.compile(
    r"█████████████ BEST ████████████████(.*?)(?:\n\n|\Z)",
    re.S
)

# -------------------------------------------------
# Group log files by job (prefer .err)
# -------------------------------------------------
jobs = defaultdict(dict)

for log_file in LOG_DIR.glob("bm3_*.*"):
    m = FILENAME_RE.match(log_file.name)
    if not m:
        continue
    job_key, dataset, ext = m.groups()
    jobs[job_key][ext] = log_file

# -------------------------------------------------
# Parse logs
# -------------------------------------------------
results_by_dataset = defaultdict(list)

for job_key, files in jobs.items():
    log_file = files.get("err") or files.get("out")
    if log_file is None:
        continue

    text = log_file.read_text(errors="ignore")
    best_blocks = BEST_BLOCK_RE.findall(text)
    if not best_blocks:
        continue

    for block in best_blocks:
        # TEST metrics only
        test_match = re.search(r"Test:(.*)", block, re.S)
        if not test_match:
            continue

        test_block = test_match.group(1)

        metrics = {}
        for m in METRICS:
            mm = re.search(rf"{m}:\s*([0-9.]+)", test_block)
            if not mm:
                break
            metrics[m] = float(mm.group(1))
        else:
            dataset = FILENAME_RE.match(log_file.name).group(2)

            record = {
                "dataset": dataset,
                **metrics,
                "job": job_key,
                "log_file": log_file.name,
            }

            results_by_dataset[dataset].append(record)

# -------------------------------------------------
# Select TOP-K per dataset
# -------------------------------------------------
topk_by_dataset = {}

for dataset, records in results_by_dataset.items():
    records_sorted = sorted(
        records,
        key=lambda r: r[SELECT_METRIC],
        reverse=True,
    )
    topk_by_dataset[dataset] = records_sorted[:TOP_K]

# -------------------------------------------------
# Write CSV
# -------------------------------------------------
fieldnames = ["dataset"] + METRICS + ["job", "log_file"]

with open(OUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for dataset, records in topk_by_dataset.items():
        for r in records:
            writer.writerow(r)

# -------------------------------------------------
# Pretty print to terminal
# -------------------------------------------------
print(f"\nTop-{TOP_K} configurations per dataset (by TEST {SELECT_METRIC})\n")

for dataset, records in topk_by_dataset.items():
    print(f"Dataset: {dataset}")
    for i, r in enumerate(records, 1):
        print(
            f"  #{i}: "
            f"recall@10={r['recall@10']:.4f}, "
            f"recall@20={r['recall@20']:.4f}, "
            f"ndcg@10={r['ndcg@10']:.4f}, "
            f"ndcg@20={r['ndcg@20']:.4f} "
            f"({r['job']})"
        )
    print()

print(f"Wrote {OUT_FILE}")
