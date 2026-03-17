# Q1 Diagrams (Mermaid, Code-Aligned)

These diagrams are intentionally aligned with the current implementation, not with the strongest possible draft narrative.

Citation and claim keys are defined in `q1_evidence_matrix_2024_2026.md`.

## Diagram 1: System Architecture

```mermaid
flowchart TB
    A["Solomon instance loader"] --> B["VRPTWInstance"]
    B --> C["Solution encoding and parser"]
    C --> D["Five-objective evaluator"]
    P["UserPreference (g, w, delta)"] --> E["Preference layer"]

    D --> F["iNSSSO main loop"]
    E --> F

    F --> G["Enhanced SSO update"]
    F --> H["ALNS / ABSearch"]
    F --> I["NDS + SDE ranking"]
    F --> J["Preference-biased reference directions"]
    F --> K["Dual archive"]

    I --> L["Environmental selection"]
    J --> L
    K --> L

    L --> M["Pareto / archive output"]
    M --> N["Metrics: HV, R-HV, Best ASF, ROI Count"]
```

## Diagram 2: Data Flow from Raw Instance to Final Objective Vector

```mermaid
flowchart LR
    A["CSV/TXT instance"] --> B["Distance and travel-time matrices"]
    B --> C["Random-key solution X"]
    C --> D["Decode via argsort"]
    D --> E["Routes with separators removed"]
    E --> F["Feasibility parse and repair"]
    F --> G["Route details: distance, waits, completion"]
    G --> H["Z1..Z5 evaluation"]
    H --> I["Preference evaluation: ASF, ROI"]
```

## Diagram 3: iNSSSO Main Loop

```mermaid
flowchart TD
    S["Start"] --> I0["Initialize population"]
    I0 --> I1["Auto-calibrate preference g"]
    I1 --> I2["Update dual archive with initial population"]
    I2 --> T{"Time budget reached?"}

    T -- "No" --> R0["Rank current population with NDS + SDE"]
    R0 --> R1["Track convergence and adapt n_abs / mutation rate"]
    R1 --> O0["Generate offspring"]

    O0 --> B0{"Random < n_abs?"}
    B0 -- "Yes" --> A0["Apply ALNS / ABSearch"]
    B0 -- "No" --> G0{"Preference enabled?"}
    G0 -- "Yes" --> G1["Select gBest by ASF from rank-0 set"]
    G0 -- "No" --> G2["Select gBest by SDE tournament"]
    G1 --> U0["Enhanced SSO update"]
    G2 --> U0
    U0 --> U1{"Stagnation and mutation trigger?"}
    U1 -- "Yes" --> U2["Polynomial mutation"]
    U1 -- "No" --> E0["Decode, parse, evaluate offspring"]
    U2 --> E0

    A0 --> E0
    E0 --> L0{"Local-search trigger?"}
    L0 -- "Yes" --> L1["Apply route-level local search"]
    L0 -- "No" --> O1["Store offspring"]
    L1 --> O1

    O1 --> O2{"More offspring to build?"}
    O2 -- "Yes" --> B0
    O2 -- "No" --> A1["Update dual archive with offspring"]
    A1 --> A2["Inject one archive solution adaptively"]
    A2 --> M0["Merge parent and offspring pools"]
    M0 --> M1["Select survivors by NDS + SDE + ref-dir niching"]
    M1 --> T

    T -- "Yes" --> F0["Update archive with final population"]
    F0 --> F1["Return archive solutions or rank-0 population"]
    F1 --> E["End"]
```

## Diagram 4: Enhanced SSO Update

```mermaid
flowchart LR
    A["Current solution xi"] --> B["Sample rho per decision variable"]
    G["gbest"] --> C
    R1["xr1"] --> D
    R2["xr2"] --> D

    B --> C{"rho <= cg ?"}
    C -- "Yes" --> C1["Copy gbest key"]
    C -- "No" --> D0{"rho <= cw ?"}
    D0 -- "Yes" --> D1["Keep current key"]
    D0 -- "No" --> E0{"rho <= cl ?"}
    E0 -- "Yes" --> E1["Levy step toward gbest"]
    E0 -- "No" --> D["DE-style perturbation"]

    C1 --> Z["Clip to [0, 0.999] and rebuild solution"]
    D1 --> Z
    E1 --> Z
    D --> Z
```

## Diagram 5: ALNS / ABSearch Flow

```mermaid
flowchart TD
    A["Input solution"] --> B["Decode and parse routes"]
    B --> C["Sample number of customers to remove"]
    C --> D["Select destroy operator by roulette weights"]
    D --> E["Destroy route structure"]
    E --> F["Select repair operator by roulette weights"]
    F --> G["Repair with regret-2 / regret-3 / greedy / astar-build"]
    G --> H["Post-process with quick 2-opt"]
    H --> I["Re-encode routes to random-key solution"]
    I --> J["Update iteration count and operator segments"]
    J --> K["Return repaired solution"]
```

## Diagram 6: Dual Archive Logic

```mermaid
flowchart TB
    A["Candidate solution"] --> B["Convergence archive branch"]
    A --> C["Diversity archive branch"]

    B --> B1["Compute epsilon box"]
    B1 --> B2{"Same epsilon box already exists?"}
    B2 -- "Yes" --> B3["Keep lower ASF representative"]
    B2 -- "No" --> B4["Apply Pareto replacement checks"]
    B3 --> B5["Convergence archive updated"]
    B4 --> B5

    C --> C1["Apply Pareto-dominance insertion only"]
    C1 --> C2["Keep all non-dominated candidates"]
    C2 --> C3{"Archive size exceeded?"}
    C3 -- "Yes" --> C4["Prune by SDE, keep isolated points"]
    C3 -- "No" --> C5["Diversity archive updated"]
    C4 --> C5

    B5 --> D["Adaptive archive injection"]
    C5 --> D
    D --> E["Bias toward convergence archive as stagnation grows"]
```

## Diagram 7: Preference Layer

```mermaid
flowchart LR
    A["User reference point g"] --> D["Preference engine"]
    B["Weight vector w"] --> D
    C["ROI radius delta"] --> D

    O["Objective vector f(x)"] --> D

    D --> E["ASF and ASF_aug"]
    D --> F["ROI mask"]
    D --> G["Weighted distance"]
    D --> H["Preference-biased directions"]

    E --> I["gBest selection"]
    E --> J["Convergence archive pruning"]
    F --> K["R-HV and ROI count metrics"]
    H --> L["Niching bias in survivor selection"]
```

## Diagram 8: Benchmark and Reporting Pipeline

```mermaid
flowchart TD
    A["ExperimentRunner"] --> B["Load instance"]
    B --> C["Run each configured algorithm"]
    C --> D["Collect Pareto fronts across runs"]
    D --> E["Estimate shared nondominated reference set"]
    E --> F["Compute metrics per run"]
    F --> G["Aggregate mean and std"]
    G --> H["Export comparison CSV / tables"]

    H --> I["Paper figures"]
    H --> J["Paper tables"]
    H --> K["Ablation design notes"]
```

## Figure Policy

Use these diagrams in the manuscript as follows:

- Fig. 1: Diagram 1 or Diagram 2
- Fig. 2: Diagram 3
- Fig. 3: Diagram 4
- Fig. 4: Diagram 5
- Fig. 5: Diagram 6
- Fig. 6: Diagram 7
- Fig. 7: Diagram 8

Do not reuse old flowcharts that mention:

- three-objective outputs only,
- full R-dominance survival selection,
- simulated annealing acceptance inside ALNS,
- seven-algorithm benchmark completion.
