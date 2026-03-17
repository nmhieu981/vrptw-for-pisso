"""
Objective Functions  (Z1 .. Z5) — 5-Objective MO-VRPTW
=======================================================

Z1 — number of vehicles used        (minimize)
Z2 — total travel distance           (minimize)
Z3 — total waiting time              (minimize)
Z4 — load balance (max-min demand)   (minimize)
Z5 — makespan (max completion time)  (minimize)

Includes adaptive objective normalization and conflict analysis
for many-objective optimization (Sec. 4 of the paper).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.solution import Solution, SolutionParser

PENALTY = 1e4  # penalty per unserved customer
N_OBJ = 5      # number of objectives


class ObjectiveNormalizer:
    """
    Adaptive objective normalization using running ideal/nadir estimates.

    At generation t, updates:
        ideal_i(t) = min(ideal_i(t-1), min_{x in pop} f_i(x))
        nadir_i(t) = (1-α) * nadir_i(t-1) + α * max_{x in pop} f_i(x)

    Normalized:
        f̂_i(x) = (f_i(x) - ideal_i) / (nadir_i - ideal_i + ε)

    The exponential moving average on nadir prevents outlier-driven
    fluctuations and stabilizes preference-based search (ASF, ROI).
    """

    def __init__(self, n_obj: int = N_OBJ, alpha: float = 0.1):
        self.n_obj = n_obj
        self.alpha = alpha
        self.ideal = np.full(n_obj, np.inf)
        self.nadir = np.full(n_obj, -np.inf)
        self._initialized = False

    def update(self, objectives: np.ndarray) -> None:
        """Update ideal/nadir from a population objective matrix (N, M)."""
        pop_min = objectives.min(axis=0)
        pop_max = objectives.max(axis=0)

        self.ideal = np.minimum(self.ideal, pop_min)

        if not self._initialized:
            self.nadir = pop_max.copy()
            self._initialized = True
        else:
            self.nadir = (1.0 - self.alpha) * self.nadir + self.alpha * pop_max

    def normalize(self, objectives: np.ndarray) -> np.ndarray:
        """Normalize objectives to [0, ~1] using adaptive ideal/nadir."""
        ranges = self.nadir - self.ideal
        ranges = np.where(ranges < 1e-10, 1.0, ranges)
        return (objectives - self.ideal) / ranges

    def get_ranges(self) -> np.ndarray:
        """Return nadir - ideal per objective."""
        ranges = self.nadir - self.ideal
        return np.where(ranges < 1e-10, 1.0, ranges)


class ObjectiveConflictAnalyzer:
    """
    Analyze pairwise conflict between objectives using the conflict
    metric from Purshouse & Fleming (2003):

        C(i,j) = 1 - r_s(f_i, f_j)

    where r_s is Spearman rank correlation.  C ∈ [0, 2]:
        C ≈ 0 → harmonious (optimizing one helps the other)
        C ≈ 1 → independent
        C ≈ 2 → maximally conflicting

    Used to:
    1. Justify the many-objective formulation (show most pairs conflict)
    2. Adaptively weight objectives in ASF when low-conflict pairs detected
    """

    @staticmethod
    def spearman_correlation(objectives: np.ndarray) -> np.ndarray:
        """Spearman rank correlation matrix (M, M)."""
        from scipy.stats import spearmanr
        n = objectives.shape[0]
        if n < 3:
            m = objectives.shape[1]
            return np.eye(m)
        corr, _ = spearmanr(objectives)
        if corr.ndim == 0:
            return np.array([[1.0]])
        return corr

    @staticmethod
    def conflict_matrix(objectives: np.ndarray) -> np.ndarray:
        """Conflict matrix C[i,j] = 1 - r_s(f_i, f_j) ∈ [0, 2]."""
        r_s = ObjectiveConflictAnalyzer.spearman_correlation(objectives)
        return 1.0 - r_s

    @staticmethod
    def conflict_summary(objectives: np.ndarray) -> Dict[str, float]:
        """Summary statistics of objective conflict."""
        C = ObjectiveConflictAnalyzer.conflict_matrix(objectives)
        m = C.shape[0]
        upper = C[np.triu_indices(m, k=1)]
        return {
            "mean_conflict": float(np.mean(upper)),
            "max_conflict": float(np.max(upper)),
            "min_conflict": float(np.min(upper)),
            "n_high_conflict": int(np.sum(upper > 1.0)),
            "n_pairs": len(upper),
        }


class FitnessEvaluator:
    """Evaluate the five objectives for a given solution."""

    def __init__(self, instance: VRPTWInstance):
        self.inst = instance
        self.parser = SolutionParser(instance)
        self.normalizer = ObjectiveNormalizer(N_OBJ)
        self.eval_count = 0

    def evaluate(self, solution: Solution) -> Tuple[float, ...]:
        """Return (Z1, Z2, Z3, Z4, Z5) and cache on the solution object."""
        if solution.routes is None:
            solution.decode()
        self.parser.parse(solution)

        penalty = solution.restcus * PENALTY
        routes = solution.routes or []

        z1 = float(len(routes)) + penalty

        total_dist = 0.0
        total_wait = 0.0
        completion_times: List[float] = []
        route_loads: List[float] = []

        for route in routes:
            dist, waits, comp = self.parser.route_details(route)
            total_dist += dist
            total_wait += sum(waits)
            completion_times.append(comp)
            load = sum(self.inst.customers[cid].demand for cid in route)
            route_loads.append(load)

        z2 = total_dist + penalty
        z3 = total_wait + penalty

        if route_loads:
            z4 = float(max(route_loads) - min(route_loads)) + penalty
        else:
            z4 = penalty

        if completion_times:
            z5 = float(max(completion_times)) + penalty
        else:
            z5 = penalty

        solution.objectives = (z1, z2, z3, z4, z5)
        self.eval_count += 1
        return solution.objectives

    def evaluate_batch(self, solutions: List[Solution]) -> List[Tuple[float, ...]]:
        return [self.evaluate(s) for s in solutions]
