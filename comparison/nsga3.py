"""
NSGA-III — Reference-Point Based Non-dominated Sorting
=======================================================
Deb & Jain, "An Evolutionary Many-Objective Optimization Algorithm
Using Reference-Point Based Non-Dominated Sorting Approach",
IEEE TEC, 2014.

Implements the full NSGA-III for MO-VRPTW with:
  - Das-Dennis structured reference points
  - Adaptive normalization with ideal/nadir tracking
  - Niche-count based selection on the boundary front
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.solution import Solution, SolutionParser
from core.objectives import FitnessEvaluator, N_OBJ
from algorithm.nondominated import fast_nondominated_sort
from algorithm.reference_dirs import (
    das_dennis,
    normalize_objectives,
    associate_to_directions,
)
from algorithm.init_heuristics import greedy_nearest_neighbour

logger = logging.getLogger(__name__)


class NSGA3:
    """NSGA-III for many-objective VRPTW."""

    def __init__(
        self,
        instance: VRPTWInstance,
        n_sol: int = 100,
        t_run: float = 60.0,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        use_greedy_init: bool = True,
    ):
        self.inst = instance
        self.n_sol = n_sol
        self.t_run = t_run
        self.cx_rate = crossover_rate
        self.mut_rate = mutation_rate
        self.use_greedy_init = use_greedy_init
        self.evaluator = FitnessEvaluator(instance)
        self.parser = SolutionParser(instance)
        self.convergence: List[Tuple[float, float]] = []

        p = max(2, round(n_sol ** (1.0 / (N_OBJ - 1))))
        self.ref_dirs = das_dennis(N_OBJ, p)

    def _crossover(self, p1: Solution, p2: Solution) -> Solution:
        """SBX-like crossover on random keys."""
        nvar = p1.nvar
        mask = np.random.rand(nvar) < 0.5
        child_keys = np.where(mask, p1.keys, p2.keys)
        return Solution(keys=child_keys, n_customers=p1.n_customers,
                        n_vehicles=p1.n_vehicles)

    def _mutate(self, sol: Solution) -> Solution:
        keys = sol.keys.copy()
        mask = np.random.rand(len(keys)) < self.mut_rate
        keys[mask] = np.random.rand(mask.sum())
        return Solution(keys=keys, n_customers=sol.n_customers,
                        n_vehicles=sol.n_vehicles)

    def _tournament(self, pop: List[Solution]) -> Solution:
        i, j = np.random.randint(0, len(pop), 2)
        if pop[i].rank < pop[j].rank:
            return pop[i]
        elif pop[i].rank > pop[j].rank:
            return pop[j]
        return pop[i] if getattr(pop[i], 'niche_dist', 0) < getattr(pop[j], 'niche_dist', 0) else pop[j]

    def _nsga3_select(self, merged: List[Solution],
                      merged_obj: np.ndarray, n_select: int) -> List[int]:
        """
        NSGA-III selection with reference-point based niching.

        1. Non-dominated sort → fronts F_0, F_1, ...
        2. Add complete fronts until boundary front F_l
        3. From F_l, use niche-preservation to fill remaining slots:
           - Normalize objectives using ideal/nadir
           - Associate each solution to nearest reference point
           - Prioritise niches with lowest count
           - Break ties by perpendicular distance to reference direction
        """
        fronts = fast_nondominated_sort(merged_obj)

        selected: List[int] = []
        boundary_front_idx = -1

        for fi, front in enumerate(fronts):
            if len(selected) + len(front) <= n_select:
                selected.extend(front)
            else:
                boundary_front_idx = fi
                break
        else:
            return selected[:n_select]

        remaining = n_select - len(selected)
        boundary = fronts[boundary_front_idx]

        # Normalise
        ideal = merged_obj.min(axis=0)
        nadir = merged_obj.max(axis=0)
        norm_obj = normalize_objectives(merged_obj, ideal, nadir)

        # Associate all selected + boundary to reference directions
        all_indices = selected + boundary
        all_norm = norm_obj[np.array(all_indices)]
        assignments = associate_to_directions(all_norm, self.ref_dirs)

        # Perpendicular distances
        n_dirs = len(self.ref_dirs)
        perp_dists = np.zeros(len(all_indices))
        for k, idx in enumerate(all_indices):
            d = self.ref_dirs[assignments[k]]
            p = norm_obj[idx]
            proj = np.dot(p, d) / (np.dot(d, d) + 1e-15) * d
            perp_dists[k] = np.linalg.norm(p - proj)

        # Niche counts for already-selected solutions
        niche_counts = np.zeros(n_dirs, dtype=int)
        n_sel = len(selected)
        for k in range(n_sel):
            niche_counts[assignments[k]] += 1

        # Niching selection from boundary front
        boundary_info = []
        for k in range(n_sel, len(all_indices)):
            niche_id = assignments[k]
            dist = perp_dists[k]
            orig_idx = all_indices[k]
            boundary_info.append((niche_id, dist, orig_idx))

        chosen: List[int] = []
        remaining_boundary = list(boundary_info)

        while len(chosen) < remaining and remaining_boundary:
            # Find niche with minimum count
            active_niches = set(info[0] for info in remaining_boundary)
            min_count = min(niche_counts[n] for n in active_niches)
            min_niches = [n for n in active_niches
                          if niche_counts[n] == min_count]

            j_bar = min_niches[np.random.randint(len(min_niches))]

            candidates = [(d, idx, k) for k, (n, d, idx)
                          in enumerate(remaining_boundary) if n == j_bar]

            if niche_counts[j_bar] == 0:
                candidates.sort(key=lambda x: x[0])
                _, c_idx, c_k = candidates[0]
            else:
                _, c_idx, c_k = candidates[np.random.randint(len(candidates))]

            chosen.append(c_idx)
            niche_counts[j_bar] += 1
            remaining_boundary.pop(c_k)

        selected.extend(chosen)
        return selected[:n_select]

    def run(self) -> Tuple[List[Solution], Dict]:
        logger.info("NSGA-III starting on %s", self.inst.name)

        pop: List[Solution] = []
        if self.use_greedy_init:
            nn = greedy_nearest_neighbour(self.inst)
            x1 = Solution.from_routes(nn, self.inst)
            x1.decode(); self.parser.parse(x1)
            pop.append(x1)
            n_start = 1
        else:
            n_start = 0

        for _ in range(n_start, self.n_sol):
            s = Solution.random(self.inst)
            s.decode(); self.parser.parse(s)
            pop.append(s)

        self.evaluator.evaluate_batch(pop)
        start = time.time()
        gen = 0

        while time.time() - start < self.t_run:
            obj = np.array([s.objectives for s in pop])
            fronts = fast_nondominated_sort(obj)
            for rank, front in enumerate(fronts):
                for i in front:
                    pop[i].rank = rank

            elapsed = time.time() - start
            pf_idx = fronts[0] if fronts else []
            proxy = float(np.mean(obj[pf_idx, 0])) if pf_idx else float("inf")
            self.convergence.append((elapsed, proxy))

            offspring: List[Solution] = []
            for _ in range(self.n_sol):
                p1 = self._tournament(pop)
                p2 = self._tournament(pop)
                if np.random.random() < self.cx_rate:
                    child = self._crossover(p1, p2)
                else:
                    child = p1.clone()
                child = self._mutate(child)
                child.decode(); self.parser.parse(child)
                self.evaluator.evaluate(child)
                offspring.append(child)

            merged = pop + offspring
            merged_obj = np.array([s.objectives for s in merged])
            best_indices = self._nsga3_select(merged, merged_obj, self.n_sol)
            pop = [merged[i] for i in best_indices]
            gen += 1

        obj = np.array([s.objectives for s in pop])
        fronts = fast_nondominated_sort(obj)
        for rank, front in enumerate(fronts):
            for i in front:
                pop[i].rank = rank
        pareto = [s for s in pop if s.rank == 0]
        logger.info("NSGA-III done: %d gen, PF=%d", gen, len(pareto))
        return pareto, {"generations": gen, "runtime": time.time() - start,
                        "convergence": self.convergence}
