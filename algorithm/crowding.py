"""
Shift-based Density Estimation (SDE) + Reference Direction Niching
===================================================================
Replaces Crowding Distance for many-objective optimization (M >= 4).

SDE: Li et al., "Shift-Based Density Estimation for Pareto-Based
     Algorithms in Many-Objective Optimization", IEEE TEC, 2014.
Niching: Deb & Jain, NSGA-III, IEEE TEC, 2014.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from algorithm.nondominated import fast_nondominated_sort
from algorithm.reference_dirs import (
    normalize_objectives,
    associate_to_directions,
    niching_selection,
)


# ─── Epsilon tolerance for detecting duplicate objectives ──────────
_EPS_DUP = 1e-6


def sde_density(objectives: np.ndarray) -> np.ndarray:
    """
    Vectorised Shift-based Density Estimation (SDE).

    For each solution i, compute the minimum shifted Euclidean distance
    to any other solution j.  The "shift" operation replaces each objective
    of j with max(f_m(j), f_m(i)), pushing j away from the ideal point
    relative to i.

    This version is **fully vectorised** using NumPy broadcasting:
        shifted[i,j,m] = max(norm[j,m], norm[i,m])
        dist[i,j] = ||shifted[i,j,:] - norm[i,:]||₂
        sde[i] = min_{j≠i} dist[i,j]

    Complexity: O(N² M) time, O(N² M) memory.
    ~10-50x faster than the scalar loop for N ≤ 500.

    Higher SDE = more isolated (better for diversity).
    Lower SDE = more crowded (candidate for removal).
    """
    N, M = objectives.shape
    if N <= 1:
        return np.full(N, np.inf)

    ideal = objectives.min(axis=0)
    nadir = objectives.max(axis=0)
    ranges = nadir - ideal
    ranges = np.where(ranges < 1e-10, 1.0, ranges)
    norm = (objectives - ideal) / ranges

    # Broadcasting: norm_i (N,1,M) vs norm_j (1,N,M) → shifted (N,N,M)
    norm_i = norm[:, np.newaxis, :]   # (N, 1, M)
    norm_j = norm[np.newaxis, :, :]   # (1, N, M)
    shifted = np.maximum(norm_j, norm_i)  # (N, N, M)
    diff = shifted - norm_i               # (N, N, M)
    dists = np.sqrt(np.sum(diff ** 2, axis=2))  # (N, N)

    # Mask self-distances
    np.fill_diagonal(dists, np.inf)

    sde = dists.min(axis=1)  # (N,)
    return sde


def assign_rank_and_sde(
    objectives: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform non-dominated sorting then compute SDE density (replaces CD).

    Returns
    -------
    ranks : ndarray shape (N,)
    sde_vals : ndarray shape (N,) — higher = more isolated = better
    """
    n = objectives.shape[0]
    ranks = np.full(n, n, dtype=int)
    sde_vals = np.zeros(n)

    fronts = fast_nondominated_sort(objectives)
    for rank, front in enumerate(fronts):
        for idx in front:
            ranks[idx] = rank
        # Compute SDE within each front
        if len(front) <= 2:
            for idx in front:
                sde_vals[idx] = np.inf
        else:
            front_obj = objectives[np.array(front)]
            front_sde = sde_density(front_obj)
            for i, idx in enumerate(front):
                sde_vals[idx] = front_sde[i]

    return ranks, sde_vals


# ─── Legacy backward-compatible aliases ────────────────────────────
def crowding_distance(objectives, front_indices, normalize=True):
    """Legacy CD — kept for backward compatibility but not used in main loop."""
    n_front = len(front_indices)
    if n_front <= 2:
        return np.full(n_front, np.inf)

    n_obj = objectives.shape[1]
    front_obj = objectives[front_indices].copy()
    if normalize:
        for m in range(n_obj):
            f_min, f_max = front_obj[:, m].min(), front_obj[:, m].max()
            rng = f_max - f_min
            if rng > 0:
                front_obj[:, m] = (front_obj[:, m] - f_min) / rng

    cd = np.zeros(n_front)
    for m in range(n_obj):
        sorted_idx = np.argsort(front_obj[:, m])
        cd[sorted_idx[0]] = np.inf
        cd[sorted_idx[-1]] = np.inf
        f_min, f_max = front_obj[sorted_idx[0], m], front_obj[sorted_idx[-1], m]
        denom = f_max - f_min
        if denom == 0:
            continue
        for i in range(1, n_front - 1):
            cd[sorted_idx[i]] += (front_obj[sorted_idx[i+1], m] - front_obj[sorted_idx[i-1], m]) / denom
    return cd


def assign_rank_and_crowding(objectives):
    """Legacy — calls SDE-based version for backward compatibility."""
    return assign_rank_and_sde(objectives)


# ═══════════════════════════════════════════════════════════════════
#  Selection Operators
# ═══════════════════════════════════════════════════════════════════

def _find_unique_indices(objectives: np.ndarray, eps: float = _EPS_DUP) -> List[int]:
    """Return indices of unique solutions (remove duplicates within eps)."""
    n = objectives.shape[0]
    if n == 0:
        return []
    unique = [0]
    for i in range(1, n):
        is_dup = False
        for j in unique:
            if np.all(np.abs(objectives[i] - objectives[j]) < eps):
                is_dup = True
                break
        if not is_dup:
            unique.append(i)
    return unique


def select_best(
    objectives: np.ndarray,
    n_select: int,
    ref_dirs: Optional[np.ndarray] = None,
) -> List[int]:
    """
    Select best n_select solutions using NDS + SDE + Reference Direction Niching.

    Process:
    1. Non-dominated sort → fronts
    2. Add fronts until we exceed n_select
    3. For the last (boundary) front, use niching selection:
       - Associate solutions to closest reference direction
       - Prioritize niches with fewest members
       - Break ties with SDE (prefer most isolated)
    """
    n = objectives.shape[0]
    fronts = fast_nondominated_sort(objectives)

    # Compute SDE for ALL solutions (needed for niching tie-break)
    _, sde_vals = assign_rank_and_sde(objectives)

    selected: List[int] = []

    # Remove duplicates — mark them
    unique_set = set(_find_unique_indices(objectives))

    for rank, front in enumerate(fronts):
        # Filter duplicates from this front
        unique_front = [idx for idx in front if idx in unique_set]
        dup_front = [idx for idx in front if idx not in unique_set]

        # Prefer unique solutions
        candidates = unique_front + dup_front

        if len(selected) + len(candidates) <= n_select:
            selected.extend(candidates)
        else:
            # Need to pick from this front — use niching if ref_dirs available
            n_remaining = n_select - len(selected)

            if ref_dirs is not None and len(ref_dirs) > 0:
                # Compute niche counts for already-selected solutions
                ideal = objectives.min(axis=0)
                nadir = objectives.max(axis=0)
                norm_obj = normalize_objectives(objectives, ideal, nadir)

                niche_counts = np.zeros(len(ref_dirs), dtype=int)
                if selected:
                    sel_norm = norm_obj[np.array(selected)]
                    sel_assignments = associate_to_directions(sel_norm, ref_dirs)
                    for a in sel_assignments:
                        niche_counts[a] += 1

                chosen = niching_selection(
                    objectives=objectives,
                    front_indices=candidates,
                    n_select=n_remaining,
                    ref_dirs=ref_dirs,
                    sde_values=sde_vals,
                    existing_assignments=np.array([]),
                    existing_niche_counts=niche_counts,
                )
                selected.extend(chosen)
            else:
                # Fallback: sort by SDE (highest = most isolated first)
                candidates.sort(key=lambda i: -sde_vals[i])
                selected.extend(candidates[:n_remaining])
            break

    return selected[:n_select]


def select_gbest(
    pareto_indices: List[int],
    sde_vals: np.ndarray,
) -> int:
    """
    Choose gbest from Pareto front via binary tournament on SDE.
    Higher SDE = more isolated = preferred for exploration.
    """
    n = len(pareto_indices)
    if n <= 1:
        return pareto_indices[0] if n == 1 else 0

    i1, i2 = np.random.choice(n, size=2, replace=False)
    idx1 = pareto_indices[i1]
    idx2 = pareto_indices[i2]

    sd1 = sde_vals[idx1]
    sd2 = sde_vals[idx2]

    if np.isinf(sd1) and np.isinf(sd2):
        return pareto_indices[np.random.choice([i1, i2])]
    elif np.isinf(sd1):
        return idx1
    elif np.isinf(sd2):
        return idx2
    else:
        return idx1 if sd1 >= sd2 else idx2
