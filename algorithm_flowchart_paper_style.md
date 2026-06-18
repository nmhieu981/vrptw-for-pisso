# Flowchart of the Proposed iNSSSO (Paper Style)

> Sơ đồ theo phong cách Fig.1 của bài báo, nhưng phản ánh đúng code thực tế.

---

## Fig. 1 — Flowchart Chính của iNSSSO

```mermaid
flowchart TD
    START(["Start"]) --> INIT

    INIT["Initialize population X⁰"]
    INIT -.- INIT_NOTE["• X₁ using best_initialization():\n   Clarke-Wright, Insertion Heuristic (×6),\n   Nearest Neighbour → full_local_search()\n   on top-2 → ruin_and_recreate()\n• Xᵢ for i = 2,...,nSol:\n   Perturbation (noise 0.05–0.15)\n   + Random fill"]

    INIT --> CALIB["Auto-calibrate reference point g\ng = ideal + 0.1 × (p₁₀ − ideal)"]

    CALIB --> RANK1["Classify and rank the\npopulation into distinct\nfronts ψ₁, ψ₂, ..., ψₖ"]
    RANK1 -.- RANK1_NOTE["• Non-dominated Sorting (NDS)\n• SDE density estimation\n  (replaces Crowding Distance)"]

    RANK1 --> ARCHIVE_INIT["Update DualArchive\nwith initial population"]

    ARCHIVE_INIT --> SET_I["i = 1"]

    SET_I --> CHECK_RHO{"Is ρ < nALNS ?"}

    CHECK_RHO -- "Yes" --> ALNS["Produce Yᵢ using ALNS"]
    ALNS -.- ALNS_NOTE["ALNSearch.apply():\n1. Select Destroy operator (adaptive roulette):\n   • Worst removal (D1)\n   • Shaw removal (D2)\n   • Route removal (D3)\n   • Random removal (D4)\n   • Proximity removal (D5)\n2. Destroy: remove U[15%,40%] customers\n3. Select Repair operator (adaptive roulette):\n   • Regret-2 insertion (R1)\n   • Regret-3 insertion (R2)\n   • Greedy insertion (R3)\n   • A*-build with pref scoring (R4)\n4. Repair: re-insert removed customers\n5. 2-opt post-processing\n6. SA temperature: T ← T × 0.995\n7. Update operator scores (Ropke & Pisinger)"]

    CHECK_RHO -- "No" --> GBEST["Choose gBest from\nthe Pareto front (ψ₁) and\nproduce Yᵢ using Eq. (2)"]
    GBEST -.- GBEST_NOTE["gBest selection:\n• With preference: ASF-based\n  (select_gbest_asf)\n• Without: SDE binary tournament\n  (select_gbest)\n\nSSO Update (Enhanced Eq. 2):\n  keyⱼ = gbest_j         if ρⱼ ≤ c_g (0.95)\n  keyⱼ = xᵢ,ⱼ            if c_g < ρⱼ ≤ c_w (0.99)\n  keyⱼ += Lévy(1.5)×Δ   if c_w < ρⱼ ≤ c_l\n  keyⱼ += F(xr1−xr2)    otherwise (DE/rand/1)\n\nIf stagnation > 3:\n  Polynomial mutation (η_m = 20)"]

    ALNS --> EVAL
    GBEST --> EVAL

    EVAL["Evaluate fitness functions\nZ₁, Z₂, Z₃, Z₄, Z₅"]
    EVAL -.- EVAL_NOTE["Z₁ = Number of vehicles\nZ₂ = Total travel distance\nZ₃ = Total waiting time\nZ₄ = Load balance (max−min)\nZ₅ = Makespan\n+ penalty 10⁴ × unserved"]

    EVAL --> LS_CHECK{"rank_i == 0 ?\nrandom < ls_prob ?"}
    LS_CHECK -- "Yes (15%)" --> LS["Apply Local Search\n2-opt + smart merge\n→ Re-evaluate"]
    LS_CHECK -- "No" --> CHECK_I
    LS --> CHECK_I

    CHECK_I{"Is i < nSol ?"}
    CHECK_I -- "Yes" --> INC_I["i = i + 1"]
    INC_I --> CHECK_RHO

    CHECK_I -- "No" --> UPDATE_ARCHIVE["Update DualArchive\nwith offspring Y′"]
    UPDATE_ARCHIVE -.- ARCHIVE_NOTE["DualArchive:\n• A_conv: ε-dominance + ASF pruning\n• A_div: Pareto-dominance + SDE pruning\n\nInject solution from archive:\n  p_conv = σ(stagnation/5 − 2)\n  → stagnation cao → ưu tiên A_conv"]

    UPDATE_ARCHIVE --> COMBINE["Combine X^t and Y′ to\nupdate X^(t+1)"]

    COMBINE --> RANK2["Classify and rank the\npopulation into distinct\nfronts ψ₁, ψ₂, ..., ψₖ"]
    RANK2 -.- RANK2_NOTE["• Non-dominated Sorting\n• SDE density estimation\n• Reference Direction association"]

    RANK2 --> SELECT["Selection"]
    SELECT -.- SELECT_NOTE["Retain nSol best solutions in X^(t+1):\n1. Add fronts F₀, F₁, ... until full\n2. Boundary front: Ref Dir Niching\n   (ưu tiên niche ít thành viên)\n3. Tie-break bằng SDE density"]

    SELECT --> ADAPT["Adapt parameters"]
    ADAPT -.- ADAPT_NOTE["• If stagnation > 5:\n    nALNS ← min(0.5, base + 0.05×stag)\n• mutation_rate ← 0.05 + 0.10×progress\n• Track convergence: min ASF on ψ₁"]

    ADAPT --> CHECK_TIME{"Is tCur > tRun ?"}
    CHECK_TIME -- "No" --> T_INC["t = t + 1"]
    T_INC --> SET_I
    CHECK_TIME -- "Yes" --> FINAL["Final ranking: NDS + SDE\nExtract Pareto front\nfrom DualArchive"]
    FINAL --> STOP(["Stop"])
```

---

## So Sánh: Bài Báo Gốc vs. Code Thực Tế

| Thành phần | Bài báo gốc (Fig.1) | Code thực tế |
|---|---|---|
| **Khởi tạo X₁** | LKH | `best_initialization()`: CW + Insertion(×6) + NN → `full_local_search()` → `ruin_and_recreate()` |
| **Khởi tạo Xᵢ** | Random | Perturbation (noise 0.05–0.15) + Random fill |
| **Ranking** | NDS + Crowding Distance | NDS + **SDE** (Shift-based Density Estimation) |
| **ABS / ALNS** | ABS (Attraction-Based Search) | **ALNSearch** (ALNS): 5 Destroy + 4 Repair + Adaptive Scoring + SA |
| **SSO (Eq. 2)** | Standard SSO (3 bands) | Enhanced SSO: 4 bands (gBest copy + conservation + **Lévy flight** + **DE/rand/1**) |
| **gBest selection** | CD-based tournament | **ASF-based** (preference) hoặc SDE binary tournament |
| **Fitness** | Eq. (15), (16), (17) — 3 objectives | **5 objectives**: Z₁(vehicles), Z₂(distance), Z₃(wait), Z₄(balance), Z₅(makespan) |
| **Archive** | Không đề cập | **DualArchive**: A_conv (ε-dominance + ASF) + A_div (Pareto + SDE) |
| **Selection** | Rank + CD | Rank + SDE + **Reference Direction Niching** (Das-Dennis / Preference-biased) |
| **Mutation** | Không đề cập | **Polynomial mutation** (η_m=20) khi stagnation > 3 |
| **Adaptive** | Không đề cập | n_ALNS tăng khi stagnation; mutation_rate tăng theo progress |
| **Preference** | Không đề cập | **R-Dominance**, ASF, auto-calibrate g, ROI (δ) |
| **Local Search** | Không đề cập | 2-opt + smart merge (15% cho rank-0 offspring) |
