# Q1 Gap Register

This register lists the gaps between:

- the current implementation,
- the current result artifacts,
- and the strongest possible paper narrative.

The intended use is simple:

- write the paper from the `E1` core,
- mention `E2` gaps honestly,
- move `E3` and `E4` items to limitations or future work.

## Gap Summary

| Gap ID | Severity | Gap | Repo evidence | Paper impact | Action for writing |
|---|---|---|---|---|---|
| G1 | High | Legacy 3-objective artifacts still exist in plots and saved logs. | `visualization/pareto_plot.py:27-30`, `test_results.txt:9`, `test_results.txt:29`, `result_output.txt:38` | A reviewer can immediately question whether the study is truly 5-objective end-to-end. | Do not use those artifacts as primary figures or evidence. State that the paper package is locked to the 5-objective code path in `core/objectives.py` and `algorithm/inssso.py`. |
| G2 | High | The benchmark runner still uses `np.empty((0, 3))` as a fallback shape, even though the working model has 5 objectives. | `benchmark/runner.py:102`, `benchmark/runner.py:135` | Weakens reproducibility claims for a strict 5-objective benchmark pipeline. | Mention as a reproducibility gap. Avoid claiming the runner is already fully sanitized for 5-objective experiments. |
| G3 | High | `NSGA-III` exists in the repo but is not included in the main comparison workflow. | `comparison/nsga3.py:36-221`, `benchmark/runner.py:121-122` | A many-objective paper without an active NSGA-III benchmark can look incomplete. | In the paper, call NSGA-III a missing-but-important comparison, not a completed baseline. |
| G4 | High | The main loop imports R-dominance helpers but does not use them for environmental ranking or survivor selection. | `algorithm/inssso.py:35-37`, `algorithm/inssso.py:625`, `algorithm/inssso.py:707` | The paper must not claim that the whole algorithm is ranked by R-dominance. | Write that preferences are injected via ASF-guided leader choice, ROI logic, archive pruning, and biased reference directions. |
| G5 | High | The ALNS class advertises simulated annealing variables, but the `apply()` path does not implement SA acceptance or rejection logic. | `algorithm/abs_search.py:104-115`, `algorithm/abs_search.py:451-536` | Any claim about "ALNS with SA acceptance" is currently inaccurate. | Write adaptive operator scoring only. Mention SA acceptance as future extension unless the code is updated later. |
| G6 | Medium | `NSGA-III` and `MOEA/D` baseline utilities appear to call `das_dennis()` with reversed argument order. | `comparison/nsga3.py:58-59`, `comparison/moead.py:32`, `comparison/moead.py:37`, `algorithm/reference_dirs.py:15` | Comparative fairness may be challenged if those baselines are used without correction. | Keep this in the internal gap register; do not discuss in the paper unless the baselines are repaired and rerun. |
| G7 | Medium | The current visualization scripts are tailored to 3D/3-objective projections only. | `visualization/pareto_plot.py:27-30`, `visualization/pareto_plot.py:73-89` | The paper cannot rely on the existing plotting layer for 5-objective presentation. | Use custom figure plans in the blueprint: pairwise projections, radar/parallel coordinates, and metric tables. |
| G8 | Medium | Some existing draft files are garbled by encoding and cannot be reused safely. | `paper_q1_full.md`, `algorithm_flowcharts.md`, `INSTALL.md` contain mixed-encoding or legacy text | Reusing old prose risks hidden inconsistencies and malformed text. | Treat all old drafts as idea banks only, not as source text. |
| G9 | Medium | Current comparison runner covers six algorithms, but the old draft claims seven-algorithm benchmarking. | `benchmark/runner.py:121-122`, legacy draft statements in `paper_q1_full.md` | A reviewer may flag mismatch between method section and released artifacts. | Write the current comparison set as six algorithms. Mention NSGA-III as an implementation-ready extension. |
| G10 | Medium | Current repo does not contain a completed ablation execution pipeline, although draft text discusses extensive ablation. | no dedicated end-to-end ablation results archive is present | Overclaiming ablation completeness will undermine credibility. | Keep ablation as a required experiment design, not as completed evidence unless rerun and archived. |
| G11 | Low | `git status` cannot be trusted without fixing safe-directory settings for this environment. | shell output reported dubious ownership | Does not affect the paper itself, but affects provenance and cleanliness checks. | Ignore for manuscript writing; fix only if code provenance is later needed. |

## Safe Narrative Core

If you need the shortest safe narrative for the article, use this:

1. The codebase currently implements a 5-objective preference-guided VRPTW solver based on enhanced SSO, ALNS-style local improvement, SDE-based many-objective environmental selection, preference-biased reference directions, and a dual archive.
2. The strongest implementation-backed contributions are the 5-objective formulation, the enhanced SSO operator, the ALNS module, the SDE-plus-reference-direction selection path, and the dual archive.
3. The paper must explicitly separate what is already benchmarked from what is implemented but not yet fully benchmarked.

## Claims That Are Safe Today

- "Our implementation addresses a five-objective VRPTW."
- "Preference information influences leader choice, archive behavior, and direction bias."
- "The algorithm integrates enhanced SSO exploration, local improvement, and dual-archive preservation."
- "The released runner currently compares six algorithms and leaves NSGA-III integration as an immediate next step."

## Claims That Need New Experiments Before They Are Safe

- "The method decisively outperforms NSGA-III on many-objective VRPTW."
- "The method is validated by a complete seven-algorithm benchmark."
- "The active implementation uses R-dominance ranking in the full selection loop."
- "The local search path uses simulated annealing acceptance."

## Suggested Limitation Paragraph

Use a paragraph close to the following in the eventual paper if needed:

> The current code release already contains the full five-objective evaluation model and the integrated preference-guided iNSSSO search pipeline. However, some surrounding research artifacts still reflect earlier three-objective experiments, and the public benchmark runner has not yet incorporated the repository's NSGA-III implementation into the main comparison suite. In addition, while preference-related utilities such as R-dominance are present in the codebase, the current main loop uses Pareto ranking with SDE density and reference-direction niching rather than full R-dominance survival selection. These gaps do not affect the core algorithmic implementation, but they define the boundary between claims that are implementation-backed and claims that require additional benchmarking before final journal submission.
