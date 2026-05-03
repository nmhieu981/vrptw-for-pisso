"""
Batch runner — run iNSSSO on ALL Solomon instances.

For every instance:
  * Print metrics (HV, R-HV, Best ASF, ROI Count) like ``main.py`` mode_single.
  * Save the entire Pareto front to ``results/solutions_{name}.csv``.
  * Save 10 route plots for the best solutions by Z2 (total distance):
        ``results/routes_{name}_distRank01..10.png``.
  * Save ``pareto_{name}.png`` and ``convergence_{name}.png``.
  * Append a one-line summary to ``results/all_results.xlsx`` (rewritten
    after each instance for crash safety).
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
from benchmark.metrics import PerformanceMetrics
from visualization.pareto_plot import plot_pareto_2d
from visualization.convergence_plot import plot_convergence
from visualization.route_visualizer import plot_routes

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_EXCEL = os.path.join(RESULTS_DIR, "all_results.xlsx")
TIME_LIMIT = 600  # seconds per instance
TOP_K_ROUTES = 10  # number of best-by-Z2 solutions to plot per instance


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


def _routes_to_string(routes):
    """Serialize routes (list of lists of customer ids) as `1-3-7|2-5|...`."""
    if not routes:
        return ""
    return "|".join("-".join(str(c) for c in r) for r in routes)


def _save_pareto_csv(pareto, instance_name, pref):
    """Write the entire Pareto front of one instance to CSV."""
    sorted_pf = sorted(
        pareto,
        key=lambda s: (s.objectives[1], s.objectives[0], s.objectives[2]),
    )

    objs = np.array([s.objectives for s in sorted_pf])
    in_roi = None
    if pref is not None and len(objs) > 0:
        ideal = objs.min(axis=0)
        nadir = objs.max(axis=0)
        in_roi = pref.roi_mask(objs, ideal, nadir)

    rows = []
    for i, s in enumerate(sorted_pf):
        o = s.objectives
        if s.routes is None:
            s.decode()
        routes = s.routes or []
        row = {
            "Rank": i + 1,
            "Z1_Vehicles": int(o[0]),
            "Z2_Distance": round(float(o[1]), 4),
            "Z3_WaitTime": round(float(o[2]), 4),
            "Z4_LoadBalance": round(float(o[3]), 4),
            "Z5_Makespan": round(float(o[4]), 4),
            "Unserved": int(s.restcus),
            "Num_Routes": len(routes),
        }
        if pref is not None:
            row["ASF"] = round(float(pref.asf(o)), 6)
            row["ASF_aug"] = round(float(pref.asf_augmented(o)), 6)
            row["In_ROI"] = bool(in_roi[i]) if in_roi is not None else False
        row["Routes"] = _routes_to_string(routes)
        rows.append(row)

    csv_path = os.path.join(RESULTS_DIR, f"solutions_{instance_name}.csv")
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return csv_path, sorted_pf


def _plot_top_routes(top_solutions, instance):
    """Plot up to TOP_K_ROUTES route diagrams for the best-by-Z2 solutions."""
    for i, sol in enumerate(top_solutions):
        rank = i + 1
        z2 = sol.objectives[1]
        fn = f"routes_{instance.name}_distRank{rank:02d}.png"
        plot_routes(
            sol,
            instance,
            save_dir=RESULTS_DIR,
            filename=fn,
            title=f"Routes — {instance.name} (#{rank} by Z2={z2:.2f})",
        )


def _process_instance(inst, pref, results, idx, total):
    """Run the algorithm on a single instance and persist all artefacts."""
    name = inst.name
    print(f"\n{'='*72}")
    print(f"[{idx+1}/{total}] {name}  (customers={inst.n_customers}, "
          f"vehicles={inst.n_vehicles}, capacity={inst.capacity})")
    print(f"{'='*72}")

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

    if not pareto:
        print(f"  WARNING: empty Pareto front for {name}, skipping plots/CSV.")
        results.append({
            "Instance": name,
            "Z1(Vehicles)": None,
            "Z2(Distance)": None,
            "Z3(WaitTime)": None,
            "Z4(LoadBal)": None,
            "Z5(Makespan)": None,
            "PF_Size": 0,
            "Generations": info.get("generations", 0),
            "Runtime(s)": round(runtime, 1),
            "HV": None,
            "Nnds": 0,
            "PF_CSV": None,
        })
        return

    objs = np.array([s.objectives for s in pareto])
    metrics = PerformanceMetrics()
    hv = metrics.hypervolume(objs)
    nnds = metrics.nnds(objs)

    print(f"  Generations : {info.get('generations', 0)}")
    print(f"  Runtime     : {runtime:.1f}s")
    print(f"  PF Size     : {len(pareto)}")
    if pref is not None:
        g_str = ", ".join(f"{v:.4f}" for v in pref.g)
        print(f"  Auto-cal g  : [{g_str}]")
    print(f"  HV          : {hv:.6f}")
    print(f"  Nnds        : {nnds}")

    r_hv = best_asf_val = None
    roi_n = None
    if pref is not None:
        r_hv = metrics.r_hypervolume(objs, pref)
        best_asf_val = metrics.best_asf(objs, pref)
        roi_n = metrics.roi_count(objs, pref)
        print(f"  R-HV        : {r_hv:.6f}")
        print(f"  Best ASF    : {best_asf_val:.6f}")
        print(f"  ROI Count   : {roi_n}/{len(pareto)}")

    best_sol = min(pareto, key=lambda s: s.objectives[1])
    print(f"  Best Dist   : {best_sol.objectives[1]:.2f}  "
          f"({int(best_sol.objectives[0])} routes)")

    if pref is not None:
        best_asf_sol = min(pareto, key=lambda s: pref.asf(s.objectives))
        ob = best_asf_sol.objectives
        print(f"  Best ASF Sol: Z1={int(ob[0])} Z2={ob[1]:.2f} "
              f"Z3={ob[2]:.4f} Z4={ob[3]:.4f} Z5={ob[4]:.2f}  "
              f"ASF={pref.asf(ob):.6f}")

    csv_path, sorted_pf = _save_pareto_csv(pareto, name, pref)
    print(f"  PF CSV      : {os.path.relpath(csv_path)}")

    top_n = min(TOP_K_ROUTES, len(sorted_pf))
    top_by_distance = sorted_pf[:top_n]

    print(f"\n  Top {top_n} solutions by lowest Z2 (total distance):")
    for i, s in enumerate(top_by_distance):
        o = s.objectives
        asf_str = ""
        if pref is not None:
            asf_str = f"  ASF={pref.asf(o):.4f}"
        print(f"    [{i+1}] Z1={int(o[0])} Z2={o[1]:.2f} Z3={o[2]:.4f} "
              f"Z4={o[3]:.4f} Z5={o[4]:.2f}  "
              f"unserved={s.restcus}{asf_str}")

    plot_pareto_2d({"iNSSSO": objs}, name, save_dir=RESULTS_DIR)
    plot_convergence({"iNSSSO": [info["convergence"]]}, name, save_dir=RESULTS_DIR)
    _plot_top_routes(top_by_distance, inst)
    print(f"  Plots saved : pareto_{name}.png, convergence_{name}.png, "
          f"routes_{name}_distRank01..{top_n:02d}.png")

    summary = {
        "Instance": name,
        "Z1(Vehicles)": int(best_sol.objectives[0]),
        "Z2(Distance)": round(float(best_sol.objectives[1]), 2),
        "Z3(WaitTime)": round(float(best_sol.objectives[2]), 4),
        "Z4(LoadBal)": round(float(best_sol.objectives[3]), 4),
        "Z5(Makespan)": round(float(best_sol.objectives[4]), 4),
        "PF_Size": len(pareto),
        "Generations": info.get("generations", 0),
        "Runtime(s)": round(runtime, 1),
        "HV": round(float(hv), 6),
        "Nnds": int(nnds),
        "PF_CSV": os.path.relpath(csv_path),
    }
    if pref is not None:
        summary["R-HV"] = round(float(r_hv), 6)
        summary["Best_ASF"] = round(float(best_asf_val), 6)
        summary["ROI_Count"] = int(roi_n)
    results.append(summary)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    paths = sorted(find_solomon_instances(DATA_DIR, "csv"))
    print(f"Found {len(paths)} instances. Time limit: {TIME_LIMIT}s each.")

    pref = load_preference()
    if pref is not None:
        print(f"Preference active: g={pref.g.tolist()}  w={pref.w.tolist()}  "
              f"delta={pref.delta}")
    else:
        print("Preference: <none>")

    results = []
    for i, path in enumerate(paths):
        inst = VRPTWInstance.load(path)
        _process_instance(inst, pref, results, i, len(paths))

        df = pd.DataFrame(results)
        df.to_excel(OUTPUT_EXCEL, index=False)

    print(f"\n{'='*72}")
    print(f"  All results saved to: {OUTPUT_EXCEL}")
    print(f"{'='*72}")

    # Compact summary table
    if results:
        print(f"\n{'Instance':<12} {'Z1':>4} {'Z2':>10} {'Z3':>10} "
              f"{'Z4':>8} {'Z5':>10} {'Time':>7}")
        print("-" * 65)
        for r in results:
            if r["Z1(Vehicles)"] is None:
                print(f"{r['Instance']:<12} {'-':>4} {'-':>10} {'-':>10} "
                      f"{'-':>8} {'-':>10} {r['Runtime(s)']:>7.1f}")
                continue
            print(f"{r['Instance']:<12} {r['Z1(Vehicles)']:>4} "
                  f"{r['Z2(Distance)']:>10.2f} "
                  f"{r['Z3(WaitTime)']:>10.2f} {r['Z4(LoadBal)']:>8.2f} "
                  f"{r['Z5(Makespan)']:>10.2f} {r['Runtime(s)']:>7.1f}")


if __name__ == "__main__":
    main()
