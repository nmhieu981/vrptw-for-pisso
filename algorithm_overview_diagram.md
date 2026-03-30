# Sơ Đồ Tổng Quát Thuật Toán iNSSSO

> **Lệnh chạy:** `python main.py --mode single --instance C101 --time 30`

## 1. Sơ Đồ Luồng Chính (High-Level Flowchart)

```mermaid
flowchart TD
    START(["▶ START"]) --> A["1. Đọc cấu hình & tham số"]
    A --> B["2. Tải bài toán VRPTW (Instance)"]
    B --> C["3. Tải preference người dùng (g, w, δ)"]
    C --> D["4. Khởi tạo thuật toán iNSSSO"]
    D --> E["5. Khởi tạo quần thể (Population Init)"]
    E --> F["6. Auto-calibrate điểm tham chiếu g"]
    F --> G["7. Cập nhật Dual Archive ban đầu"]

    G --> LOOP{"⏱ elapsed < t_run ?"}

    LOOP -- Có --> H["8. Xếp hạng: NDS + SDE"]
    H --> I["9. Theo dõi hội tụ (ASF / PF)"]
    I --> J["10. Điều chỉnh tham số thích ứng"]
    J --> K["11. Sinh con (Offspring Generation)"]
    K --> L["12. Cập nhật Dual Archive"]
    L --> M["13. Tiêm lời giải từ Archive"]
    M --> N["14. Chọn lọc thế hệ mới (Selection)"]
    N --> LOOP

    LOOP -- Không --> O["15. Xếp hạng cuối cùng (Final Ranking)"]
    O --> P["16. Trích xuất Pareto Front"]
    P --> Q["17. Tính metrics & xuất kết quả"]
    Q --> R["18. Vẽ đồ thị (Pareto, Routes, Convergence)"]
    R --> END(["■ END"])
```

---

## 2. Chi Tiết Các Khối Chính

### 🔹 Giai đoạn Chuẩn Bị (Bước 1–4)

| Bước | Mô tả | Module |
|------|--------|--------|
| 1 | Đọc `config/params.yaml` → tham số thuật toán | `main.py` → `load_config()` |
| 2 | Tải instance Solomon (CSV) → tọa độ, demand, time window | `VRPTWInstance.load()` |
| 3 | Tải preference: điểm tham chiếu **g**, trọng số **w**, ngưỡng **δ** | `UserPreference` |
| 4 | Khởi tạo: `FitnessEvaluator`, `SolutionParser`, `ABSearch`, `DualArchive`, Reference Directions | `iNSSSO.__init__()` |

### 🔹 Giai đoạn Khởi Tạo Quần Thể (Bước 5–7)

```mermaid
flowchart LR
    A["best_initialization()"] --> B["Insertion Heuristic\n(6 sort keys)"]
    B --> C["Clarke-Wright\nSavings"]
    C --> D["Nearest Neighbour"]
    D --> E["2-opt + Merge\ncho mỗi seed"]
    E --> F["Nhiễu hóa\n(perturbation)"]
    F --> G["Random fill\n(nếu thiếu)"]
    G --> H["Quần thể\nn_sol cá thể"]
```

### 🔹 Vòng Lặp Chính — Sinh Con (Bước 11)

```mermaid
flowchart TD
    A{"random < n_abs ?"} -- Có --> B["ABS Search\n(Attraction-Based)"]
    A -- Không --> C["Chọn gBest\n(ASF hoặc SDE)"]
    C --> D["SSO Update\n(gBest copy + Lévy + DE)"]
    D --> E{"Stagnation > 3 ?"}
    E -- Có --> F["Polynomial Mutation"]
    E -- Không --> G["Giữ nguyên"]
    F --> G
    B --> G
    G --> H["Decode → Parse → Evaluate"]
    H --> I{"Rank 0 & random < ls_prob ?"}
    I -- Có --> J["Local Search\n(2-opt + Merge)"]
    I -- Không --> K["offspring"]
    J --> K
```

### 🔹 Chọn Lọc & Archive (Bước 12–14)

```mermaid
flowchart LR
    A["Offspring"] --> B["Cập nhật\nDual Archive"]
    B --> C["Inject solution\ntừ Archive"]
    C --> D["Merged =\nPopulation + Offspring"]
    D --> E["NDS + SDE +\nRef Dir Niching"]
    E --> F["Chọn n_sol\ncá thể tốt nhất"]
```

---

## 3. Dual Archive — Cơ Chế Lưu Trữ

```mermaid
flowchart TD
    subgraph DualArchive
        CA["A_conv\n(Convergence Archive)\nε-dominance + ASF pruning"]
        DA["A_div\n(Diversity Archive)\nPareto-dominance + SDE pruning"]
    end

    INPUT["Candidate solutions"] --> CA
    INPUT --> DA
    CA -- "σ(stagnation) → p_conv" --> INJECT["Inject vào Population"]
    DA -- "1 - p_conv" --> INJECT
```

---

## 4. Tổng Quan Kiến Trúc Module

```mermaid
flowchart TD
    subgraph "main.py"
        M1["CLI Parser"]
        M2["mode_single()"]
    end

    subgraph "core/"
        C1["VRPTWInstance"]
        C2["Solution"]
        C3["SolutionParser"]
        C4["FitnessEvaluator"]
        C5["UserPreference"]
    end

    subgraph "algorithm/"
        A1["iNSSSO"]
        A2["ABSearch"]
        A3["init_heuristics"]
        A4["nondominated"]
        A5["crowding / SDE"]
        A6["r_dominance"]
        A7["reference_dirs"]
    end

    subgraph "output"
        O1["PerformanceMetrics"]
        O2["Pareto Plot"]
        O3["Route Plot"]
        O4["Convergence Plot"]
    end

    M1 --> M2
    M2 --> C1
    M2 --> C5
    M2 --> A1
    A1 --> C2
    A1 --> C3
    A1 --> C4
    A1 --> A2
    A1 --> A3
    A1 --> A4
    A1 --> A5
    A1 --> A6
    A1 --> A7
    M2 --> O1
    M2 --> O2
    M2 --> O3
    M2 --> O4
```

---

> [!NOTE]
> Đây là sơ đồ **tổng quát nhất** của thuật toán iNSSSO. Mỗi khối có thể được mở rộng chi tiết thêm (VD: bên trong ABS Search, chi tiết SSO Update, cách tính ASF, cơ chế ε-dominance, v.v.)
