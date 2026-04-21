"""
iNSSSO — Preference-Based improved NSSSO
==========================================
Enhanced with:
  - R-Dominance ranking (preference-guided non-dominated sorting)
  - ASF-based gBest selection (Achievement Scalarizing Function)
  - External ε-dominance archive with preference tie-breaking
  - Adaptive operator rates (ABS/LS probabilities adjust dynamically)
  - Polynomial mutation for diversity
  - Preference-aware convergence tracking
Optimised for near-optimal solutions on Solomon VRPTW benchmarks.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.solution import Solution, SolutionParser
from core.objectives import FitnessEvaluator
from core.preference import UserPreference
from algorithm.nondominated import fast_nondominated_sort, is_dominated_by_set
from algorithm.crowding import (
    assign_rank_and_crowding,
    assign_rank_and_sde,
    crowding_distance,
    select_best,
    select_gbest,
)
from algorithm.r_dominance import (
    r_assign_rank_and_crowding,
    select_best_r,
    select_gbest_asf,
)
from algorithm.reference_dirs import (
    das_dennis,
    preference_biased_dirs,
)
from algorithm.abs_search import ABSearch
from algorithm.init_heuristics import (
    best_initialization,
    greedy_nearest_neighbour,
    insertion_heuristic,
    clarke_wright_savings,
    full_local_search,
    two_opt_route,
    or_opt_route,
    evaluate_route,
    total_distance,
    merge_routes,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
#  External Archive with ε-dominance + Preference
# ═══════════════════════════════════════════════════════════════════
class DualArchive:
    """
    Dual-archive system for balancing convergence and diversity.

    Architecture:
        A_conv (Convergence archive):
            - ε-dominance based
            - Pruned by ASF when preference is set
            - Maintains solutions close to ROI
        A_div (Diversity archive):
            - Pareto-dominance only (no ε-boxing)
            - Pruned by SDE density to spread across PF
            - Maintains well-distributed boundary solutions

    Mathematical formulation:
        1. ε-dominance (A_conv):
           box(f) = ⌊f_m / (ε + 10^{-15})⌋  ∀m
           x replaces y in same box iff ASF(x) < ASF(y)

        2. SDE pruning (A_div):
           When |A_div| > max_size:
             Remove argmin_i SDE(i)  (most crowded)

        3. Archive injection into population:
           With prob p_conv → inject from A_conv (intensification)
           With prob p_div  → inject from A_div  (diversification)
           where p_conv/p_div adapts based on stagnation count

    This dual mechanism prevents the well-known "convergence-diversity
    dilemma" in many-objective optimization (Ishibuchi et al., 2017).
    """

    def __init__(self, max_size: int = 200, epsilon: float = 0.01,
                 pref: Optional[UserPreference] = None):
        self.max_size = max_size
        self.epsilon = epsilon
        self.pref = pref

        # Convergence archive (preference-driven)
        self.conv_archive: List[Solution] = []
        # Diversity archive (spread-driven)
        self.div_archive: List[Solution] = []

        # Adaptive epsilon: scaled per-objective once we see data
        self._obj_ranges: Optional[np.ndarray] = None
        self._eps_vector: Optional[np.ndarray] = None

    def _update_eps_vector(self, obj: np.ndarray) -> None:
        """Update per-objective epsilon vector from observed ranges."""
        if self._obj_ranges is None:
            self._obj_ranges = np.zeros((2, len(obj)))
            self._obj_ranges[0] = obj  # min
            self._obj_ranges[1] = obj  # max
        else:
            self._obj_ranges[0] = np.minimum(self._obj_ranges[0], obj)
            self._obj_ranges[1] = np.maximum(self._obj_ranges[1], obj)
        ranges = self._obj_ranges[1] - self._obj_ranges[0]
        ranges = np.where(ranges < 1e-10, 1.0, ranges)
        self._eps_vector = self.epsilon * ranges

    def _eps_box(self, obj: np.ndarray) -> np.ndarray:
        self._update_eps_vector(obj)
        if self._eps_vector is not None:
            return np.floor(obj / (self._eps_vector + 1e-15))
        return np.floor(obj / (self.epsilon + 1e-15))

    @staticmethod
    def _is_duplicate(obj: np.ndarray, archive: List[Solution],
                      tol: float = 1e-6) -> bool:
        """Check if an objective vector already exists in the archive."""
        for member in archive:
            if np.allclose(obj, np.array(member.objectives), atol=tol, rtol=0):
                return True
        return False

    def update(self, candidates: List[Solution]) -> None:
        """Update both archives with new candidates."""
        for sol in candidates:
            if sol.objectives is None:
                continue
            self._try_add_conv(sol)
            self._try_add_div(sol)

        if len(self.conv_archive) > self.max_size:
            self._prune_conv()
        if len(self.div_archive) > self.max_size:
            self._prune_div()

    def _try_add_conv(self, sol: Solution) -> None:
        """ε-dominance based insertion for convergence archive."""
        obj = np.array(sol.objectives)
        eps_box = self._eps_box(obj)

        to_remove = []
        for i, member in enumerate(self.conv_archive):
            m_obj = np.array(member.objectives)
            m_box = self._eps_box(m_obj)

            if np.array_equal(eps_box, m_box):
                if self.pref is not None:
                    if self.pref.asf(obj) < self.pref.asf(m_obj):
                        to_remove.append(i)
                    else:
                        return
                else:
                    if sum(sol.objectives) < sum(member.objectives):
                        to_remove.append(i)
                    else:
                        return
            elif np.all(m_obj <= obj) and np.any(m_obj < obj):
                return
            elif np.all(obj <= m_obj) and np.any(obj < m_obj):
                to_remove.append(i)

        for i in sorted(to_remove, reverse=True):
            self.conv_archive.pop(i)
        self.conv_archive.append(sol.clone())

    def _try_add_div(self, sol: Solution) -> None:
        """Pareto-dominance insertion for diversity archive (no ε-boxing)."""
        obj = np.array(sol.objectives)

        if self._is_duplicate(obj, self.div_archive):
            return

        to_remove = []
        for i, member in enumerate(self.div_archive):
            m_obj = np.array(member.objectives)
            if np.all(m_obj <= obj) and np.any(m_obj < obj):
                return
            elif np.all(obj <= m_obj) and np.any(obj < m_obj):
                to_remove.append(i)

        for i in sorted(to_remove, reverse=True):
            self.div_archive.pop(i)
        self.div_archive.append(sol.clone())

    def _prune_conv(self) -> None:
        """Prune convergence archive by ASF (preference) or sum."""
        if len(self.conv_archive) <= self.max_size:
            return
        objs = np.array([s.objectives for s in self.conv_archive])
        if self.pref is not None:
            asf_vals = self.pref.asf_augmented_batch(objs)
            sorted_idx = np.argsort(asf_vals)[:self.max_size]
        else:
            sums = objs.sum(axis=1)
            sorted_idx = np.argsort(sums)[:self.max_size]
        self.conv_archive = [self.conv_archive[i] for i in sorted_idx]

    def _prune_div(self) -> None:
        """Prune diversity archive by removing most crowded (lowest SDE)."""
        if len(self.div_archive) <= self.max_size:
            return
        objs = np.array([s.objectives for s in self.div_archive])
        from algorithm.crowding import sde_density
        sde_vals = sde_density(objs)
        sorted_idx = np.argsort(-sde_vals)[:self.max_size]
        self.div_archive = [self.div_archive[i] for i in sorted_idx]

    def get_solutions(self, mode: str = "combined") -> List[Solution]:
        """
        Get solutions from archive.
        mode: "conv" | "div" | "combined"
        Combined returns non-dominated, deduplicated merge of both archives.
        """
        if mode == "conv":
            return list(self.conv_archive)
        elif mode == "div":
            return list(self.div_archive)
        else:
            all_sols = self.conv_archive + self.div_archive
            if not all_sols:
                return []
            objs = np.array([s.objectives for s in all_sols])
            fronts = fast_nondominated_sort(objs)
            if not fronts:
                return all_sols
            pf_sols = [all_sols[i] for i in fronts[0]]
            return self._deduplicate(pf_sols)

    @staticmethod
    def _deduplicate(solutions: List[Solution], tol: float = 1e-6) -> List[Solution]:
        """Remove solutions with near-identical objective vectors."""
        if not solutions:
            return solutions
        unique: List[Solution] = []
        seen_objs: List[np.ndarray] = []
        for sol in solutions:
            obj = np.array(sol.objectives)
            is_dup = False
            for s_obj in seen_objs:
                if np.allclose(obj, s_obj, atol=tol, rtol=0):
                    is_dup = True
                    break
            if not is_dup:
                unique.append(sol)
                seen_objs.append(obj)
        return unique

    def inject_solution(self, stagnation_count: int = 0) -> Optional[Solution]:
        """
        Inject an archive solution.
        Probability shifts from diversity to convergence as stagnation grows:
            p_conv = σ(stagnation/5)   (sigmoid)
        """
        if not self.conv_archive and not self.div_archive:
            return None

        p_conv = 1.0 / (1.0 + np.exp(-stagnation_count / 5.0 + 2.0))

        if np.random.random() < p_conv and self.conv_archive:
            idx = np.random.randint(len(self.conv_archive))
            return self.conv_archive[idx].clone()
        elif self.div_archive:
            idx = np.random.randint(len(self.div_archive))
            return self.div_archive[idx].clone()
        elif self.conv_archive:
            idx = np.random.randint(len(self.conv_archive))
            return self.conv_archive[idx].clone()
        return None

    def size(self) -> int:
        return len(self.conv_archive) + len(self.div_archive)


# Backward compatibility
ParetoArchive = DualArchive


class iNSSSO:
    """
    Preference-based improved NSSSO with R-Dominance ranking,
    ASF-based gBest selection, and preference-aware ABS.
    """

    def __init__(
        self,
        instance: VRPTWInstance,
        n_sol: int = 100,
        cw: float = 0.99,
        cg: float = 0.95,
        n_abs: float = 0.2,
        t_run: float = 60.0,
        archive_size: int = 200,
        epsilon: float = 0.001,
        ls_rate_rank0: float = 0.10,
        mutation_rate: float = 0.05,
        preference: Optional[UserPreference] = None,
    ):
        self.inst = instance
        self.n_sol = n_sol
        self.cw = cw
        self.cg = cg
        self.n_abs_base = n_abs
        self.n_abs = n_abs
        self.t_run = t_run
        self.ls_rate_rank0 = ls_rate_rank0
        self.mutation_rate = mutation_rate
        self.pref = preference

        self.evaluator = FitnessEvaluator(instance)
        self.parser = SolutionParser(instance)
        self.abs_search = ABSearch(instance, n_abs, preference=preference)

        self.archive = ParetoArchive(
            max_size=archive_size, epsilon=epsilon, pref=preference
        )
        self.population: List[Solution] = []
        self.convergence: List[Tuple[float, float]] = []

        # Generate reference directions for many-objective selection
        n_obj = 5  # Z1..Z5
        if preference is not None:
            self.ref_dirs = preference_biased_dirs(
                n_objectives=n_obj,
                g=preference.g,
                w=preference.w,
                n_total=105,
                pref_ratio=0.7,
            )
        else:
            self.ref_dirs = das_dennis(n_partitions=4, n_objectives=n_obj)

        logger.info("Generated %d reference directions (M=%d)",
                    len(self.ref_dirs), n_obj)

        # Adaptive tracking
        self._stagnation_count = 0
        self._last_best_asf = float("inf")

    def _auto_calibrate_preference(self) -> None:
        """
        Auto-calibrate reference point g from initial population.

        Strategy: g = ideal + margin * (p10 - ideal)
        - ideal = best value per objective among feasible solutions
        - p10 = 10th percentile (near-best, not outlier)
        - margin = 0.1 (slightly relaxed aspiration)
        This makes g instance-adaptive — works for C101, R101, etc.
        """
        if self.pref is None:
            return

        # Only use feasible solutions (no unserved customers)
        feasible = [s for s in self.population
                    if s.objectives is not None and s.restcus == 0]

        if len(feasible) < 3:
            # Fallback: use all solutions but cap at reasonable values
            feasible = [s for s in self.population
                        if s.objectives is not None]

        if len(feasible) == 0:
            return

        objs = np.array([s.objectives for s in feasible])

        ideal = objs.min(axis=0)
        p10 = np.percentile(objs, 10, axis=0)

        # g = ideal + small margin towards p10
        margin = 0.1
        new_g = ideal + margin * np.maximum(p10 - ideal, 0.0)

        # Ensure g is slightly above ideal (at least 1% of range)
        obj_range = objs.max(axis=0) - ideal
        min_shift = 0.01 * obj_range
        new_g = np.maximum(new_g, ideal + min_shift)

        self.pref.g = new_g

        # Update ABS search preference too
        self.abs_search.pref = self.pref
        self.archive.pref = self.pref

        g_str = ', '.join(f'{v:.4f}' for v in new_g)
        logger.info("Auto-calibrated g = [%s] (from %d feasible)",
                    g_str, len(feasible))

    # ----- initialisation ---------------------------------------------------
    def initialize_population(self) -> List[Solution]:
        """Multi-start initialisation with heavy local search."""
        pop: List[Solution] = []

        # Best init with local search
        init_time = min(self.t_run * 0.4, 15.0)
        best_routes = best_initialization(self.inst, time_limit=init_time)

        # Smart merge: only when capacity utilization is low (RC-type)
        total_demand = sum(self.inst.customers[c].demand
                          for r in best_routes for c in r)
        avg_util = total_demand / (len(best_routes) * self.inst.capacity)
        if avg_util < 0.6:  # spare capacity → try merging
            best_routes = merge_routes(best_routes, self.inst)
            logger.info("Route merge: %d routes (util=%.0f%%)",
                        len(best_routes), avg_util * 100)

        best_dist = total_distance(best_routes, self.inst)

        x1 = Solution.from_routes(best_routes, self.inst)
        x1.decode()
        self.parser.parse(x1)
        self.evaluator.evaluate(x1)
        pop.append(x1)
        logger.info("Best init: %d routes, dist=%.1f",
                    len(best_routes), best_dist)

        # Generate diverse seeds from different strategies
        seed_routes_list: List[List[List[int]]] = [best_routes]

        for sort_key in ["ready_time", "distance", "angle", "demand",
                         "due_date", "tw_center"]:
            try:
                r = insertion_heuristic(self.inst, sort_key=sort_key)
                r = [two_opt_route(rt, self.inst) for rt in r]
                seed_routes_list.append(r)
            except Exception:
                pass

        try:
            cw_routes = clarke_wright_savings(self.inst)
            cw_routes = [two_opt_route(r, self.inst) for r in cw_routes]
            seed_routes_list.append(cw_routes)
        except Exception:
            pass

        try:
            nn_routes = greedy_nearest_neighbour(self.inst)
            nn_routes = [two_opt_route(r, self.inst) for r in nn_routes]
            seed_routes_list.append(nn_routes)
        except Exception:
            pass

        # Create solutions from seeds + perturbations
        for seed in seed_routes_list:
            if len(pop) >= self.n_sol:
                break
            sol = Solution.from_routes(seed, self.inst)
            sol.decode()
            self.parser.parse(sol)
            self.evaluator.evaluate(sol)
            pop.append(sol)

            for noise_scale in [0.05, 0.10, 0.15]:
                if len(pop) >= self.n_sol:
                    break
                ps = self._perturb_solution(sol, noise_scale)
                ps.decode()
                self.parser.parse(ps)
                self.evaluator.evaluate(ps)
                pop.append(ps)

        # Fill remaining with random
        while len(pop) < self.n_sol:
            sol = Solution.random(self.inst)
            sol.decode()
            self.parser.parse(sol)
            self.evaluator.evaluate(sol)
            pop.append(sol)

        return pop

    def _perturb_solution(self, sol: Solution,
                          noise_scale: float = 0.08) -> Solution:
        """Create a perturbed copy of a solution's keys."""
        noise = np.random.uniform(-noise_scale, noise_scale, len(sol.keys))
        new_keys = np.clip(sol.keys + noise, 0.0, 0.999)
        return Solution(
            keys=new_keys,
            n_customers=sol.n_customers,
            n_vehicles=sol.n_vehicles,
        )

    # ----- SSO update (Enhanced Eq 2) — with Lévy flight & DE perturbation ---
    def update_solution(self, xi: Solution, gbest: Solution,
                        xr1: Optional[Solution] = None,
                        xr2: Optional[Solution] = None,
                        cg_override: Optional[float] = None) -> Solution:
        """
        Enhanced SSO update with three exploration mechanisms:

        x_{i,j}^{new} = { gbest_j            if ρ_j ≤ c_g        (exploitation)
                        { x_{i,j}             if c_g < ρ_j ≤ c_w  (conservation)
                        { x_{i,j} + L_j       if c_w < ρ_j ≤ c_l  (Lévy flight)
                        { x_{i,j} + F(r1-r2)  otherwise            (DE mutation)

        Lévy flight step:
            L_j ~ Lévy(β=1.5) × (gbest_j - x_{i,j})
            Lévy(β) drawn via Mantegna's algorithm

        DE/rand/1 perturbation:
            x_{i,j} + F × (x_{r1,j} - x_{r2,j}),  F = 0.5

        This replaces the original random exploration (1% probability)
        with structured exploration that maintains search direction.
        """
        nvar = xi.nvar
        rho = np.random.rand(nvar)

        cg = cg_override if cg_override is not None else self.cg
        new_keys = np.where(rho <= cg, gbest.keys, xi.keys)

        # Lévy flight exploration (replaces pure random for ρ > c_w)
        c_l = self.cw + (1.0 - self.cw) * 0.6  # 60% of exploration band
        levy_mask = (rho > self.cw) & (rho <= c_l)
        if np.any(levy_mask):
            levy_steps = self._levy_flight(nvar, beta=1.5)
            direction = gbest.keys - xi.keys
            levy_keys = xi.keys + levy_steps * direction * 0.01
            new_keys = np.where(levy_mask, levy_keys, new_keys)

        # Differential perturbation (remaining exploration band)
        de_mask = rho > c_l
        if np.any(de_mask) and xr1 is not None and xr2 is not None:
            F = 0.5
            de_keys = xi.keys + F * (xr1.keys - xr2.keys)
            new_keys = np.where(de_mask, de_keys, new_keys)
        else:
            random_keys = np.random.rand(nvar)
            new_keys = np.where(de_mask, random_keys, new_keys)

        new_keys = np.clip(new_keys, 0.0, 0.999)
        return Solution(
            keys=new_keys,
            n_customers=xi.n_customers,
            n_vehicles=xi.n_vehicles,
        )

    @staticmethod
    def _levy_flight(n: int, beta: float = 1.5) -> np.ndarray:
        """
        Generate Lévy flight steps using Mantegna's algorithm.

        σ_u = { Γ(1+β) sin(πβ/2) / [Γ((1+β)/2) β 2^{(β-1)/2}] }^{1/β}
        u ~ N(0, σ_u²),  v ~ N(0, 1)
        step = u / |v|^{1/β}
        """
        from math import gamma as _gamma
        sigma_u = (
            _gamma(1 + beta) * np.sin(np.pi * beta / 2)
            / (_gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
        ) ** (1.0 / beta)
        u = np.random.normal(0, sigma_u, n)
        v = np.random.normal(0, 1, n)
        return u / (np.abs(v) ** (1.0 / beta))

    # ----- polynomial mutation (vectorised) ----------------------------------
    def _polynomial_mutation(self, sol: Solution, eta_m: float = 20.0) -> Solution:
        """Vectorised polynomial mutation on random keys."""
        keys = sol.keys.copy()
        n = len(keys)
        mask = np.random.random(n) < self.mutation_rate
        if not np.any(mask):
            return Solution(keys=keys, n_customers=sol.n_customers,
                            n_vehicles=sol.n_vehicles)

        y = keys[mask]
        delta1 = y
        delta2 = 1.0 - y
        rnd = np.random.random(len(y))

        low = rnd < 0.5
        xy_low = 1.0 - delta1[low]
        val_low = 2.0 * rnd[low] + (1.0 - 2.0 * rnd[low]) * (xy_low ** (eta_m + 1.0))
        dq_low = val_low ** (1.0 / (eta_m + 1.0)) - 1.0

        high = ~low
        xy_high = 1.0 - delta2[high]
        val_high = (2.0 * (1.0 - rnd[high])
                    + 2.0 * (rnd[high] - 0.5) * (xy_high ** (eta_m + 1.0)))
        dq_high = 1.0 - val_high ** (1.0 / (eta_m + 1.0))

        deltaq = np.empty(len(y))
        deltaq[low] = dq_low
        deltaq[high] = dq_high

        keys[mask] = np.clip(y + deltaq, 0.0, 0.999)
        return Solution(keys=keys, n_customers=sol.n_customers,
                        n_vehicles=sol.n_vehicles)

    # ----- local search on decoded solution ---------------------------------
    def apply_local_search(self, solution: Solution) -> Solution:
        """Apply 2-opt + smart route merge to decoded routes."""
        if solution.routes is None or solution.restcus > 0:
            return solution
        routes = [two_opt_route(r, self.inst) for r in solution.routes]

        # Smart merge: only when spare capacity exists
        total_demand = sum(self.inst.customers[c].demand
                          for r in routes for c in r)
        if routes:
            avg_util = total_demand / (len(routes) * self.inst.capacity)
            if avg_util < 0.6:
                routes = merge_routes(routes, self.inst, max_attempts=2)

        result = Solution.from_routes(routes, self.inst)
        result.decode()
        self.parser.parse(result)
        return result

    # ----- diverse gbest per reference direction -----------------------------
    def _select_diverse_gbest(
        self, obj_matrix: np.ndarray, pf_indices: List[int],
    ) -> np.ndarray:
        """
        Assign a different gbest to each individual using reference directions.

        Each individual i is associated with ref_dir[i % D]. The gbest for
        that individual is the PF solution closest to that reference direction.
        This prevents all individuals from converging to the same gbest.
        """
        n = len(self.population)
        n_dirs = len(self.ref_dirs)
        gbest_map = np.zeros(n, dtype=int)

        if len(pf_indices) == 0:
            return gbest_map

        pf_obj = obj_matrix[pf_indices]
        ideal = obj_matrix.min(axis=0)
        nadir = obj_matrix.max(axis=0)
        ranges = nadir - ideal
        ranges = np.where(ranges < 1e-10, 1.0, ranges)
        pf_norm = (pf_obj - ideal) / ranges

        # For each reference direction, find the closest PF solution
        dir_to_pf = np.zeros(n_dirs, dtype=int)
        for j in range(n_dirs):
            d = self.ref_dirs[j]
            dd = np.dot(d, d)
            if dd < 1e-15:
                dir_to_pf[j] = pf_indices[0]
                continue
            proj_scalars = pf_norm @ d / dd
            projs = proj_scalars[:, np.newaxis] * d[np.newaxis, :]
            perp_dists = np.linalg.norm(pf_norm - projs, axis=1)
            dir_to_pf[j] = pf_indices[np.argmin(perp_dists)]

        for i in range(n):
            ref_idx = i % n_dirs
            gbest_map[i] = dir_to_pf[ref_idx]

        return gbest_map

    # ----- adaptive parameter control ----------------------------------------
    def _adapt_parameters(self, gen: int, progress: float) -> None:
        """Adapt ABS probability based on search progress and stagnation."""
        # Check stagnation using ASF (preference-aware)
        current_pf = [s for s in self.population if s.rank == 0]
        if current_pf:
            if self.pref is not None:
                best_asf = min(self.pref.asf(s.objectives) for s in current_pf)
            else:
                best_asf = min(s.objectives[0] for s in current_pf)

            if abs(best_asf - self._last_best_asf) < 1e-6:
                self._stagnation_count += 1
            else:
                self._stagnation_count = 0
                self._last_best_asf = best_asf

        # Increase ABS probability when stagnating
        if self._stagnation_count > 5:
            self.n_abs = min(0.5, self.n_abs_base + 0.05 * self._stagnation_count)
        else:
            self.n_abs = self.n_abs_base

        # Increase mutation rate in later stages
        self.mutation_rate = 0.05 + 0.10 * progress

    # ----- main loop --------------------------------------------------------
    def run(self) -> Tuple[List[Solution], Dict]:
        """Main loop: fast Pareto sort + ASF-based gBest (hybrid)."""
        pref_str = ""
        if self.pref is not None:
            pref_str = f", g={self.pref.g.tolist()}, w={self.pref.w.tolist()}"
        logger.info("iNSSSO starting on %s  (nSol=%d, tRun=%.0fs, nABS=%.2f%s)",
                     self.inst.name, self.n_sol, self.t_run, self.n_abs, pref_str)

        # 1. Initialise
        self.population = self.initialize_population()

        # Auto-calibrate reference point from initial population
        self._auto_calibrate_preference()

        self.archive.update(self.population)

        start = time.time()
        generation = 0

        while True:
            elapsed = time.time() - start
            if elapsed >= self.t_run:
                break
            progress = elapsed / self.t_run

            # ── Ranking: NDS + SDE (replaces CD for many-objective) ──
            obj_matrix = np.array([s.objectives for s in self.population])
            ranks, sde_vals = assign_rank_and_sde(obj_matrix)

            for i, sol in enumerate(self.population):
                sol.rank = ranks[i]
                sol.crowding_distance = sde_vals[i]

            pf_indices = [i for i, r in enumerate(ranks) if r == 0]
            pf_sde = sde_vals[pf_indices] if len(pf_indices) > 0 else np.array([])

            # Convergence tracking (ASF-based when preference set)
            if pf_indices:
                pf_obj = obj_matrix[pf_indices]
                if self.pref is not None:
                    asf_vals = self.pref.asf_batch(pf_obj)
                    conv_metric = float(np.min(asf_vals))
                else:
                    conv_metric = float(np.mean(pf_obj[:, 0]))
            else:
                conv_metric = float("inf")
            self.convergence.append((elapsed, conv_metric))

            # Adapt parameters
            self._adapt_parameters(generation, progress)
            self.abs_search.n_abs = self.n_abs

            # ── Pre-compute diverse gbest per individual ──
            diverse_gb = self._select_diverse_gbest(obj_matrix, pf_indices)

            # Adaptive cg: lower early on for exploration, higher later
            cg_effective = self.cg * (0.7 + 0.3 * progress)

            # ── Generate offspring ──
            offspring: List[Solution] = []
            for i in range(self.n_sol):
                if np.random.random() < self.n_abs:
                    yi = self.abs_search.apply(self.population[i])
                else:
                    # 70% diverse gbest, 30% ASF-best (intensification)
                    if np.random.random() < 0.7:
                        gb_idx = diverse_gb[i]
                    elif self.pref is not None:
                        gb_idx = select_gbest_asf(
                            obj_matrix, self.pref, pf_indices
                        )
                    else:
                        gb_idx = select_gbest(pf_indices, sde_vals)

                    gbest = self.population[gb_idx]

                    # DE donors: two random distinct individuals
                    r_indices = np.random.choice(
                        self.n_sol, size=2, replace=False
                    )
                    xr1 = self.population[r_indices[0]]
                    xr2 = self.population[r_indices[1]]

                    yi = self.update_solution(
                        self.population[i], gbest, xr1=xr1, xr2=xr2,
                        cg_override=cg_effective,
                    )

                    if self._stagnation_count > 3 and np.random.random() < self.mutation_rate:
                        yi = self._polynomial_mutation(yi)

                yi.decode()
                self.parser.parse(yi)
                self.evaluator.evaluate(yi)

                # Adaptive local search on good offspring
                rank_i = ranks[i] if i < len(ranks) else 1
                ls_prob = self.ls_rate_rank0 if rank_i == 0 else 0.03
                if yi.restcus == 0 and np.random.random() < ls_prob:
                    yi = self.apply_local_search(yi)
                    self.evaluator.evaluate(yi)

                offspring.append(yi)

            # Update dual archive
            self.archive.update(offspring)

            # Inject from dual archive (adaptive convergence/diversity balance)
            injected = self.archive.inject_solution(self._stagnation_count)
            if injected is not None:
                if injected.objectives is None:
                    injected.decode()
                    self.parser.parse(injected)
                    self.evaluator.evaluate(injected)
                offspring.append(injected)

            # ── Selection: NDS + SDE + Ref Dir niching ──
            merged = self.population + offspring
            merged_obj = np.array([s.objectives for s in merged])
            best_indices = select_best(merged_obj, self.n_sol, self.ref_dirs)

            self.population = [merged[i] for i in best_indices]
            generation += 1

        # ── Final ranking ──
        obj_matrix = np.array([s.objectives for s in self.population])
        ranks, cds = assign_rank_and_crowding(obj_matrix)

        for i, sol in enumerate(self.population):
            sol.rank = ranks[i]
            sol.crowding_distance = cds[i]

        self.archive.update(self.population)

        # Return archive as the Pareto front
        pareto = self.archive.get_solutions()
        if not pareto:
            pareto = [s for s in self.population if s.rank == 0]

        elapsed = time.time() - start
        logger.info("iNSSSO finished: %d gen, %.1fs, PF=%d (archive=%d)",
                     generation, elapsed, len(pareto), self.archive.size())

        return pareto, {
            "generations": generation,
            "runtime": elapsed,
            "convergence": self.convergence,
            "evaluations": self.evaluator.eval_count,
        }
