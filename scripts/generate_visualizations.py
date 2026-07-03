"""Generate the two report visualizations from results/full/summary.json:
1. Accuracy heatmap (3 models x 3 tasks)
2. Precision vs. recall scatter (9 points: 3 models x 3 tasks)

Palette and mark specs follow the project's dataviz skill: sequential blue
ramp for magnitude (heatmap), fixed-order categorical slots for model
identity (scatter), direct labels as the relief channel for low-contrast
categorical slots.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(REPO_ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

with open(os.path.join(REPO_ROOT, "results", "full", "summary.json")) as f:
    summary = json.load(f)

MODELS = ["qwen", "llama", "gemma"]
MODEL_LABELS = {"qwen": "Qwen3 1.7B", "llama": "Llama 3.2 1B", "gemma": "Gemma 3 1B"}
TASKS = ["qa", "dialogue", "summarization"]
TASK_LABELS = {"qa": "QA", "dialogue": "Dialogue", "summarization": "Summarization"}

# ---- palette (dataviz skill reference instance) ----
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

# sequential blue ramp, light -> dark (100 -> 700)
SEQ_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# categorical slots 1-3 (fixed order: blue, aqua, yellow)
CAT_COLORS = {"qwen": "#2a78d6", "llama": "#1baf7a", "gemma": "#eda100"}
TASK_MARKERS = {"qa": "o", "dialogue": "s", "summarization": "^"}

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["text.color"] = INK_PRIMARY
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["axes.labelcolor"] = INK_SECONDARY
plt.rcParams["xtick.color"] = INK_MUTED
plt.rcParams["ytick.color"] = INK_MUTED


def luminance_ink(hex_color):
    """Return white or ink text color depending on fill luminance."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return "#ffffff" if L < 0.4 else INK_PRIMARY


# ============================================================
# Chart 1: Accuracy heatmap
# ============================================================
acc_matrix = np.array([
    [summary[f"{m}_{t}"]["accuracy"] for t in TASKS] for m in MODELS
])

fig, ax = plt.subplots(figsize=(7, 4.2), facecolor=PAGE)
ax.set_facecolor(SURFACE)

# custom colormap from the sequential ramp
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("seq_blue", SEQ_RAMP, N=256)

# HaluEval discrimination is a balanced binary task, so 0.50 = chance.
# Anchor the color scale at a fixed range so cell shading reflects genuine
# distance from chance rather than auto-scaling to this run's narrow spread.
vmin, vmax = 0.40, 0.60
im = ax.imshow(acc_matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

ax.set_xticks(range(len(TASKS)))
ax.set_xticklabels([TASK_LABELS[t] for t in TASKS], fontsize=11)
ax.set_yticks(range(len(MODELS)))
ax.set_yticklabels([MODEL_LABELS[m] for m in MODELS], fontsize=11)
ax.tick_params(length=0)

for spine in ax.spines.values():
    spine.set_visible(False)

for i in range(len(MODELS)):
    for j in range(len(TASKS)):
        val = acc_matrix[i, j]
        cell_hex_idx = int((val - vmin) / (vmax - vmin) * (len(SEQ_RAMP) - 1))
        cell_hex_idx = max(0, min(len(SEQ_RAMP) - 1, cell_hex_idx))
        txt_color = luminance_ink(SEQ_RAMP[cell_hex_idx])
        ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                fontsize=13, fontweight="medium", color=txt_color)

# 2px surface-color gridlines between cells (the surface gap, not a border)
ax.set_xticks(np.arange(-0.5, len(TASKS), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(MODELS), 1), minor=True)
ax.grid(which="minor", color=SURFACE, linewidth=3)
ax.tick_params(which="minor", length=0)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.06)
cbar.set_label("Accuracy", fontsize=10, color=INK_SECONDARY)
cbar.ax.tick_params(labelsize=9, color=INK_MUTED, labelcolor=INK_MUTED)
cbar.outline.set_visible(False)
cbar.ax.axhline(0.5, color=INK_PRIMARY, linewidth=1, linestyle=(0, (2, 2)))

ax.set_title("HaluEval Discrimination Accuracy by Model and Task",
             fontsize=13, fontweight="bold", color=INK_PRIMARY, pad=14, loc="left")
fig.text(0.02, 0.02,
         "Dashed line on scale = chance baseline (0.50). All 9 cells sit within "
         "±6pp of chance — no model reliably beats random guessing.",
         fontsize=8.5, color=INK_MUTED, ha="left")

fig.tight_layout(rect=[0, 0.05, 1, 1])
heatmap_path = os.path.join(FIG_DIR, "accuracy_heatmap.png")
fig.savefig(heatmap_path, dpi=300, facecolor=PAGE)
plt.close(fig)
print(f"Saved {heatmap_path}")

# ============================================================
# Chart 2: Precision vs. Recall scatter
# ============================================================
fig, ax = plt.subplots(figsize=(8, 5.5), facecolor=PAGE)
ax.set_facecolor(SURFACE)

for spine in ax.spines.values():
    spine.set_visible(False)
ax.spines["left"].set_visible(True)
ax.spines["bottom"].set_visible(True)
ax.spines["left"].set_color(BASELINE)
ax.spines["bottom"].set_color(BASELINE)

ax.grid(True, color=GRIDLINE, linewidth=1, zorder=0)
ax.set_axisbelow(True)

# chance-baseline reference lines (precision=0.5 under this balanced design)
ax.axhline(0.5, color=BASELINE, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
ax.axvline(0.5, color=BASELINE, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
ax.text(0.83, 0.615, "precision = chance", fontsize=8, color=INK_MUTED, ha="left", va="bottom")
ax.text(0.515, 0.365, "recall = chance", fontsize=8, color=INK_MUTED, ha="left", va="bottom", rotation=90)

# Direct per-point labels are dropped: the tight llama cluster (recall 0.84-1.00,
# precision 0.50) makes every label placement collide. Identity is fully recoverable
# from the color (model) + shape (task) legend, and exact values live in the
# accompanying metrics table (results/full/summary.json) -- that table is the
# contrast-WARN relief channel for the aqua/yellow slots, not per-point text.
for m in MODELS:
    for t in TASKS:
        d = summary[f"{m}_{t}"]
        x, y = d["recall"], d["precision"]
        ax.scatter(x, y, s=170, color=CAT_COLORS[m], marker=TASK_MARKERS[t],
                   edgecolors=SURFACE, linewidths=2, zorder=3)

ax.set_xlim(-0.03, 1.05)
ax.set_ylim(0.35, 0.75)
ax.set_xlabel("Recall  (share of true hallucinations caught)", fontsize=10.5)
ax.set_ylabel("Precision  (share of “Yes” judgements that were correct)", fontsize=10.5)
ax.set_title("Precision vs. Recall Trade-off by Model and Task",
             fontsize=13, fontweight="bold", color=INK_PRIMARY, pad=14, loc="left")

# legend: color = model (categorical), shape = task
model_handles = [mpatches.Patch(color=CAT_COLORS[m], label=MODEL_LABELS[m]) for m in MODELS]
shape_handles = [plt.Line2D([0], [0], marker=TASK_MARKERS[t], color=INK_MUTED,
                             linestyle="None", markersize=8, label=TASK_LABELS[t])
                  for t in TASKS]
leg1 = ax.legend(handles=model_handles, title="Model", loc="upper left",
                  bbox_to_anchor=(1.02, 1.0), frameon=False, fontsize=9, title_fontsize=9.5)
ax.add_artist(leg1)
ax.legend(handles=shape_handles, title="Task (shape)", loc="upper left",
          bbox_to_anchor=(1.02, 0.62), frameon=False, fontsize=9, title_fontsize=9.5)

fig.text(0.02, 0.045,
         "Llama clusters at precision≈chance with high recall (always-“Yes” bias).",
         fontsize=8.5, color=INK_MUTED, ha="left")
fig.text(0.02, 0.015,
         "Gemma clusters at low recall (always-“No” bias); Qwen is the only model off both edges.",
         fontsize=8.5, color=INK_MUTED, ha="left")

fig.tight_layout(rect=[0, 0.08, 0.80, 1])
scatter_path = os.path.join(FIG_DIR, "precision_recall_scatter.png")
fig.savefig(scatter_path, dpi=300, facecolor=PAGE)
plt.close(fig)
print(f"Saved {scatter_path}")
