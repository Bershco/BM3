import re
import csv
import math
from pathlib import Path
from collections import defaultdict
from scipy.stats import ttest_ind

# ============================================================
# PATH
# ============================================================
LOG_DIR = Path("{output_path}/logs_seeds")

OUT_RESULTS = "bm3_results_long.csv"
OUT_STATS   = "bm3_significance.csv"

METRICS = ["recall@10", "recall@20", "ndcg@10", "ndcg@20"]
PRIMARY = "recall@10"

# ============================================================
# PAPER RESULTS
# ============================================================
PAPER = {
    "baby":        {"recall@10":0.0564,"recall@20":0.0883,"ndcg@10":0.0301,"ndcg@20":0.0383},
    "sports":      {"recall@10":0.0656,"recall@20":0.0980,"ndcg@10":0.0355,"ndcg@20":0.0438},
    "electronics": {"recall@10":0.0437,"recall@20":0.0648,"ndcg@10":0.0247,"ndcg@20":0.0302},
}

# ============================================================
# Utilities
# ============================================================
def norm(ds):
    return "electronics" if ds=="elec" else ds

def mean(xs): return sum(xs)/len(xs)

def std(xs):
    if len(xs)<=1: return 0.0
    m=mean(xs)
    return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def fmt(m,s=None):
    return f"{m:.4f}" if s is None else f"{m:.4f} ± {s:.4f}"

def welch(x,y):
    return ttest_ind(x,y,equal_var=False).pvalue

def student(x,y):
    return ttest_ind(x,y,equal_var=True).pvalue

# ============================================================
# REGEX
# ============================================================
BEST_RE = re.compile(r"█████████████ BEST ████████████████(.*?)(?:\n\n|\Z)", re.S)
SEED_RE = re.compile(r"bm3_([^_]+)_cfg(\d+)_seed(\d+)")

# ============================================================
# Parse all seed logs
# ============================================================
def parse_logs():
    data = defaultdict(lambda: defaultdict(list))

    for f in LOG_DIR.glob("bm3_*.*"):
        m = SEED_RE.search(f.name)
        if not m: continue

        dataset = norm(m.group(1))
        cfg_id  = m.group(2)

        text = f.read_text(errors="ignore")
        blocks = BEST_RE.findall(text)
        if not blocks: continue
        block = blocks[-1]

        test = re.search(r"Test:(.*)", block, re.S)
        if not test: continue
        tb = test.group(1)

        metrics = {}
        for k in METRICS:
            mk = re.search(rf"{k}:\s*([0-9.]+)", tb)
            if not mk: break
            metrics[k] = float(mk.group(1))
        else:
            data[dataset][cfg_id].append(metrics)

    return data

# ============================================================
# MAIN
# ============================================================
def main():
    data = parse_logs()

    datasets = sorted(set(list(data.keys()) + list(PAPER.keys())))

    # --------------------------------------------------------
    # RESULTS TABLE (long format)
    # --------------------------------------------------------
    with open(OUT_RESULTS,"w",newline="",encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["dataset","method"]+METRICS)

        for ds in datasets:

            # PAPER
            if ds in PAPER:
                w.writerow([ds,"paper"]+[fmt(PAPER[ds][m]) for m in METRICS])

            # RESTORED (cfg0)
            if ds in data and "0" in data[ds]:
                rows = data[ds]["0"]
                means = {m:mean([r[m] for r in rows]) for m in METRICS}
                stds  = {m:std([r[m] for r in rows])  for m in METRICS}
                w.writerow([ds,"restored"]+[fmt(means[m],stds[m]) for m in METRICS])

            # ADAPTER (best among cfg1/2/3)
            if ds in data:
                best_cfg = None
                best_score = None

                for cfg_id, rows in data[ds].items():
                    if cfg_id == "0": continue
                    score = mean([r[PRIMARY] for r in rows])
                    if best_score is None or score>best_score:
                        best_score=score
                        best_cfg=(cfg_id,rows)

                if best_cfg:
                    cfg_id, rows = best_cfg
                    means = {m:mean([r[m] for r in rows]) for m in METRICS}
                    stds  = {m:std([r[m] for r in rows])  for m in METRICS}

                    # delta %
                    if ds in data and "0" in data[ds]:
                        restored_means = {
                            m:mean([r[m] for r in data[ds]["0"]])
                            for m in METRICS
                        }
                        row_vals=[]
                        for m in METRICS:
                            delta = 100*(means[m]-restored_means[m])/restored_means[m]
                            row_vals.append(fmt(means[m],stds[m]) + f" ({delta:+.2f}%)")
                        w.writerow([ds,"adapter"]+row_vals)
                    else:
                        w.writerow([ds,"adapter"]+[fmt(means[m],stds[m]) for m in METRICS])

    # --------------------------------------------------------
    # SIGNIFICANCE TABLE
    # --------------------------------------------------------
    with open(OUT_STATS,"w",newline="",encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["dataset","metric","delta_percent","p_welch","p_student"])

        for ds in datasets:
            if ds not in data: continue
            if "0" not in data[ds]: continue

            restored_vals = {
                m:[r[m] for r in data[ds]["0"]]
                for m in METRICS
            }

            # best adapter
            best_cfg=None
            best_score=None
            for cfg_id, rows in data[ds].items():
                if cfg_id=="0": continue
                score=mean([r[PRIMARY] for r in rows])
                if best_score is None or score>best_score:
                    best_score=score
                    best_cfg=(cfg_id,rows)

            if not best_cfg: continue
            cfg_id, rows = best_cfg
            adapter_vals = {
                m:[r[m] for r in rows]
                for m in METRICS
            }

            for m in METRICS:
                r_mean=mean(restored_vals[m])
                a_mean=mean(adapter_vals[m])
                delta=100*(a_mean-r_mean)/r_mean

                p_w = welch(adapter_vals[m], restored_vals[m])
                p_s = student(adapter_vals[m], restored_vals[m])

                w.writerow([ds,m,f"{delta:.2f}%",p_w,p_s])

    print("Finished.")
    print("Created:",OUT_RESULTS,"and",OUT_STATS)

if __name__=="__main__":
    main()
