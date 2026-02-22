import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MGOD_DIR = "src/modality_gate_outputs"

FILENAME_RE = re.compile(
    r"modality_gate_([^_]+)_L([0-9]+)_R([0-9.]+)_D([0-9.]+)_M([0-9.]+)_S([0-9]+)"
)

def entropy(alpha):
    eps = 1e-12
    return -np.sum(alpha * np.log(alpha + eps), axis=1)

records = []

for fname in os.listdir(MGOD_DIR):
    if not fname.endswith(".npy"):
        continue

    match = FILENAME_RE.search(fname)
    if not match:
        continue

    dataset, L, R, D, M, S = match.groups()

    path = os.path.join(MGOD_DIR, fname)
    alpha = np.load(path)

    alpha_text = alpha[:, 0]
    alpha_vis  = alpha[:, 1]

    ent = entropy(alpha)

    records.append({
        "dataset": dataset,
        "n_layers": int(L),
        "reg_weight": float(R),
        "dropout": float(D),
        "mm_weight": float(M),
        "seed": int(S),
        "mean_text": alpha_text.mean(),
        "std_text": alpha_text.std(),
        "mean_vis": alpha_vis.mean(),
        "std_vis": alpha_vis.std(),
        "mean_entropy": ent.mean(),
        "std_entropy": ent.std(),
        "pct_text_dominant": np.mean(alpha_text > 0.8),
        "pct_vis_dominant": np.mean(alpha_vis > 0.8),
    })

df = pd.DataFrame(records)

# Save summary CSV
df.to_csv("mgod_summary.csv", index=False)

print("\n=== Dataset-level Summary ===")
print(df.groupby("dataset")[[
    "mean_text",
    "std_text",
    "mean_entropy",
    "pct_text_dominant",
    "pct_vis_dominant"
]].mean())

# Plot histograms per dataset
for dataset in df["dataset"].unique():
    subset = df[df["dataset"] == dataset]

    # concatenate all seeds for that dataset
    alphas = []
    for fname in os.listdir(MGOD_DIR):
        if dataset in fname and fname.endswith(".npy"):
            alphas.append(np.load(os.path.join(MGOD_DIR, fname)))

    if not alphas:
        continue

    alphas = np.vstack(alphas)
    alpha_text = alphas[:, 0]

    plt.figure()
    plt.hist(alpha_text, bins=30)
    plt.title(f"{dataset} - a_text distribution")
    plt.xlabel("a_text")
    plt.ylabel("Count")
    plt.savefig(f"{dataset}_alpha_text_hist.png")
    plt.close()

print("\nSaved mgod_summary.csv and histograms.")
