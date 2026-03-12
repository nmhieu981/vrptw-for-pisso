"""
Objective Functions  (Z1 .. Z5) — 5-Objective MO-VRPTW
=======================================================

Z1 — number of vehicles used        (minimize)
Z2 — total travel distance           (minimize)
Z3 — total waiting time              (minimize)
Z4 — load balance (max-min demand)   (minimize)
Z5 — makespan (max completion time)  (minimize)
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.solution import Solution, SolutionParser

PENALTY = 1e4  # penalty per unserved customer
N_OBJ = 5      # number of objectives


class FitnessEvaluator:
    """Evaluate the five objectives for a given solution."""

    def __init__(self, instance: VRPTWInstance):
        self.inst = instance
        self.parser = SolutionParser(instance)

    # ----- single evaluation ------------------------------------------------
    def evaluate(self, solution: Solution) -> Tuple[float, ...]:
        """Return (Z1, Z2, Z3, Z4, Z5) and cache on the solution object."""
        # Make sure routes are decoded & parsed
        if solution.routes is None:
            solution.decode()
        self.parser.parse(solution)

        penalty = solution.restcus * PENALTY
        routes = solution.routes or []

        # ── Z1: number of vehicles ──
        z1 = float(len(routes)) + penalty

        # Per-route computation
        total_dist = 0.0
        total_wait = 0.0
        completion_times: List[float] = []
        route_loads: List[float] = []

        for route in routes:
            dist, waits, comp = self.parser.route_details(route)
            total_dist += dist
            total_wait += sum(waits)
            completion_times.append(comp)

            # Load = sum of customer demands in this route
            load = sum(self.inst.customers[cid].demand for cid in route)
            route_loads.append(load)

        # ── Z2: total distance ──
        z2 = total_dist + penalty

        # ── Z3: total waiting time (sum, not average) ──
        z3 = total_wait + penalty

        # ── Z4: load balance = L_max - L_min ──
        if route_loads:
            z4 = float(max(route_loads) - min(route_loads)) + penalty
        else:
            z4 = penalty

        # ── Z5: makespan = max completion time ──
        if completion_times:
            z5 = float(max(completion_times)) + penalty
        else:
            z5 = penalty

        solution.objectives = (z1, z2, z3, z4, z5)
        return solution.objectives

    # ----- batch evaluation -------------------------------------------------
    def evaluate_batch(self, solutions: List[Solution]) -> List[Tuple[float, ...]]:
        return [self.evaluate(s) for s in solutions]
