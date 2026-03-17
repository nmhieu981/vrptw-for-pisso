"""
Ablation Study Framework
========================
Systematically disable individual components of iNSSSO to measure
their contribution to overall performance.

Variants tested:
  V0: Full iNSSSO (all components)
  V1: No Lévy flight (standard SSO exploration)
  V2: No DE perturbation (standard SSO exploration)
  V3: No ALNS (disable local search entirely)
  V4: No dual archive (single ε-dominance archive only)
  V5: No preference guidance (pure Pareto-based)
  V6: No SDE (use crowding distance instead)
  V7: No adaptive parameters (fixed n_abs, mutation_rate)
  V8: No polynomial mutation

For each variant, compute:
  - HV (hypervolume)
  - R-HV (reference-based hypervolume)
  - Best ASF
  - ROI count
  - IGD
  - Runtime

Report: Δ% = (metric_V0 - metric_Vk) / metric_V0 × 100

This framework is essential for Q1 papers to justify each proposed
component's contribution (required by reviewers).
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from core.problem import VRPTWInstance
from core.preference import UserPreference

logger = logging.getLogger(__name__)


@dataclass
class AblationVariant:
    name: str
    description: str
    config_overrides: Dict[str, Any] = field(default_factory=dict)


ABLATION_VARIANTS = [
    AblationVariant(
        name="V0_full",
        description="Full iNSSSO (all components enabled)",
    ),
    AblationVariant(
        name="V1_no_levy",
        description="Disable Lévy flight exploration",
        config_overrides={"disable_levy": True},
    ),
    AblationVariant(
        name="V2_no_de",
        description="Disable differential evolution perturbation",
        config_overrides={"disable_de": True},
    ),
    AblationVariant(
        name="V3_no_alns",
        description="Disable ALNS local search (n_abs=0)",
        config_overrides={"n_abs": 0.0},
    ),
    AblationVariant(
        name="V4_single_archive",
        description="Single ε-dominance archive (no diversity archive)",
        config_overrides={"single_archive": True},
    ),
    AblationVariant(
        name="V5_no_preference",
        description="Disable preference guidance (pure Pareto-based)",
        config_overrides={"preference": None},
    ),
    AblationVariant(
        name="V6_no_sde",
        description="Replace SDE with crowding distance",
        config_overrides={"use_crowding_distance": True},
    ),
    AblationVariant(
        name="V7_no_adaptive",
        description="Fixed parameters (no adaptive n_abs, mutation_rate)",
        config_overrides={"adaptive_params": False},
    ),
    AblationVariant(
        name="V8_no_mutation",
        description="Disable polynomial mutation",
        config_overrides={"mutation_rate": 0.0},
    ),
]


@dataclass
class AblationResult:
    variant_name: str
    metrics: Dict[str, float]
    runtime: float
    generations: int


class AblationStudy:
    """
    Run ablation study across all variants on specified instances.

    Usage:
        study = AblationStudy(instance, preference, base_config)
        results = study.run_all(n_runs=5)
        study.report(results)
    """

    def __init__(
        self,
        instance: VRPTWInstance,
        preference: Optional[UserPreference] = None,
        base_config: Optional[Dict[str, Any]] = None,
    ):
        self.inst = instance
        self.pref = preference
        self.base_config = base_config or {
            "n_sol": 100,
            "t_run": 60.0,
            "n_abs": 0.2,
        }

    def _create_algorithm(self, variant: AblationVariant):
        """Create an iNSSSO instance with the variant's overrides applied."""
        from algorithm.inssso import iNSSSO

        config = copy.deepcopy(self.base_config)
        pref = self.pref

        for key, val in variant.config_overrides.items():
            if key == "preference":
                pref = val
            else:
                config[key] = val

        algo = iNSSSO(
            instance=self.inst,
            n_sol=config.get("n_sol", 100),
            t_run=config.get("t_run", 60.0),
            n_abs=config.get("n_abs", 0.2),
            preference=pref,
        )

        if config.get("disable_levy"):
            algo._disable_levy = True
        if config.get("disable_de"):
            algo._disable_de = True
        if config.get("adaptive_params") is False:
            algo._adaptive_enabled = False
        if config.get("mutation_rate") == 0.0:
            algo.mutation_rate = 0.0

        return algo

    def run_variant(self, variant: AblationVariant,
                    n_runs: int = 5) -> List[AblationResult]:
        """Run a single variant n_runs times."""
        from benchmark.metrics import PerformanceMetrics

        results = []
        for run_id in range(n_runs):
            logger.info("Ablation %s, run %d/%d", variant.name, run_id + 1, n_runs)

            algo = self._create_algorithm(variant)
            pareto, info = algo.run()

            obj_matrix = np.array([s.objectives for s in pareto])
            metrics_calc = PerformanceMetrics(self.pref)
            metrics = metrics_calc.compute_all(obj_matrix, obj_matrix)

            results.append(AblationResult(
                variant_name=variant.name,
                metrics=metrics,
                runtime=info["runtime"],
                generations=info["generations"],
            ))

        return results

    def run_all(self, n_runs: int = 5,
                variants: Optional[List[AblationVariant]] = None
                ) -> Dict[str, List[AblationResult]]:
        """Run all ablation variants."""
        if variants is None:
            variants = ABLATION_VARIANTS

        all_results: Dict[str, List[AblationResult]] = {}
        for variant in variants:
            all_results[variant.name] = self.run_variant(variant, n_runs)

        return all_results

    @staticmethod
    def report(results: Dict[str, List[AblationResult]]) -> str:
        """
        Generate a formatted ablation report.

        Computes mean ± std for each metric, and Δ% relative to V0_full.
        """
        lines = ["=" * 80]
        lines.append("ABLATION STUDY REPORT")
        lines.append("=" * 80)

        v0_means: Dict[str, float] = {}
        if "V0_full" in results:
            v0_runs = results["V0_full"]
            metric_names = list(v0_runs[0].metrics.keys()) if v0_runs else []
            for mn in metric_names:
                vals = [r.metrics.get(mn, 0) for r in v0_runs]
                v0_means[mn] = float(np.mean(vals))

        for vname, runs in results.items():
            lines.append(f"\n--- {vname} ---")
            if not runs:
                lines.append("  No runs.")
                continue

            metric_names = list(runs[0].metrics.keys())
            for mn in metric_names:
                vals = [r.metrics.get(mn, 0) for r in runs]
                mean_val = float(np.mean(vals))
                std_val = float(np.std(vals))

                delta_str = ""
                if vname != "V0_full" and mn in v0_means and v0_means[mn] != 0:
                    delta = (v0_means[mn] - mean_val) / abs(v0_means[mn]) * 100
                    delta_str = f"  (Δ = {delta:+.2f}%)"

                lines.append(f"  {mn:20s}: {mean_val:.4f} ± {std_val:.4f}{delta_str}")

            runtimes = [r.runtime for r in runs]
            lines.append(f"  {'runtime':20s}: {np.mean(runtimes):.1f}s ± {np.std(runtimes):.1f}s")

        lines.append("\n" + "=" * 80)
        report_text = "\n".join(lines)
        logger.info(report_text)
        return report_text
