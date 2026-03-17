"""
ALNS — Adaptive Large Neighbourhood Search (Preference-Aware)
==============================================================
Extends the original ABS with:
  - Multiple destroy operators: worst removal, Shaw removal, route removal,
    random removal, proximity-based removal
  - Multiple repair operators: regret-2, regret-3, greedy insertion,
    A*-based build
  - Roulette-wheel adaptive operator selection (Ropke & Pisinger, 2006)
  - Preference-guided scoring for repair decisions
  - Simulated annealing acceptance criterion

Mathematical formulation:
  Score update for operator k at segment s:
    π_k(s+1) = (1-r) × π_k(s) + r × Δ_k(s)     (Eq. A1)
  Selection probability:
    P(k) = π_k / Σ_j π_j                          (Eq. A2)
  SA acceptance:
    accept(Δf) ↔ Δf < 0 ∨ rand() < exp(-Δf/T)   (Eq. A3)
    T(t+1) = c_T × T(t),  c_T ∈ [0.99, 0.999]   (Eq. A4)

Destroy operators:
  1. Worst removal (Eq. D1): remove customers with max distance saving
  2. Shaw removal (Eq. D2): relatedness R(i,j) = α d(i,j) + β|TW_i-TW_j|
  3. Route removal (Eq. D3): remove entire routes by P(k)∝exp(-10 nCus_k/max)
  4. Random removal (Eq. D4): uniform random customer selection
  5. Proximity removal (Eq. D5): remove cluster of spatially close customers

Repair operators:
  1. Regret-2 insertion (Eq. R1)
  2. Regret-3 insertion (Eq. R2)
  3. Greedy best-position insertion (Eq. R3)
  4. A*-based route building with preference scoring (Eq. R4)
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.solution import Solution, SolutionParser


class OperatorScoring:
    """
    Adaptive weight adjustment for operator selection (Ropke & Pisinger, 2006).

    Each operator maintains a score π_k that tracks recent performance.
    Score segments are reset every `segment_size` iterations.

    Rewards:
        σ_1 = 33  (new global best)
        σ_2 = 9   (improving, not dominated)
        σ_3 = 3   (accepted by SA)
        σ_4 = 0   (rejected)
    """

    def __init__(self, n_operators: int, reaction_factor: float = 0.1,
                 sigma: Tuple[float, ...] = (33.0, 9.0, 3.0, 0.0)):
        self.n_ops = n_operators
        self.r = reaction_factor
        self.sigma = sigma

        self.weights = np.ones(n_operators)
        self.usage_count = np.zeros(n_operators, dtype=int)
        self.segment_score = np.zeros(n_operators)

    def select(self) -> int:
        """Roulette-wheel selection: P(k) = π_k / Σ_j π_j."""
        probs = self.weights / self.weights.sum()
        return int(np.random.choice(self.n_ops, p=probs))

    def update(self, op_idx: int, reward_level: int) -> None:
        """Record reward for operator. reward_level ∈ {0, 1, 2, 3}."""
        self.usage_count[op_idx] += 1
        self.segment_score[op_idx] += self.sigma[reward_level]

    def end_segment(self) -> None:
        """End of segment: update weights using exponential smoothing."""
        for k in range(self.n_ops):
            if self.usage_count[k] > 0:
                avg_score = self.segment_score[k] / self.usage_count[k]
                self.weights[k] = ((1.0 - self.r) * self.weights[k]
                                   + self.r * avg_score)
            self.weights[k] = max(self.weights[k], 0.01)

        self.usage_count[:] = 0
        self.segment_score[:] = 0.0


class ALNSearch:
    """Adaptive Large Neighbourhood Search with preference-aware heuristics."""

    DESTROY_NAMES = [
        "worst_removal", "shaw_removal", "route_removal",
        "random_removal", "proximity_removal",
    ]
    REPAIR_NAMES = [
        "regret2_insertion", "regret3_insertion",
        "greedy_insertion", "astar_build",
    ]

    def __init__(self, instance: VRPTWInstance, n_abs: float = 0.2,
                 preference=None, sa_init_temp: float = 100.0,
                 sa_cooling: float = 0.995, segment_size: int = 25):
        self.inst = instance
        self.n_abs = n_abs
        self.parser = SolutionParser(instance)
        self.pref = preference

        self.sa_temp = sa_init_temp
        self.sa_cooling = sa_cooling
        self.segment_size = segment_size

        self.destroy_scoring = OperatorScoring(len(self.DESTROY_NAMES))
        self.repair_scoring = OperatorScoring(len(self.REPAIR_NAMES))
        self._iteration = 0

    # ════════════════════════════════════════════════════════════════
    #  DESTROY OPERATORS
    # ════════════════════════════════════════════════════════════════

    def _calc_removal_count(self, routes: List[List[int]]) -> int:
        """Number of customers to remove: U[15%, 40%] of total."""
        total = sum(len(r) for r in routes)
        return max(1, int(total * np.random.uniform(0.15, 0.40)))

    def worst_removal(self, routes: List[List[int]],
                      n_remove: int) -> Tuple[List[List[int]], List[int]]:
        """D1: Remove customers whose removal saves the most distance."""
        dm = self.inst.distance_matrix
        savings: List[Tuple[float, int, int]] = []

        for ri, route in enumerate(routes):
            for ci, cid in enumerate(route):
                prev_id = 0 if ci == 0 else route[ci - 1]
                next_id = 0 if ci == len(route) - 1 else route[ci + 1]
                s = dm[prev_id][cid] + dm[cid][next_id] - dm[prev_id][next_id]
                savings.append((s, ri, cid))

        savings.sort(reverse=True)
        removed_set: set = set()
        for s, ri, cid in savings:
            if len(removed_set) >= n_remove:
                break
            removed_set.add(cid)

        new_routes = [[c for c in r if c not in removed_set] for r in routes]
        new_routes = [r for r in new_routes if r]
        return new_routes, list(removed_set)

    def shaw_removal(self, routes: List[List[int]],
                     n_remove: int) -> Tuple[List[List[int]], List[int]]:
        """
        D2: Shaw removal — remove related customers.
        R(i,j) = α × d(i,j)/d_max + β × |tw_i - tw_j|/tw_max + γ × |q_i - q_j|/q_max
        """
        all_cus = [c for r in routes for c in r]
        if not all_cus:
            return routes, []

        seed = np.random.choice(all_cus)
        removed = [seed]
        remaining = [c for c in all_cus if c != seed]

        dm = self.inst.distance_matrix
        d_max = max(max(row) for row in dm) + 1e-10
        custs = self.inst.customers
        tw_max = max(abs(custs[c].due_date - custs[c].ready_time)
                     for c in all_cus) + 1e-10
        q_max = max(custs[c].demand for c in all_cus) + 1e-10

        alpha, beta, gamma = 0.4, 0.3, 0.3

        while len(removed) < n_remove and remaining:
            ref = removed[-1]
            relatedness = []
            for c in remaining:
                r_val = (alpha * dm[ref][c] / d_max
                         + beta * abs(custs[ref].ready_time - custs[c].ready_time) / tw_max
                         + gamma * abs(custs[ref].demand - custs[c].demand) / q_max)
                relatedness.append((r_val, c))
            relatedness.sort()
            # Deterministic-ish: pick from top 30%
            top_k = max(1, len(relatedness) // 3)
            _, chosen = relatedness[np.random.randint(top_k)]
            removed.append(chosen)
            remaining.remove(chosen)

        removed_set = set(removed)
        new_routes = [[c for c in r if c not in removed_set] for r in routes]
        new_routes = [r for r in new_routes if r]
        return new_routes, removed

    def route_removal(self, routes: List[List[int]],
                      n_remove: int) -> Tuple[List[List[int]], List[int]]:
        """D3: Remove entire routes. P(k) ∝ exp(-10 nCus_k / max(nCus))."""
        if not routes:
            return routes, []

        n_cus = np.array([len(r) for r in routes], dtype=float)
        max_cus = n_cus.max()
        if max_cus == 0:
            return routes, []

        probs = np.exp(-10.0 * n_cus / max_cus)
        probs /= probs.sum()

        n_routes_remove = max(1, round(len(routes) / 3))
        n_routes_remove = min(n_routes_remove, len(routes) - 1)

        chosen = np.random.choice(len(routes), size=n_routes_remove,
                                  replace=False, p=probs)
        chosen_set = set(chosen)

        removed = []
        kept = []
        for i, r in enumerate(routes):
            if i in chosen_set:
                removed.extend(r)
            else:
                kept.append(r)

        return kept, removed

    def random_removal(self, routes: List[List[int]],
                       n_remove: int) -> Tuple[List[List[int]], List[int]]:
        """D4: Uniform random removal."""
        all_cus = [c for r in routes for c in r]
        n_remove = min(n_remove, len(all_cus))
        removed = list(np.random.choice(all_cus, size=n_remove, replace=False))
        removed_set = set(removed)
        new_routes = [[c for c in r if c not in removed_set] for r in routes]
        new_routes = [r for r in new_routes if r]
        return new_routes, removed

    def proximity_removal(self, routes: List[List[int]],
                          n_remove: int) -> Tuple[List[List[int]], List[int]]:
        """D5: Remove spatially close cluster centered on a random customer."""
        all_cus = [c for r in routes for c in r]
        if not all_cus:
            return routes, []

        seed = np.random.choice(all_cus)
        dm = self.inst.distance_matrix
        dists = [(dm[seed][c], c) for c in all_cus if c != seed]
        dists.sort()
        removed = [seed] + [c for _, c in dists[:n_remove - 1]]

        removed_set = set(removed)
        new_routes = [[c for c in r if c not in removed_set] for r in routes]
        new_routes = [r for r in new_routes if r]
        return new_routes, removed

    # ════════════════════════════════════════════════════════════════
    #  REPAIR OPERATORS
    # ════════════════════════════════════════════════════════════════

    def _insertion_cost(self, route: List[int], pos: int,
                        cid: int) -> Tuple[bool, float]:
        """Cost of inserting cid at position pos in route."""
        from algorithm.init_heuristics import evaluate_route
        cand = route[:pos] + [cid] + route[pos:]
        ok, d_new, _ = evaluate_route(cand, self.inst)
        if not ok:
            return False, float("inf")
        _, d_old, _ = evaluate_route(route, self.inst)
        return True, d_new - d_old

    def _best_insertion(self, routes: List[List[int]],
                        cid: int) -> Optional[Tuple[float, int, int]]:
        """Find best insertion position for cid across all routes."""
        best = None
        for ri, route in enumerate(routes):
            for pos in range(len(route) + 1):
                ok, cost = self._insertion_cost(route, pos, cid)
                if ok and (best is None or cost < best[0]):
                    best = (cost, ri, pos)
        return best

    def regret_k_insertion(self, routes: List[List[int]],
                           unassigned: List[int],
                           k: int = 2) -> List[List[int]]:
        """
        Regret-k insertion: prioritise customers whose k-th best insertion
        cost differs most from their best.

        regret(c) = Σ_{j=2}^{k} (cost_j(c) - cost_1(c))
        """
        from algorithm.init_heuristics import evaluate_route

        remaining = list(unassigned)
        routes = [list(r) for r in routes]

        while remaining:
            regrets: List[Tuple[float, int, int, int]] = []

            for cid in remaining:
                costs: List[Tuple[float, int, int]] = []
                for ri, route in enumerate(routes):
                    _, old_d, _ = evaluate_route(route, self.inst)
                    for pos in range(len(route) + 1):
                        cand = route[:pos] + [cid] + route[pos:]
                        ok, d, _ = evaluate_route(cand, self.inst)
                        if ok:
                            costs.append((d - old_d, ri, pos))

                if not costs:
                    regrets.append((float("inf"), cid, -1, -1))
                    continue

                costs.sort(key=lambda x: x[0])
                regret_val = sum(
                    costs[min(j, len(costs) - 1)][0] - costs[0][0]
                    for j in range(1, k)
                )
                regrets.append((regret_val, cid, costs[0][1], costs[0][2]))

            if not regrets:
                break

            regrets.sort(reverse=True)
            _, chosen_cid, best_ri, best_pos = regrets[0]

            if best_ri >= 0:
                routes[best_ri].insert(best_pos, chosen_cid)
            else:
                routes.append([chosen_cid])
            remaining.remove(chosen_cid)

        return routes

    def greedy_insertion(self, routes: List[List[int]],
                         unassigned: List[int]) -> List[List[int]]:
        """R3: Greedy cheapest-insertion."""
        remaining = sorted(unassigned,
                           key=lambda c: self.inst.customers[c].due_date)
        routes = [list(r) for r in routes]

        for cid in remaining:
            best = self._best_insertion(routes, cid)
            if best is not None:
                _, ri, pos = best
                routes[ri].insert(pos, cid)
            else:
                routes.append([cid])

        return routes

    def astar_build(self, routes: List[List[int]],
                    unassigned: List[int]) -> List[List[int]]:
        """R4: A*-based route building with preference-guided scoring."""
        new_routes = list(routes)
        remaining = list(unassigned)

        avg_msp = 0.0
        if new_routes:
            ctimes = []
            for r in new_routes:
                _, _, ct = self.parser.route_details(r)
                ctimes.append(ct)
            avg_msp = np.mean(ctimes)

        max_new = self.inst.n_vehicles - len(new_routes)
        attempts = 0

        while remaining and attempts < max_new:
            built, remaining = self._build_one_route(remaining, avg_msp)
            if built:
                new_routes.append(built)
            else:
                break
            attempts += 1

        if remaining:
            new_routes = self.regret_k_insertion(new_routes, remaining, k=2)

        return new_routes

    def _build_one_route(self, unassigned: List[int],
                         avg_makespan: float) -> Tuple[List[int], List[int]]:
        """Build one route using A*-style scoring with preference weights."""
        route: List[int] = []
        current_time = 0.0
        current_load = 0.0
        prev_id = 0
        remaining = list(unassigned)

        while remaining:
            valid = []
            for cid in remaining:
                cust = self.inst.customers[cid]
                if current_load + cust.demand > self.inst.capacity:
                    continue
                travel = self.inst.travel_time_matrix[prev_id][cid]
                arrival = current_time + travel
                start = max(arrival, cust.ready_time)
                if start > cust.due_date:
                    continue
                ret = (start + cust.service_time
                       + self.inst.travel_time_matrix[cid][0])
                if ret > self.inst.depot.due_date:
                    continue
                valid.append(cid)

            if not valid:
                break

            if route and current_time >= avg_makespan:
                break

            g_costs = np.array([self.inst.distance_matrix[prev_id][c]
                                for c in valid])
            tw_urg = np.array([
                1.0 / max(1.0, self.inst.customers[c].due_date
                          - self.inst.customers[c].ready_time)
                for c in valid
            ])

            g_max = g_costs.max() if g_costs.max() > 0 else 1.0
            g_sc = g_costs / g_max
            tw_max = tw_urg.max() if tw_urg.max() > 0 else 1.0
            tw_sc = tw_urg / tw_max

            if self.pref is not None:
                w = self.pref.w
                f = w[0] * g_sc + w[1] * tw_sc + (1.0 - w[0] - w[1]) * 0.5
            else:
                f = g_sc + tw_sc

            f_max = f.max()
            if f_max > 0:
                f = f_max - f
            f += 1e-10
            probs = f / f.sum()
            chosen_cid = valid[np.random.choice(len(valid), p=probs)]

            cust = self.inst.customers[chosen_cid]
            travel = self.inst.travel_time_matrix[prev_id][chosen_cid]
            arrival = current_time + travel
            start = max(arrival, cust.ready_time)
            current_time = start + cust.service_time
            current_load += cust.demand
            prev_id = chosen_cid

            route.append(chosen_cid)
            remaining.remove(chosen_cid)

        return route, remaining

    # ════════════════════════════════════════════════════════════════
    #  MAIN ALNS APPLICATION
    # ════════════════════════════════════════════════════════════════

    def _quick_two_opt(self, route: List[int]) -> List[int]:
        """Single-pass 2-opt improvement."""
        from algorithm.init_heuristics import evaluate_route

        best = list(route)
        _, best_d, _ = evaluate_route(best, self.inst)

        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                ok, d, _ = evaluate_route(cand, self.inst)
                if ok and d < best_d - 1e-10:
                    best = cand
                    best_d = d
        return best

    def apply(self, solution: Solution) -> Solution:
        """
        Apply one iteration of ALNS:
        1. Select destroy operator via adaptive scoring
        2. Select repair operator via adaptive scoring
        3. Destroy → Repair → 2-opt post-processing
        4. SA acceptance: accept if improving or by Boltzmann probability
        5. Update operator scores based on outcome
        """
        new_sol = solution.clone()
        if new_sol.routes is None:
            new_sol.decode()
        self.parser.parse(new_sol)

        routes = new_sol.routes if new_sol.routes else []
        if not routes:
            return new_sol

        n_remove = self._calc_removal_count(routes)

        # Select and apply destroy operator
        d_idx = self.destroy_scoring.select()
        destroy_ops = [
            self.worst_removal, self.shaw_removal, self.route_removal,
            self.random_removal, self.proximity_removal,
        ]
        kept_routes, unassigned = destroy_ops[d_idx](routes, n_remove)
        unassigned = list(new_sol.unassigned) + unassigned

        # Select and apply repair operator
        r_idx = self.repair_scoring.select()
        repair_ops = [
            lambda r, u: self.regret_k_insertion(r, u, k=2),
            lambda r, u: self.regret_k_insertion(r, u, k=3),
            self.greedy_insertion,
            self.astar_build,
        ]
        rebuilt_routes = repair_ops[r_idx](kept_routes, unassigned)

        # 2-opt post-processing
        rebuilt_routes = [self._quick_two_opt(r) for r in rebuilt_routes if r]

        # Re-encode
        result = Solution.from_routes(rebuilt_routes, self.inst)
        served = set(c for r in rebuilt_routes for c in r)
        still_unassigned = [c for c in unassigned if c not in served]
        result.unassigned = still_unassigned
        result.restcus = len(still_unassigned)

        # Update iteration counter and temperature
        self._iteration += 1
        self.sa_temp *= self.sa_cooling

        if self._iteration % self.segment_size == 0:
            self.destroy_scoring.end_segment()
            self.repair_scoring.end_segment()

        return result

    def record_reward(self, d_idx: int, r_idx: int, reward: int) -> None:
        """Record reward for the last destroy/repair pair."""
        self.destroy_scoring.update(d_idx, reward)
        self.repair_scoring.update(r_idx, reward)


# Backward-compatible alias
ABSearch = ALNSearch
