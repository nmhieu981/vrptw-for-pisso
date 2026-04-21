"""
Pareto Front Visualization
===========================
2D projections + parallel coordinates for 5-objective MO-VRPTW Pareto fronts.

Objectives:
  Z1 — Number of Vehicles   (minimize)
  Z2 — Total Distance        (minimize)
  Z3 — Total Waiting Time    (minimize)
  Z4 — Load Balance          (minimize)
  Z5 — Makespan              (minimize)
"""

from __future__ import annotations

import os
from typing import Dict, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

OBJ_LABELS = [
    "$Z_1$ (Vehicles)",
    "$Z_2$ (Distance)",
    "$Z_3$ (Wait Time)",
    "$Z_4$ (Balance)",
    "$Z_5$ (Makespan)",
]

PROJECTION_PAIRS = [
    (0, 1),  # Vehicles vs Distance
    (1, 2),  # Distance vs Wait Time
    (1, 4),  # Distance vs Makespan
    (0, 2),  # Vehicles vs Wait Time
    (2, 3),  # Wait Time vs Balance
    (3, 4),  # Balance vs Makespan
]

ALGO_STYLES = {
    "iNSSSO":  {"color": "#2196F3", "marker": "o"},
    "NSSSO":   {"color": "#00BCD4", "marker": "s"},
    "SPEA2":   {"color": "#4CAF50", "marker": "^"},
    "MOEA/D":  {"color": "#FF9800", "marker": "D"},
    "NSGA-II": {"color": "#9C27B0", "marker": "v"},
    "MOPSO":   {"color": "#F44336", "marker": "P"},
}

DEFAULT_STYLE = {"color": "#999999", "marker": "x"}


def plot_pareto_2d(
    all_solutions: Dict[str, np.ndarray],
    instance_name: str,
    true_pf: Optional[np.ndarray] = None,
    save_dir: str = "results",
) -> None:
    """
    Plot 6 key 2D projections of 5-objective Pareto fronts in a 2x3 grid.

    Parameters
    ----------
    all_solutions : {algo_name: ndarray (N, M)}  where M >= 5
    """
    n_cols, n_rows = 3, 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(17, 9))
    fig.suptitle(
        f"Pareto Front — {instance_name}",
        fontsize=15, fontweight="bold", y=0.98,
    )

    for ax_idx, (i, j) in enumerate(PROJECTION_PAIRS):
        row, col = divmod(ax_idx, n_cols)
        ax = axes[row][col]

        for algo_name, objs in all_solutions.items():
            if objs.size == 0:
                continue
            style = ALGO_STYLES.get(algo_name, DEFAULT_STYLE)
            ax.scatter(
                objs[:, i], objs[:, j],
                label=algo_name,
                c=style["color"],
                marker=style["marker"],
                s=30, alpha=0.75, edgecolors="white", linewidths=0.3,
            )

        if true_pf is not None and true_pf.size > 0:
            ax.scatter(
                true_pf[:, i], true_pf[:, j],
                label="True PF",
                facecolors="none", edgecolors="red",
                s=60, linewidths=1.5, zorder=0,
            )

        ax.set_xlabel(OBJ_LABELS[i], fontsize=10)
        ax.set_ylabel(OBJ_LABELS[j], fontsize=10)

        if i == 0:
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        ax.legend(fontsize=7, loc="best", framealpha=0.7)
        ax.grid(True, alpha=0.25, linestyle="--")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"pareto_{instance_name}.png")
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_pareto_parallel(
    all_solutions: Dict[str, np.ndarray],
    instance_name: str,
    save_dir: str = "results",
) -> None:
    """
    Parallel-coordinates plot for 5-objective Pareto fronts.

    Each line is one solution; objectives are normalized to [0, 1] for
    visual comparison. Colour encodes the algorithm.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    x_ticks = np.arange(len(OBJ_LABELS))

    global_min = np.full(5, np.inf)
    global_max = np.full(5, -np.inf)
    for objs in all_solutions.values():
        if objs.size == 0:
            continue
        global_min = np.minimum(global_min, objs[:, :5].min(axis=0))
        global_max = np.maximum(global_max, objs[:, :5].max(axis=0))

    ranges = global_max - global_min
    ranges[ranges < 1e-12] = 1.0

    for algo_name, objs in all_solutions.items():
        if objs.size == 0:
            continue
        style = ALGO_STYLES.get(algo_name, DEFAULT_STYLE)
        normed = (objs[:, :5] - global_min) / ranges

        for row in normed:
            ax.plot(
                x_ticks, row,
                color=style["color"], alpha=0.35, linewidth=0.8,
            )
        ax.plot([], [], color=style["color"], linewidth=2, label=algo_name)

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(OBJ_LABELS, fontsize=10)
    ax.set_ylabel("Normalized value", fontsize=10)
    ax.set_title(
        f"Parallel Coordinates — {instance_name}",
        fontsize=14, fontweight="bold",
    )
    ax.legend(fontsize=9, loc="upper right", framealpha=0.8)
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"parallel_{instance_name}.png")
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_pareto_3d(
    all_solutions: Dict[str, np.ndarray],
    instance_name: str,
    save_dir: str = "results",
) -> None:
    """3D scatter plot using the three continuous objectives Z2, Z3, Z5."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for algo_name, objs in all_solutions.items():
        if objs.size == 0:
            continue
        style = ALGO_STYLES.get(algo_name, DEFAULT_STYLE)
        ax.scatter(
            objs[:, 1], objs[:, 2], objs[:, 4],
            label=algo_name, c=style["color"],
            marker=style["marker"], s=25, alpha=0.7,
        )

    ax.set_xlabel(OBJ_LABELS[1])
    ax.set_ylabel(OBJ_LABELS[2])
    ax.set_zlabel(OBJ_LABELS[4])
    ax.set_title(f"3D Pareto Front — {instance_name}")
    ax.legend(fontsize=8)

    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(
        os.path.join(save_dir, f"pareto3d_{instance_name}.png"),
        dpi=180, bbox_inches="tight",
    )
    plt.close()
