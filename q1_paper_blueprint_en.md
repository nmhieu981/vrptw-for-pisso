# Paper Blueprint for a Q1 Submission

Working title:

**Preference-Guided iNSSSO for Five-Objective Vehicle Routing with Time Windows: A Code-Aligned Many-Objective Optimization Framework**

This blueprint is intentionally aligned with the current codebase, not with the strongest legacy draft claims.

Master references and claim-status keys live in:

- `q1_evidence_matrix_2024_2026.md`
- `q1_gap_register.md`
- `q1_formulas_and_symbols.tex.md`
- `q1_diagrams_mermaid.md`

## 0. Scope Lock

The paper package is locked to the following facts:

- the problem is a **5-objective VRPTW**,
- the core method is **iNSSSO**,
- preference is active through **ASF, ROI logic, auto-calibrated reference point, and biased reference directions**,
- environmental selection is **NDS + SDE + reference-direction niching**,
- local improvement is **ALNS / ABSearch with adaptive operator scoring**,
- solution preservation uses a **dual archive**.

The paper must not state that:

- the main loop already uses full R-dominance survival selection,
- the local search path already uses SA-based accept/reject logic,
- the released benchmark already includes NSGA-III in the main comparison pipeline.

## 1. Abstract Blueprint

### Purpose

State the practical and methodological problem in one paragraph:

- VRPTW in practice involves multiple conflicting objectives beyond total distance.
- Classical Pareto selection becomes weak as the number of objectives increases.
- Decision makers usually care more about a preferred region than about the entire Pareto front.

### Suggested abstract structure

1. Problem statement:
   "This study addresses a five-objective vehicle routing problem with time windows (VRPTW) under decision-maker preferences."
2. Method:
   "We develop a preference-guided improved non-dominated sorting squirrel search optimizer (iNSSSO) integrating an enhanced SSO update, ALNS-based local improvement, SDE-based many-objective environmental selection, preference-biased reference directions, and a dual archive."
3. Implementation contribution:
   "The released implementation includes a five-objective evaluator, random-key routing representation, auto-calibrated preference management, and preference-aware reporting metrics."
4. Experimental positioning:
   "The current benchmark package compares iNSSSO against six implemented baselines on Solomon-type instances, while also exposing a clear path for future NSGA-III-inclusive validation."
5. Result wording:
   use conservative language such as "shows promising performance" or "demonstrates code-level readiness for broader many-objective benchmarking" unless stronger rerun evidence is added.

## 2. Introduction Blueprint

### 2.1 Problem motivation

Write three short paragraphs:

- logistics routing increasingly requires multi-criteria trade-offs such as fleet size, travel cost, waiting, workload balance, and route completion time;
- many-objective optimization complicates ranking, diversity preservation, and decision support;
- preference-guided search is attractive because decision makers often need a focused subset of solutions.

Recent support:

- multiobjective and time-dependent VRP practice: `[R1]`, `[R13]`
- many-objective VRP trend: `[R5]`
- preference-guided many-objective direction: `[R2]`, `[R3]`, `[R6]`

### 2.2 Research gap statement

Use a compact gap table or gap paragraph:

- recent VRP studies are multiobjective but often limited to 2-3 objectives or problem-specific settings;
- recent many-objective optimization studies are not directly built for VRPTW decision structures;
- recent ALNS-style routing work is strong, but not integrated with the current preference-guided SSO pipeline;
- the repo implementation specifically combines these elements in one working system.

### 2.3 Contribution list

Keep the contribution list limited to code-backed contributions:

1. A five-objective VRPTW implementation with a random-key representation and feasibility-aware evaluation.
2. A preference-guided iNSSSO framework combining ASF-driven exploitation, SDE-based many-objective selection, and biased reference directions.
3. An enhanced SSO move operator with Levy-flight and DE-style perturbation.
4. An ALNS-style local improvement module with five destroy and four repair operators under adaptive scoring.
5. A dual-archive preservation and reinjection mechanism.

Optional sixth contribution only if phrased carefully:

6. A manuscript-ready evidence package that distinguishes implementation-backed claims from benchmark gaps.

## 3. Related Work Blueprint

Organize by themes, not by year-by-year listing.

### 3.1 Recent VRPTW and multiobjective routing

Use:

- `[R1]` for time-dependent multiobjective VRPTW,
- `[R13]` for multiobjective time-dependent routing in logistics,
- `[R7]` and `[R8]` for modern evolutionary VRP variants,
- `[R5]` for large-scale many-objective VRP.

Suggested paragraph ending:

> These studies confirm that practical routing problems are moving toward richer and more conflicting objective sets; however, they still leave room for an integrated preference-guided many-objective metaheuristic that is directly aligned with a five-objective VRPTW workflow.

### 3.2 Recent many-objective search and environmental selection

Use:

- `[R4]` for convergence-diversity balance in MaO,
- `[R7]` for recent NSGA-III-style routing usage,
- `[R2]`, `[R3]`, `[R6]` for preference-focused many-objective reasoning.

Main writing point:

- justify why simple Pareto ranking is not enough,
- motivate SDE and reference-direction biasing,
- connect preference information to a more usable solution region.

### 3.3 Recent ALNS and hybrid routing search

Use:

- `[R8]`, `[R9]`, `[R10]`, `[R11]`, `[R12]`

Main writing point:

- recent routing algorithms still rely heavily on destroy-repair search,
- adaptive local improvement remains one of the most practical routes to better routing quality,
- the novelty here is not ALNS alone, but ALNS inside the current preference-guided iNSSSO framework.

### 3.4 Positioning paragraph

Close Related Work with one clear statement:

> In contrast to recent standalone evolutionary, local-search, or ALNS variants, the present work focuses on a code-realized integration of five-objective evaluation, preference-guided exploitation, many-objective density management, adaptive route-level improvement, and dual-archive preservation within a single search framework.

## 4. Problem Formulation Blueprint

### 4.1 Instance definition

Define:

- depot and customer set,
- coordinates, demand, service time,
- time windows,
- capacity,
- distance and travel-time matrices.

Equations to import:

- from `q1_formulas_and_symbols.tex.md`: capacity feasibility, time-window feasibility, waiting time, completion time.

### 4.2 Solution representation

Describe:

- random-key encoding,
- route separators,
- decode-parse-repair cycle,
- penalty for unserved customers.

### 4.3 Objective vector

Write the five objectives explicitly:

- $Z_1$: used vehicles,
- $Z_2$: total travel distance,
- $Z_3$: total waiting time,
- $Z_4$: load-balance spread,
- $Z_5$: makespan.

Keep this section equation-heavy and code-aligned.

## 5. Proposed Method Blueprint

This should be the longest section.

### 5.1 Overall pipeline

Use Diagram 3 from `q1_diagrams_mermaid.md`.

Describe the loop in this exact order:

1. initialize population,
2. auto-calibrate preference point,
3. rank by NDS + SDE,
4. generate offspring via ALNS or enhanced SSO,
5. evaluate and optionally refine,
6. update dual archive,
7. inject archive solution,
8. select survivors via SDE + reference-direction niching.

### 5.2 Multi-start initialization

Explain:

- best-initialization seed,
- heuristic seed diversity,
- perturbation scales,
- random fill.

Suggested wording:

> Rather than relying on purely random initialization, the implementation seeds the population from several constructive heuristics and then expands it by controlled perturbation, which provides early route diversity without abandoning feasible structure.

### 5.3 Preference management

Cover:

- weight normalization,
- ASF,
- augmented ASF,
- ROI,
- auto-calibration of the preference point.

Use `[R2]`, `[R3]`, `[R6]`.

### 5.4 Environmental selection for many-objective search

Cover:

- NDS,
- SDE,
- biased reference directions,
- niching selection.

Use `[R4]`, `[R7]`, plus foundational `[F3]`, `[F4]` only where needed.

### 5.5 Enhanced SSO update

Cover:

- exploitation with `gbest`,
- conservation of current keys,
- Levy exploration,
- DE perturbation,
- late-stage polynomial mutation.

Use the exact equations from `q1_formulas_and_symbols.tex.md`.

### 5.6 ALNS / ABSearch module

Describe:

- five destroy operators,
- four repair operators,
- adaptive operator scoring,
- route rebuilding and 2-opt post-processing.

Important narrative constraint:

- do not state that SA acceptance is active in the current implementation.

Use `[R8]`, `[R9]`, `[R10]`, `[R11]`, `[R12]`.

### 5.7 Dual archive

Explain:

- convergence archive with epsilon-boxing and ASF tie-breaking,
- diversity archive with Pareto retention and SDE pruning,
- adaptive reinjection.

Use `[R4]` as the recent many-objective motivation and treat the exact archive behavior as the code-specific contribution.

### 5.8 Complexity discussion

Give a compact table:

- objective evaluation,
- SDE,
- reference-direction association,
- ALNS application,
- archive updates.

Keep this section simple and implementation-oriented.

## 6. Experimental Design Blueprint

### 6.1 Benchmark scope

State clearly:

- Solomon-style data format is used in the repo,
- the released comparison runner currently covers six algorithms.

Do not claim a seven-algorithm final benchmark unless rerun.

### 6.2 Baselines

Current benchmarkable set:

- `MOPSO`,
- `NSGA-II`,
- `MOEA/D`,
- `SPEA2`,
- `NSSSO`,
- `iNSSSO`.

Important note:

- `NSGA-III` is implemented in the repo, but not yet part of the main runner.

### 6.3 Metrics

Use:

- HV,
- IGD,
- Coverage,
- Nnds,
- R-HV,
- Best ASF,
- ROI Count.

### 6.4 Statistical protocol

State:

- repeated independent runs,
- mean and standard deviation aggregation,
- nonparametric testing recommended for final paper tables.

If no complete statistical reruns are available yet, write this as the protocol for the paper-ready benchmark phase.

### 6.5 Figure and table roadmap

Suggested figures:

1. system architecture,
2. main loop,
3. enhanced SSO update,
4. ALNS flow,
5. dual archive,
6. pairwise Pareto projections or parallel coordinates,
7. convergence curves,
8. ablation or component-effect plot if rerun later.

Suggested tables:

1. notation,
2. objective functions,
3. algorithm parameters,
4. baseline summary,
5. metrics summary,
6. main benchmark results,
7. preference-focused results,
8. gap-aware limitations.

## 7. Results and Discussion Blueprint

This section must be conservative unless stronger reruns are added.

### 7.1 How to write current results safely

Use wording like:

- "The current implementation produces non-dominated solution sets under the five-objective formulation."
- "The released artifacts indicate that the solver is operational and preference-aware."
- "The current benchmark package supports a six-algorithm comparison and exposes the next validation step, namely NSGA-III-inclusive reruns."

### 7.2 What to analyze

- objective trade-offs,
- preference sensitivity,
- role of SDE and reference-direction niching,
- contribution of ALNS as route-level improvement,
- archive effects on convergence versus spread.

### 7.3 Do not oversell

Avoid language like:

- "state-of-the-art superiority",
- "decisive dominance over all many-objective baselines",
- "full ablation confirmation",

unless those experiments are actually rerun and archived.

## 8. Threats to Validity Blueprint

Include a dedicated section. This helps rather than hurts.

Use the following categories:

- implementation validity:
  some surrounding artifacts still reflect a previous 3-objective stage;
- benchmark validity:
  NSGA-III is not yet part of the active comparison runner;
- metric validity:
  preference metrics are implemented, but their strongest use still depends on broader repeated experiments;
- external validity:
  the released pipeline is tied to Solomon-style instances and should be extended to larger or richer industrial datasets.

## 9. Conclusion Blueprint

Close with three points:

1. the paper presents a code-aligned five-objective preference-guided iNSSSO framework for VRPTW;
2. the strongest implementation-backed components are the enhanced SSO move, ALNS local improvement, SDE-plus-directional selection, and dual archive;
3. the next required step for a final Q1 submission is a broader cleaned benchmark package, especially with NSGA-III integration and gap-free 5-objective reporting artifacts.

## 10. Suggested Ready-to-Write Paragraphs

### Contribution paragraph

> This work develops a code-realized preference-guided iNSSSO framework for a five-objective VRPTW. The implementation integrates a random-key routing representation, a five-objective evaluator, preference management based on ASF and ROI concepts, an enhanced SSO update with Levy-flight and DE-style perturbation, an ALNS-based local improvement path, and a dual-archive preservation mechanism. The resulting framework is designed to support many-objective routing search while keeping the narrative grounded in the actual released implementation.

### Limitation paragraph

> The present paper deliberately separates implementation-backed findings from broader claims that would require additional benchmarking. In particular, while the repository already contains an NSGA-III implementation and several preference-related utilities, the main released benchmark runner currently compares six algorithms and the main iNSSSO loop uses Pareto ranking with SDE density and reference-direction niching rather than full R-dominance survival selection. These distinctions are made explicit to keep the final manuscript technically accurate and reproducible.

## 11. Final Checklist Before Expanding into Full Paper

- lock all prose to the 5-objective definition in `core/objectives.py`
- pull equations only from `q1_formulas_and_symbols.tex.md`
- pull flowcharts only from `q1_diagrams_mermaid.md`
- validate every contribution statement against `q1_evidence_matrix_2024_2026.md`
- keep every nontrivial limitation visible in `q1_gap_register.md`
- use recent references `[R1]`-`[R13]` as the default citation pool
