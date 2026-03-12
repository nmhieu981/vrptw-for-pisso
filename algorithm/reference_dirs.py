"""
Reference Directions (Das-Dennis) + Preference-Biased Sampling
===============================================================
Generates well-distributed reference directions on the M-dimensional
unit simplex for many-objective optimization (NSGA-III style niching).

References:
    Das & Dennis, "Normal-Boundary Intersection", SIAM J. Optim., 1998.
    Deb & Jain, IEEE TEC, 2014.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Optional

import numpy as np


def das_dennis(n_partitions: int, n_objectives: int) -> np.ndarray:
    """
    Generate uniformly distributed reference directions on the unit simplex
    using the Das-Dennis systematic approach.

    Parameters
    ----------
    n_partitions : int (H)
        Number of divisions along each objective axis.
    n_objectives : int (M)
        Number of objectives.

    Returns
    -------
    dirs : ndarray shape (N_dirs, M)
        Each row sums to 1.0, all values in [0, 1].
    """
    def _recursive(M, H, d, result, current):
        if d == M - 1:
            current[d] = H
            result.append(current.copy() / n_partitions)
            return
        for i in range(H + 1):
            current[d] = i
            _recursive(M, H - i, d + 1, result, current)

    ref_points = []
    _recursive(n_objectives, n_partitions, 0, ref_points,
               np.zeros(n_objectives))
    return np.array(ref_points)


def preference_biased_dirs(
    n_objectives: int,
    g: np.ndarray,
    w: np.ndarray,
    n_total: int = 105,
    pref_ratio: float = 0.7,
) -> np.ndarray:
    """
    Generate reference directions with preference bias.

    70% of directions are clustered around the preference direction
    (derived from weight vector w), and 30% are uniformly distributed
    across the full simplex.

    Parameters
    ----------
    n_objectives : M
    g : reference point (aspiration)
    w : weight vector (importance)
    n_total : approximate total number of directions desired
    pref_ratio : fraction of directions clustered around preference

    Returns
    -------
    dirs : ndarray shape (N, M), each row sums to ~1.0
    """
    # --- Uniform layer ---
    n_uniform = max(int(n_total * (1 - pref_ratio)), 10)
    # Choose H so that C(H+M-1, M-1) is close to n_uniform
    H_uniform = _find_partitions(n_objectives, n_uniform)
    uniform_dirs = das_dennis(H_uniform, n_objectives)

    # --- Preference layer ---
    n_pref = n_total - len(uniform_dirs)
    if n_pref <= 0:
        return uniform_dirs

    # Preference center = normalized weight vector
    center = w / (w.sum() + 1e-15)

    # Generate dense directions around center via perturbation
    H_pref = _find_partitions(n_objectives, n_pref * 2)
    dense_dirs = das_dennis(H_pref, n_objectives)

    # Shift towards preference center
    alpha = 0.5  # blend factor: 0 = full simplex, 1 = all at center
    shifted = (1 - alpha) * dense_dirs + alpha * center[np.newaxis, :]
    # Re-normalize to sum=1
    shifted = shifted / shifted.sum(axis=1, keepdims=True)

    # Keep only the closest n_pref directions to center
    dists = np.linalg.norm(shifted - center[np.newaxis, :], axis=1)
    closest_idx = np.argsort(dists)[:n_pref]
    pref_dirs = shifted[closest_idx]

    # Combine
    all_dirs = np.vstack([uniform_dirs, pref_dirs])

    # Remove near-duplicates
    all_dirs = _remove_duplicates(all_dirs, tol=1e-4)

    return all_dirs


def _find_partitions(M: int, target_n: int) -> int:
    """Find H such that C(H+M-1, M-1) is closest to target_n."""
    from math import comb
    best_H = 1
    for H in range(1, 50):
        n = comb(H + M - 1, M - 1)
        if n >= target_n:
            return H
        best_H = H
    return best_H


def _remove_duplicates(dirs: np.ndarray, tol: float = 1e-4) -> np.ndarray:
    """Remove near-duplicate directions."""
    if len(dirs) <= 1:
        return dirs
    unique = [dirs[0]]
    for i in range(1, len(dirs)):
        is_dup = False
        for u in unique:
            if np.linalg.norm(dirs[i] - u) < tol:
                is_dup = True
                break
        if not is_dup:
            unique.append(dirs[i])
    return np.array(unique)


# ═══════════════════════════════════════════════════════════════════
#  Association & Niching (NSGA-III style)
# ═══════════════════════════════════════════════════════════════════

def normalize_objectives(
    objectives: np.ndarray,
    ideal: Optional[np.ndarray] = None,
    nadir: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Normalize objectives to [0, 1] using ideal and nadir points.
    """
    if ideal is None:
        ideal = objectives.min(axis=0)
    if nadir is None:
        nadir = objectives.max(axis=0)

    ranges = nadir - ideal
    ranges = np.where(ranges < 1e-10, 1.0, ranges)
    return (objectives - ideal) / ranges


def associate_to_directions(
    norm_objectives: np.ndarray,
    ref_dirs: np.ndarray,
) -> np.ndarray:
    """
    Associate each solution to the closest reference direction.

    Uses perpendicular distance from each solution to each reference line.

    Parameters
    ----------
    norm_objectives : (N, M)  normalized objectives
    ref_dirs : (D, M)  reference directions (unit simplex)

    Returns
    -------
    assignments : (N,)  index of closest ref direction per solution
    """
    N = norm_objectives.shape[0]
    D = ref_dirs.shape[0]

    # For each ref dir d, the perpendicular distance of point p is:
    # d_perp = ||p - (p·d / d·d) * d||
    assignments = np.zeros(N, dtype=int)

    for i in range(N):
        p = norm_objectives[i]
        min_dist = np.inf
        for j in range(D):
            d = ref_dirs[j]
            # Project p onto direction d
            dd = np.dot(d, d)
            if dd < 1e-15:
                continue
            proj_scalar = np.dot(p, d) / dd
            proj = proj_scalar * d
            perp_dist = np.linalg.norm(p - proj)

            if perp_dist < min_dist:
                min_dist = perp_dist
                assignments[i] = j

    return assignments


def niching_selection(
    objectives: np.ndarray,
    front_indices: List[int],
    n_select: int,
    ref_dirs: np.ndarray,
    sde_values: np.ndarray,
    existing_assignments: np.ndarray,
    existing_niche_counts: np.ndarray,
) -> List[int]:
    """
    NSGA-III style niching to select solutions from the last front.

    Prioritizes solutions belonging to niches (ref dirs) with fewest
    existing members. Breaks ties using SDE (lower = more isolated = preferred).

    Parameters
    ----------
    objectives : full objective matrix
    front_indices : indices of solutions in the boundary front
    n_select : how many to pick from this front
    ref_dirs : reference directions
    sde_values : SDE density values for all solutions
    existing_assignments : niche assignments for already-selected solutions
    existing_niche_counts : count of already-selected solutions per niche

    Returns
    -------
    selected : list of indices (from front_indices) to include
    """
    if n_select >= len(front_indices):
        return list(front_indices)

    # Normalize objectives for association
    ideal = objectives.min(axis=0)
    nadir = objectives.max(axis=0)
    norm_obj = normalize_objectives(objectives, ideal, nadir)

    # Associate front solutions to ref dirs
    front_norm = norm_obj[front_indices]
    front_assignments = associate_to_directions(front_norm, ref_dirs)

    # Build niche counts (copy to avoid mutating)
    niche_counts = existing_niche_counts.copy()

    selected = []
    remaining = list(range(len(front_indices)))

    for _ in range(n_select):
        if not remaining:
            break

        # Find the niche with minimum count among remaining solutions
        min_count = np.inf
        candidate_niches = set()
        for r in remaining:
            niche = front_assignments[r]
            c = niche_counts[niche]
            if c < min_count:
                min_count = c
                candidate_niches = {niche}
            elif c == min_count:
                candidate_niches.add(niche)

        # Among candidates in rarest niches, pick by SDE (lowest = most isolated)
        best_r = -1
        best_sde = np.inf
        for r in remaining:
            niche = front_assignments[r]
            if niche in candidate_niches:
                idx = front_indices[r]
                if sde_values[idx] < best_sde:
                    best_sde = sde_values[idx]
                    best_r = r

        if best_r < 0:
            best_r = remaining[0]

        selected.append(front_indices[best_r])
        niche_counts[front_assignments[best_r]] += 1
        remaining.remove(best_r)

    return selected
