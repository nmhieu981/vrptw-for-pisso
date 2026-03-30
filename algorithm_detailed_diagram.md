# Sơ Đồ Chi Tiết Thuật Toán iNSSSO

> **Lệnh:** `python main.py --mode single --instance C101 --time 30`
>
> **Lưu ý:** Tên class trong code là `ABSearch` nhưng thực chất là alias của `ALNSearch` (ALNS — Adaptive Large Neighbourhood Search).

---

## 1. Luồng Tổng Thể (End-to-End)

```mermaid
flowchart TD
    START(["▶ START"]) --> A1["load_config()\nĐọc config/params.yaml"]
    A1 --> A2["VRPTWInstance.load(path)\nTải dữ liệu Solomon C101.csv"]
    A2 --> A3["UserPreference(g, w, δ)\nTải preference người dùng"]
    A3 --> A4["Khởi tạo iNSSSO\n(FitnessEvaluator, SolutionParser,\nALNSearch, DualArchive, RefDirs)"]

    A4 --> B["initialize_population()\nKhởi tạo n_sol cá thể"]
    B --> C["_auto_calibrate_preference()\ng = ideal + 0.1 × (p10 - ideal)"]
    C --> D["archive.update(population)\nNạp quần thể vào DualArchive"]

    D --> LOOP{"⏱ elapsed < t_run (30s) ?"}

    LOOP -- Có --> E["VÒNG LẶP CHÍNH\n(xem mục 3)"]
    E --> LOOP

    LOOP -- Không --> F["Xếp hạng cuối: NDS + SDE"]
    F --> G["archive.update(population)"]
    G --> H["pareto = archive.get_solutions()"]
    H --> I["Tính metrics:\nHV, Nnds, R-HV, Best ASF, ROI Count"]
    I --> J["Vẽ đồ thị:\npareto_plot, route_plot, convergence_plot"]
    J --> END(["■ END"])
```

---

## 2. Khởi Tạo Quần Thể — `initialize_population()`

```mermaid
flowchart TD
    subgraph "Phase 1: Tạo ứng viên (không có LS)"
        S1["Clarke-Wright Savings"]
        S2["Nearest Neighbour"]
        S3["Insertion Heuristic\n× 6 sort keys:\nready_time, distance, angle,\ndemand, due_date, tw_center"]
    end

    subgraph "Phase 2: Full Local Search trên top-2"
        LS["full_local_search()\n2-opt → or-opt → relocate\n→ swap → cross-exchange\n→ ruin-and-recreate"]
    end

    subgraph "Phase 3: Ruin & Recreate bổ sung"
        RR["ruin_and_recreate_iter()\n200 iterations trên best"]
    end

    S1 --> RANK["Sắp xếp theo distance\nChọn top-2"]
    S2 --> RANK
    S3 --> RANK
    RANK --> LS
    LS --> RR
    RR --> BEST["best_routes\n(kết quả best_initialization)"]

    BEST --> SEEDS["Tạo seeds từ\ncác chiến lược khác"]
    SEEDS --> PERTURB["Nhiễu hóa mỗi seed\n(noise_scale: 0.05, 0.10, 0.15)"]
    PERTURB --> FILL["Random fill\nnếu < n_sol"]
    FILL --> POP["Quần thể ban đầu\n(n_sol cá thể)"]

    POP --> EVAL["Mỗi cá thể:\ndecode() → parse() → evaluate()"]
```

---

## 3. Vòng Lặp Chính — 1 Generation

```mermaid
flowchart TD
    A["Tính obj_matrix\ntừ population"] --> B["assign_rank_and_sde()\nNDS → SDE density"]
    B --> C["Gán rank, sde cho mỗi cá thể"]
    C --> D["Convergence tracking\n(ASF nếu có preference)"]
    D --> E["_adapt_parameters()\nĐiều chỉnh n_abs, mutation_rate"]

    E --> F["Sinh n_sol offspring\n(xem mục 4)"]

    F --> G["archive.update(offspring)\nCập nhật DualArchive"]
    G --> H["archive.inject_solution()\nTiêm 1 lời giải từ archive"]
    H --> I["merged = population + offspring"]
    I --> J["select_best(merged, n_sol, ref_dirs)\nNDS + SDE + Ref Dir Niching"]
    J --> K["population = n_sol cá thể tốt nhất"]
    K --> L["generation += 1"]
```

---

## 4. Sinh Con (Offspring) — Mỗi Cá Thể i

```mermaid
flowchart TD
    A{"random() < n_abs ?"} 

    A -- "Có (ALNS path)" --> ALNS["ALNSearch.apply(xi)\n(xem mục 5)"]

    A -- "Không (SSO path)" --> GB{"Có preference ?"}
    GB -- Có --> ASF["select_gbest_asf()\nChọn gBest theo ASF\ntừ Pareto Front"]
    GB -- Không --> SDE["select_gbest()\nBinary tournament\ntheo SDE density"]

    ASF --> SSO
    SDE --> SSO

    SSO["update_solution(xi, gbest, xr1, xr2)"]

    SSO --> MUT{"stagnation > 3\n& random < mutation_rate ?"}
    MUT -- Có --> PM["polynomial_mutation()\neta_m = 20"]
    MUT -- Không --> SKIP[" "]
    PM --> SKIP

    ALNS --> DEC
    SKIP --> DEC

    DEC["yi.decode() → parse() → evaluate()"]

    DEC --> LS{"rank_i == 0 &\nrandom < ls_prob ?"}
    LS -- "Có (15% cho rank 0)" --> LOCAL["apply_local_search()\n2-opt + smart merge"]
    LS -- "Không" --> OUT["offspring.append(yi)"]
    LOCAL --> EVAL2["evaluate(yi) lại"]
    EVAL2 --> OUT
```

---

## 5. ALNSearch (ALNS) — `apply()` Chi Tiết

> Class: `ALNSearch` (alias `ABSearch`)
> File: `algorithm/abs_search.py`

```mermaid
flowchart TD
    INPUT["Solution đầu vào"] --> DECODE["clone() → decode() → parse()"]
    DECODE --> NR["Tính n_remove\n= U[15%, 40%] × total customers"]

    NR --> DS["Chọn Destroy Operator\n(Roulette-wheel adaptive)"]

    DS --> D1{"Operator nào ?"}
    D1 -- "D1" --> WR["Worst Removal\nXóa customer có savings lớn nhất"]
    D1 -- "D2" --> SR["Shaw Removal\nXóa nhóm related\nR = αd + β|TW| + γ|q|"]
    D1 -- "D3" --> RR["Route Removal\nXóa nguyên route ngắn\nP(k) ∝ exp(-10 nk/max)"]
    D1 -- "D4" --> RAND["Random Removal\nUniform random"]
    D1 -- "D5" --> PR["Proximity Removal\nXóa cluster gần nhau"]

    WR --> DEST_OUT
    SR --> DEST_OUT
    RR --> DEST_OUT
    RAND --> DEST_OUT
    PR --> DEST_OUT

    DEST_OUT["kept_routes + unassigned"] --> RS["Chọn Repair Operator\n(Roulette-wheel adaptive)"]

    RS --> R1{"Operator nào ?"}
    R1 -- "R1" --> REG2["Regret-2 Insertion\nregret = cost₂ - cost₁"]
    R1 -- "R2" --> REG3["Regret-3 Insertion\nregret = Σ(costⱼ - cost₁)"]
    R1 -- "R3" --> GI["Greedy Insertion\nCheapest position"]
    R1 -- "R4" --> AB["A*-Build\nPreference-guided scoring"]

    REG2 --> REPAIR_OUT
    REG3 --> REPAIR_OUT
    GI --> REPAIR_OUT
    AB --> REPAIR_OUT

    REPAIR_OUT["Rebuilt routes"] --> TOPT["2-opt trên mỗi route"]
    TOPT --> ENCODE["Solution.from_routes()\nRe-encode thành random keys"]

    ENCODE --> SA_TEMP["SA: T = T × c_T\n(c_T = 0.995)"]
    SA_TEMP --> SEG{"iteration % 25 == 0 ?"}
    SEG -- Có --> UPDATE["end_segment()\nCập nhật weights:\nπ_k = (1-r)π_k + r × avg_score"]
    SEG -- Không --> DONE
    UPDATE --> DONE
    DONE["Trả về Solution mới"]
```

### Bảng Operator Scoring (Ropke & Pisinger 2006)

| Reward Level | Điều kiện | Điểm (σ) |
|:---:|---|:---:|
| 0 | New global best | 33 |
| 1 | Improving, not dominated | 9 |
| 2 | Accepted by SA | 3 |
| 3 | Rejected | 0 |

---

## 6. SSO Update — `update_solution()` Chi Tiết

```mermaid
flowchart TD
    A["Sinh ρⱼ ~ U(0,1)\ncho mỗi biến j"] --> B{"ρⱼ ≤ c_g (0.95) ?"}

    B -- Có --> COPY["keyⱼ = gbest_j\n(Exploitation: copy từ gBest)"]

    B -- Không --> C{"ρⱼ ≤ c_w (0.99) ?"}

    C -- Có --> KEEP["keyⱼ = xᵢ,ⱼ\n(Conservation: giữ nguyên)"]

    C -- Không --> D{"ρⱼ ≤ c_l ?"}

    D -- Có --> LEVY["keyⱼ = xᵢ,ⱼ + Lévy(1.5) × (gbest_j - xᵢ,ⱼ) × 0.01\n(Lévy flight exploration)"]

    D -- Không --> DE["keyⱼ = xᵢ,ⱼ + 0.5 × (xr1,ⱼ - xr2,ⱼ)\n(DE/rand/1 mutation)"]

    COPY --> CLIP["clip(0, 0.999)"]
    KEEP --> CLIP
    LEVY --> CLIP
    DE --> CLIP
    CLIP --> OUT["Solution mới"]

    style COPY fill:#2d5a27,color:#fff
    style LEVY fill:#8b4513,color:#fff
    style DE fill:#4a148c,color:#fff
```

> **c_l = c_w + 0.6 × (1 - c_w)** → với c_w = 0.99 thì c_l = 0.996

---

## 7. DualArchive — Cơ Chế Lưu Trữ Kép

```mermaid
flowchart TD
    subgraph "A_conv — Convergence Archive"
        C1["ε-dominance insertion\nbox(f) = ⌊f_m / ε⌋"]
        C2["Trong cùng box:\ngiữ solution có ASF thấp hơn"]
        C3["Pruning: giữ max_size\ntheo ASF ascending"]
    end

    subgraph "A_div — Diversity Archive"
        D1["Pareto-dominance insertion\n(không dùng ε-box)"]
        D2["Pruning: loại bỏ\ncá thể crowded nhất (SDE thấp)"]
    end

    INPUT["Candidate solutions"] --> C1
    INPUT --> D1
    C1 --> C2 --> C3
    D1 --> D2

    subgraph "Injection vào Population"
        INJ["p_conv = σ(stag/5 - 2)\nSigmoid: stagnation cao → ưu tiên A_conv"]
        INJ1["random < p_conv → lấy từ A_conv"]
        INJ2["random ≥ p_conv → lấy từ A_div"]
    end

    C3 --> INJ
    D2 --> INJ
    INJ --> INJ1
    INJ --> INJ2
```

---

## 8. Selection — `select_best()` Chi Tiết

```mermaid
flowchart TD
    A["merged = population + offspring\n(2 × n_sol cá thể)"] --> B["fast_nondominated_sort()\n→ fronts F₀, F₁, F₂, ..."]
    B --> C["assign_rank_and_sde()\nTính SDE cho tất cả"]
    C --> D["Loại duplicate\n(eps = 10⁻⁶)"]

    D --> E["Thêm lần lượt F₀, F₁, ...\nvào selected"]
    E --> F{"selected + |Fₖ| ≤ n_sol ?"}
    F -- Có --> G["selected += Fₖ\nTiếp tục front kế"]
    G --> F

    F -- "Không (Fₖ là boundary front)" --> H{"Có ref_dirs ?"}
    H -- Có --> I["normalize_objectives()\nassociate_to_directions()\nniching_selection()"]
    H -- Không --> J["Sort theo SDE giảm dần\nLấy đủ n_sol"]

    I --> K["Ưu tiên niche ít thành viên\nTie-break bằng SDE"]
    K --> L["population mới\n(n_sol cá thể)"]
    J --> L
```

---

## 9. 5 Hàm Mục Tiêu — `FitnessEvaluator`

```mermaid
flowchart LR
    SOL["Solution\n(decoded routes)"] --> Z1["Z1: Số xe\n= len(routes)"]
    SOL --> Z2["Z2: Tổng khoảng cách\n= Σ dist(routeₖ)"]
    SOL --> Z3["Z3: Tổng thời gian chờ\n= Σ waitₖ"]
    SOL --> Z4["Z4: Cân bằng tải\n= max(load) - min(load)"]
    SOL --> Z5["Z5: Makespan\n= max(completion_timeₖ)"]

    Z1 --> OBJ["objectives = (Z1, Z2, Z3, Z4, Z5)\n+ penalty × n_unserved"]
    Z2 --> OBJ
    Z3 --> OBJ
    Z4 --> OBJ
    Z5 --> OBJ
```

> Tất cả 5 mục tiêu đều **minimize**. Penalty = 10⁴ cho mỗi khách hàng không phục vụ được.

---

## 10. Kiến Trúc Module Đầy Đủ

```mermaid
flowchart TD
    subgraph "main.py"
        CLI["argparse CLI"]
        MODE["mode_single()"]
    end

    subgraph "core/"
        INST["VRPTWInstance\n(.load, customers, depot,\ndistance_matrix)"]
        SOL["Solution\n(.keys, .routes, .decode(),\n.from_routes(), .clone())"]
        PARSE["SolutionParser\n(.parse, .route_details)"]
        FIT["FitnessEvaluator\n(.evaluate → Z1..Z5)\n+ ObjectiveNormalizer"]
        PREF["UserPreference\n(g, w, δ, .asf(), .asf_batch())"]
    end

    subgraph "algorithm/"
        ALGO["iNSSSO\n(.run, .update_solution,\n.initialize_population)"]
        ALNS["ALNSearch\n(5 Destroy + 4 Repair\n+ OperatorScoring + SA)"]
        NDS["fast_nondominated_sort()"]
        CROWD["assign_rank_and_sde()\nsde_density()\nselect_best() + niching"]
        RDOM["r_assign_rank_and_crowding()\nselect_gbest_asf()"]
        RDIR["das_dennis()\npreference_biased_dirs()\nniching_selection()"]
        INIT["best_initialization()\nclarke_wright_savings()\ninsertion_heuristic()\nfull_local_search()"]
    end

    subgraph "benchmark/"
        METRICS["PerformanceMetrics\n(HV, Nnds, R-HV, ROI)"]
    end

    subgraph "visualization/"
        VP["plot_pareto_2d()"]
        VR["plot_routes()"]
        VC["plot_convergence()"]
    end

    CLI --> MODE
    MODE --> INST
    MODE --> PREF
    MODE --> ALGO
    ALGO --> SOL
    ALGO --> PARSE
    ALGO --> FIT
    ALGO --> ALNS
    ALGO --> NDS
    ALGO --> CROWD
    ALGO --> RDOM
    ALGO --> RDIR
    ALGO --> INIT
    MODE --> METRICS
    MODE --> VP
    MODE --> VR
    MODE --> VC
```

---

## 11. Tham Số Thích Ứng — `_adapt_parameters()`

```mermaid
flowchart TD
    A["Kiểm tra stagnation:\nbest_ASF có cải thiện ?"] --> B{"|ΔASF| < 10⁻⁶ ?"}
    B -- Có --> C["stagnation_count += 1"]
    B -- Không --> D["stagnation_count = 0\nCập nhật last_best_asf"]

    C --> E{"stagnation > 5 ?"}
    E -- Có --> F["n_abs = min(0.5,\nn_abs_base + 0.05 × stag)\n→ Tăng tỷ lệ dùng ALNS"]
    E -- Không --> G["n_abs = n_abs_base (0.2)"]

    D --> H["mutation_rate =\n0.05 + 0.10 × progress\n(tăng dần theo thời gian)"]
    F --> H
    G --> H
```

> **Ý nghĩa:** Khi thuật toán bế tắc (stagnation), tự động tăng tỷ lệ sử dụng ALNS destroy/repair để thoát khỏi cực tiểu cục bộ.
