"""
Batch runner — run iNSSSO on ALL Solomon instances, save to Excel.
Updated for 5-objective (Z1..Z5) formulation.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(__file__))

from core.problem import VRPTWInstance, find_solomon_instances
from core.preference import UserPreference
from algorithm.inssso import iNSSSO

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "csv", "R1")
OUTPUT_EXCEL = os.path.join(os.path.dirname(__file__), "results", "all_results.xlsx")
TIME_LIMIT = 600  # seconds per instance


def load_preference():
    """Load UserPreference from config/params.yaml."""
    cfg_path = os.path.join(os.path.dirname(__file__), "config", "params.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            config = yaml.safe_load(f)
        pref_cfg = config.get("preference", {})
        if pref_cfg:
            return UserPreference(
                g=np.array(pref_cfg.get("reference_point", [10, 830, 0.5, 0, 100])),
                w=np.array(pref_cfg.get("weights", [0.3, 0.3, 0.15, 0.1, 0.15])),
                delta=pref_cfg.get("roi_delta", 0.5),
            )
    return None


def main():
    os.makedirs(os.path.dirname(OUTPUT_EXCEL), exist_ok=True)
    paths = sorted(find_solomon_instances(DATA_DIR, "csv"))
    print(f"Found {len(paths)} instances. Time limit: {TIME_LIMIT}s each.\n")

    pref = load_preference()
    results = []

    for i, path in enumerate(paths):
        inst = VRPTWInstance.load(path)
        name = inst.name
        print(f"[{i+1}/{len(paths)}] {name} ...", end=" ", flush=True)

        t0 = time.time()
        algo = iNSSSO(
            instance=inst,
            n_sol=100,
            cw=0.99,
            cg=0.95,
            n_abs=0.2,
            t_run=TIME_LIMIT,
            preference=pref,
        )
        pareto, info = algo.run()
        runtime = time.time() - t0

        # Best by Z2 (total distance)
        best = min(pareto, key=lambda s: s.objectives[1])
        z1 = int(best.objectives[0])     # vehicles
        z2 = best.objectives[1]          # distance
        z3 = best.objectives[2]          # waiting time
        z4 = best.objectives[3]          # load balance
        z5 = best.objectives[4]          # makespan

        print(f"Z1={z1} Z2={z2:.2f} Z3={z3:.2f} Z4={z4:.2f} Z5={z5:.2f} ({runtime:.1f}s)")

        results.append({
            "Instance": name,
            "Z1(Vehicles)": z1,
            "Z2(Distance)": round(z2, 2),
            "Z3(WaitTime)": round(z3, 2),
            "Z4(LoadBal)": round(z4, 2),
            "Z5(Makespan)": round(z5, 2),
            "PF_Size": len(pareto),
            "Generations": info.get("generations", 0),
            "Runtime(s)": round(runtime, 1),
        })

        # Save immediately to Excel after each instance
        df = pd.DataFrame(results)
        df.to_excel(OUTPUT_EXCEL, index=False)

    print(f"\n{'='*60}")
    print(f"  All results saved to: {OUTPUT_EXCEL}")
    print(f"{'='*60}")

    # Summary
    print(f"\n{'Instance':<12} {'Z1':>4} {'Z2':>10} {'Z3':>10} {'Z4':>8} {'Z5':>10} {'Time':>7}")
    print("-" * 65)
    for r in results:
        print(f"{r['Instance']:<12} {r['Z1(Vehicles)']:>4} {r['Z2(Distance)']:>10.2f} "
              f"{r['Z3(WaitTime)']:>10.2f} {r['Z4(LoadBal)']:>8.2f} "
              f"{r['Z5(Makespan)']:>10.2f} {r['Runtime(s)']:>7.1f}")


if __name__ == "__main__":
    main()
