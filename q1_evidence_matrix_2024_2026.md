# Q1 Evidence Matrix (2024-2026 First, Minimal Foundational Exceptions)

This file is the master evidence register for the new paper package.

Use it as the source of truth for:

- what is implemented in the repo,
- what is supported by current experimental artifacts,
- what must be written as a conditional or future-validation claim,
- which recent references can be cited for each argument.

## Status Legend

- `E1 - Implemented and evidenced`: directly supported by current code and repo artifacts.
- `E2 - Implemented, but benchmark coverage is incomplete`: code exists, but comparative validation is incomplete or inconsistent.
- `E3 - Utility exists, not active in the main experimental path`: present in repo, but not actually used in the current main loop or benchmark workflow.
- `E4 - Do not overclaim`: draft language exists, but current code/results do not justify a strong paper claim.

## Claim Matrix

| ID | Claim to write | Status | Repo evidence | Writing rule | Recent support |
|---|---|---:|---|---|---|
| C1 | The working problem formulation is a 5-objective MO-VRPTW with `Z1` vehicles, `Z2` travel distance, `Z3` waiting time, `Z4` load balance, and `Z5` makespan. | E1 | `core/objectives.py:2-25`, `core/objectives.py:136-172`, `config/params.yaml:18-20` | Write as a hard implementation fact. | [R1], [R5], [R7], [R13] |
| C2 | The solution representation is random-key encoding with route separators and a decode-parse-repair workflow. | E1 | `core/solution.py:8-15`, `core/solution.py:66-128`, `core/solution.py:163-280` | Write as the canonical encoding section. | [R12] |
| C3 | The initial population is multi-start, built from best-initialization, insertion heuristics, Clarke-Wright, nearest-neighbour, perturbation, and random fill. | E1 | `algorithm/inssso.py:349-414` | Write as an implemented hybrid initialization, not as an exact meta-learning strategy. | [R1], [R8], [R12] |
| C4 | Preference handling is implemented through `g`, `w`, `delta`, ASF, augmented ASF, ROI masks, and auto-calibration of the reference point. | E1 | `core/preference.py:16-107`, `algorithm/inssso.py:299-347` | Write as an active preference layer. | [R2], [R3], [R6] |
| C5 | The main selection backbone of `iNSSSO` is Pareto sorting plus SDE density and reference-direction niching. | E1 | `algorithm/inssso.py:625-707`, `algorithm/crowding.py:20-96`, `algorithm/reference_dirs.py:15-219` | Write this as the main environmental selection mechanism. | [R4], [R7] |
| C6 | Preference-biased reference directions are implemented to bias environmental selection toward the preferred region while keeping a uniform layer. | E1 | `algorithm/inssso.py:281-295`, `algorithm/reference_dirs.py:42-98` | Write as an implemented mechanism; avoid claiming formal optimality. | [R3], [R4], [R6] |
| C7 | `gBest` is selected by ASF among Pareto-rank-0 candidates when preferences are enabled. | E1 | `algorithm/inssso.py:657-660`, `algorithm/r_dominance.py:136-158` | Write as an exploitation guidance mechanism. | [R2], [R6] |
| C8 | The SSO update is enhanced with Levy flight and DE-style perturbation in the exploration band. | E1 | `algorithm/inssso.py:416-490` | Write as a concrete operator-level enhancement. | [R4], [R11] |
| C9 | The local improvement path uses `ABSearch = ALNSearch` with five destroy operators and four repair operators, plus adaptive operator scoring. | E1 | `algorithm/abs_search.py:94-110`, `algorithm/abs_search.py:124-515`, `algorithm/abs_search.py:540` | Write as an implemented ALNS module. | [R8], [R9], [R10], [R11] |
| C10 | The archive is dual: a convergence archive with epsilon-boxing and a diversity archive pruned by SDE, with adaptive archive injection back into the offspring pool. | E1 | `algorithm/inssso.py:54-228`, `algorithm/inssso.py:693-701` | Write as an implemented dual-archive strategy. | [R4], [R10] |
| C11 | The algorithm adapts `n_abs` and mutation rate according to progress and stagnation. | E1 | `algorithm/inssso.py:575-605` | Write as an implemented adaptive control mechanism. | [R4], [R8] |
| C12 | Preference-aware metrics `R-HV`, `Best_ASF`, and `ROI_Count` are implemented. | E1 | `benchmark/metrics.py:81-139`, `benchmark/metrics.py:164-176` | Write as implemented metrics, but do not imply a large preference benchmark unless results are added. | [R2], [R6] |
| C13 | The current benchmark runner compares six algorithms: `MOPSO`, `NSGA-II`, `MOEA/D`, `SPEA2`, `NSSSO`, and `iNSSSO`. | E1 | `benchmark/runner.py:31-38`, `benchmark/runner.py:121-139` | Write exactly this set in the current paper package. | [R7], [R8] |
| C14 | `NSGA-III` is implemented in the repo but is not part of the current benchmark runner. | E2 | `comparison/nsga3.py:36-221`, `benchmark/runner.py:121-122` | Mention as a missing-but-important baseline, not as a completed comparison. | [R7] |
| C15 | R-dominance utilities exist in the repo. | E3 | `algorithm/r_dominance.py:1-158` | Only mention as an available utility or future extension. Do not claim that the main loop uses R-dominance ranking. | [R2], [R6] |
| C16 | The main loop does not currently use `r_assign_rank_and_crowding` or `select_best_r`; it uses `assign_rank_and_sde` and `select_best`. | E1 | `algorithm/inssso.py:625`, `algorithm/inssso.py:707`, `algorithm/inssso.py:35-36` | Use this to keep the paper narrative honest. | none |
| C17 | The repo contains comparison and visualization artifacts that still assume 3 objectives. | E1 | `visualization/pareto_plot.py:27-30`, `test_results.txt:9`, `test_results.txt:29`, `result_output.txt:38` | Treat them as legacy artifacts; do not use them as primary 5-objective evidence. | none |
| C18 | The benchmark workflow still contains 3-objective empty-array fallbacks. | E1 | `benchmark/runner.py:102`, `benchmark/runner.py:135` | Mention this as a reproducibility gap in the limitations register. | none |
| C19 | The ALNS class declares simulated annealing temperature variables, but the `apply()` path does not implement SA-based acceptance. | E1 | `algorithm/abs_search.py:104-115`, `algorithm/abs_search.py:451-536` | Do not write "ALNS with SA acceptance" as an active implementation claim. | [R8], [R9] |
| C20 | Some baseline many-objective utilities likely have reference-direction argument-order mismatches. | E1 | `comparison/nsga3.py:58-59`, `comparison/moead.py:24-37` | Mention only in the gap register, not in the main algorithm contribution section. | none |

## Suggested Claim Language

### Safe, direct claims

- "The proposed implementation solves a five-objective VRPTW with preference-guided search."
- "Environmental selection combines Pareto ranking, shift-based density estimation, and reference-direction niching."
- "The search process integrates an enhanced SSO update, an ALNS local improvement path, and a dual archive."

### Conditional claims

- "The current codebase is structured to support preference-oriented many-objective search."
- "The current experimental package suggests that the method is ready for a stronger NSGA-III-inclusive comparison, but that benchmark is not yet part of the main runner."

### Claims to avoid in the current paper package

- "The main loop uses R-dominance ranking throughout environmental selection."
- "The ALNS module uses a fully implemented SA acceptance rule."
- "The paper already demonstrates fair seven-algorithm many-objective benchmarking."

## Recent Reference Set (Primary Writing Pool, 2024-2026)

Use these keys throughout the other files.

- `[R1]` T. F. Abdelmaguid, "An improved multiobjective evolutionary algorithm for time-dependent vehicle routing problem with time windows," *Egyptian Informatics Journal*, vol. 28, art. 100574, 2024. DOI: [10.1016/j.eij.2024.100574](https://doi.org/10.1016/j.eij.2024.100574)
- `[R2]` D. Yadav, P. Ramu, and K. Deb, "An Updated Performance Metric for Preference-Based Evolutionary Multi-Objective Optimization Algorithms," in *GECCO '24*, 2024. PDF: [MSU technical copy](https://www.egr.msu.edu/~kdeb/papers/c2024003.pdf)
- `[R3]` R. Ye, L. Chen, J. Zhang, and H. Ishibuchi, "Evolutionary Preference Sampling for Pareto Set Learning," *GECCO 2024* / CoRR abs/2404.08414, 2024. URL: [arXiv 2404.08414](https://arxiv.org/abs/2404.08414)
- `[R4]` X. Wang, F. Zhang, and M. Yao, "Dynamic decomposition and hyper-distance based many-objective evolutionary algorithm," *Complex & Intelligent Systems*, vol. 11, art. 85, 2025. DOI: [10.1007/s40747-024-01637-3](https://doi.org/10.1007/s40747-024-01637-3)
- `[R5]` Y. Zhou, L. Kong, H. Wang, Y. Cai, and S. Liu, "A local search with chain search path strategy for real-world many-objective vehicle routing problem," *Complex & Intelligent Systems*, vol. 11, art. 199, 2025. DOI: [10.1007/s40747-025-01825-9](https://doi.org/10.1007/s40747-025-01825-9)
- `[R6]` P. Zhao, L. Wang, and Q. Qiu, "Preference-based expensive multi-objective optimization without using an ideal point," *Complex & Intelligent Systems*, vol. 11, art. 317, 2025. DOI: [10.1007/s40747-025-01905-w](https://doi.org/10.1007/s40747-025-01905-w)
- `[R7]` X. Liu et al., "Research on Multi-Objective Green Vehicle Routing Problem with Time Windows Based on the Improved Non-Dominated Sorting Genetic Algorithm III," *Symmetry*, vol. 17, no. 5, art. 734, 2025. DOI: [10.3390/sym17050734](https://doi.org/10.3390/sym17050734)
- `[R8]` H. Jiang, Z. Zhang, C. Wang, and X. Xiang, "A multiobjective evolutionary algorithm incorporating neighborhood detection for the vehicle routing problem with soft time windows," *Complex & Intelligent Systems*, vol. 11, art. 419, 2025. DOI: [10.1007/s40747-025-02044-y](https://doi.org/10.1007/s40747-025-02044-y)
- `[R9]` H. Ma and T. Yang, "Improved Adaptive Large Neighborhood Search Combined with Simulated Annealing (IALNS-SA) Algorithm for Vehicle Routing Problem with Simultaneous Delivery and Pickup and Time Windows," *Electronics*, vol. 14, no. 12, art. 2375, 2025. DOI: [10.3390/electronics14122375](https://doi.org/10.3390/electronics14122375)
- `[R10]` Z. Wu, P. Lou, J. Hu, Y. Zeng, and C. Fan, "An Adaptive Large Neighborhood Search for a Green Vehicle Routing Problem with Depot Sharing," *Mathematics*, vol. 13, no. 2, art. 214, 2025. DOI: [10.3390/math13020214](https://doi.org/10.3390/math13020214)
- `[R11]` M. He et al., "Time-Dependent Vehicle Routing Problem with Simultaneous Pickup-and-Delivery and Time Windows Considering Carbon Emission Costs Using an Improved Ant Colony Optimization Algorithm," *Sustainability*, vol. 18, no. 3, art. 1430, 2026. DOI: [10.3390/su18031430](https://doi.org/10.3390/su18031430)
- `[R12]` X. Wei, Z. Xiao, and Y. Wang, "Solving the Vehicle Routing Problem with Time Windows Using Modified Rat Swarm Optimization Algorithm Based on Large Neighborhood Search," *Mathematics*, vol. 12, no. 11, art. 1702, 2024. DOI: [10.3390/math12111702](https://doi.org/10.3390/math12111702)
- `[R13]` Y. Li et al., "Collaboration and resource sharing in the multidepot time-dependent vehicle routing problem with time windows," *Transportation Research Part E: Logistics and Transportation Review*, vol. 192, art. 103798, 2024. DOI: [10.1016/j.tre.2024.103798](https://doi.org/10.1016/j.tre.2024.103798)

## Minimal Foundational Exceptions

Keep these only where the paper needs the original source of a classical method or model.

- `[F1]` M. M. Solomon, "Algorithms for the vehicle routing and scheduling problems with time window constraints," *Operations Research*, 1987.
- `[F2]` A. P. Wierzbicki, "The use of reference objectives in multiobjective optimization," 1980.
- `[F3]` K. Deb and H. Jain, "An evolutionary many-objective optimization algorithm using reference-point-based nondominated sorting approach," *IEEE TEC*, 2014.
- `[F4]` K. Li et al., "Shift-Based Density Estimation for Pareto-Based Algorithms in Many-Objective Optimization," *IEEE TEC*, 2014.
- `[F5]` M. Jain, V. Singh, and A. Rani, "A novel nature-inspired algorithm for optimization: Squirrel search algorithm," *Swarm and Evolutionary Computation*, 2019.
- `[F6]` R. N. Mantegna, "Fast, accurate algorithm for numerical simulation of Levy stable stochastic processes," *Physical Review E*, 1994.
- `[F7]` R. Storn and K. Price, "Differential evolution - a simple and efficient heuristic for global optimization over continuous spaces," *Journal of Global Optimization*, 1997.

## Writing Policy for the New Paper

1. Use `[R1]`-`[R13]` as the default citation pool in the main text.
2. Use `[F1]`-`[F7]` only when the paper needs the original classical source.
3. Never cite legacy repo outputs as scientific evidence for the final paper.
4. If a section needs a claim that is only `E2`, mark it in prose as:
   "implemented in the current codebase, but requiring broader benchmark validation."
5. If a section touches `E3` or `E4`, move it to:
   limitations, future work, or codebase improvement notes.
