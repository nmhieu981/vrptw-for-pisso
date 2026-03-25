# Sắp xếp không trội nhanh (NDS) và ưu thế Pareto
_Exported on 3/26/2026 at 03:03:39 GMT+7 from Cursor (2.6.21)_

---

**User**

@paper_q1_full.md:1-2305 giải thích phần này cho tôi, và công thức đã đúng format chưa 

---

**Cursor**

Tôi sẽ giải thích phần Section 5.1 và kiểm tra format công thức cho bạn.

## Giải thích Section 5.1 — Fast Non-dominated Sorting (NDS)

### Ý tưởng chính

Đây là phần mô tả cách **xếp hạng các lời giải** trong quần thể dựa trên khái niệm Pareto dominance — nền tảng của mọi thuật toán tối ưu đa mục tiêu.

### Từng công thức

**Eq. 20 — Pareto Dominance:** Lời giải **x** thống trị (dominate) lời giải **y** khi và chỉ khi:
- Tất cả mục tiêu của x đều **không tệ hơn** y (tức \(f_m(x) \leq f_m(y)\) với mọi m)
- Và tồn tại **ít nhất một** mục tiêu mà x **tốt hơn nghiêm ngặt** y (tức \(f_m(x) < f_m(y)\))

Ví dụ: nếu x = (3, 5, 2) và y = (4, 5, 3) thì x dominate y vì mọi giá trị của x đều nhỏ hơn hoặc bằng y, và ở mục tiêu 1 và 3 thì x tốt hơn hẳn.

**Eq. 21 — all\_leq:** Ma trận boolean kiểm tra "x\_i có nhỏ hơn hoặc bằng x\_j trên **tất cả** M mục tiêu không?" — dùng phép AND (\(\bigwedge\)) trên tất cả objectives.

**Eq. 22 — any\_lt:** Ma trận boolean kiểm tra "x\_i có nhỏ hơn nghiêm ngặt x\_j trên **ít nhất một** mục tiêu không?" — dùng phép OR (\(\bigvee\)).

**Eq. 23 — dominates:** Kết hợp: x\_i dominate x\_j khi cả hai điều kiện trên đều đúng. Đây chính là triển khai vectorised của Eq. 20.

Cách triển khai này dùng NumPy broadcasting để tính **toàn bộ ma trận dominance N×N** cùng lúc thay vì dùng vòng lặp, cho tốc độ nhanh hơn rất nhiều. Độ phức tạp là \(O(M \cdot N^2)\).

---

## Kiểm tra Format Công thức

Nhìn vào source markdown và hình render, tôi thấy một **vấn đề format** ở các biến dùng underscore trong `\text{}`:

```488:504:g:\vrptw-for-pisso\paper_q1_full.md
### 5.1 Fast Non-dominated Sorting (NDS)

**Pareto dominance:**

$$\mathbf{x} \prec \mathbf{y} \iff \forall m: f_m(\mathbf{x}) \leq f_m(\mathbf{y}) \;\land\; \exists m: f_m(\mathbf{x}) < f_m(\mathbf{y}) \tag{20}$$

**Vectorised implementation** sử dụng NumPy broadcasting:

$$\text{dom\_matrix}[i,j] = \text{True} \iff \mathbf{x}_i \prec \mathbf{x}_j$$

$$\text{all\_leq} = \bigwedge_{m=1}^{M} (f_m(\mathbf{x}_i) \leq f_m(\mathbf{x}_j)) \tag{21}$$

$$\text{any\_lt} = \bigvee_{m=1}^{M} (f_m(\mathbf{x}_i) < f_m(\mathbf{x}_j)) \tag{22}$$

$$\text{dominates} = \text{all\_leq} \;\land\; \text{any\_lt} \tag{23}$$

**Complexity:** $O(M \cdot N^2)$ cho pairwise dominance check.
```

Trong hình render, bạn có thể thấy dấu `\` hiện ra trước underscore: **dom\_matrix**, **all\_leq**, **any\_lt**. Đây là lỗi hiển thị vì trong `\text{}` của một số renderer (MathJax/KaTeX trong markdown preview), `\_` không luôn render đúng.

### Cách sửa

Có 2 cách:

**Cách 1** — Dùng `\texttt{}` (monospace, phù hợp cho tên biến code):

```latex
$$\texttt{dom\_matrix}[i,j] = \text{True} \iff \mathbf{x}_i \prec \mathbf{x}_j$$
```

**Cách 2** — Dùng `\mathrm{}` với `\_` hoặc chuyển sang dạng không underscore:

```latex
$$\mathrm{dom{\_}matrix}[i,j] = \text{True} \iff \mathbf{x}_i \prec \mathbf{x}_j$$
```

**Cách 3 (đề xuất)** — Dùng subscript thay underscore cho đẹp hơn kiểu toán học:

```latex
$$D[i,j] = \text{True} \iff \mathbf{x}_i \prec \mathbf{x}_j$$
$$A_{\leq} = \bigwedge_{m=1}^{M} (f_m(\mathbf{x}_i) \leq f_m(\mathbf{x}_j))$$
$$A_{<} = \bigvee_{m=1}^{M} (f_m(\mathbf{x}_i) < f_m(\mathbf{x}_j))$$
$$\text{dominates} = A_{\leq} \;\land\; A_{<}$$
```

Bạn muốn tôi sửa theo cách nào? Hay bạn muốn tôi kiểm tra toàn bộ file để tìm tất cả các chỗ có vấn đề format tương tự?

---

**User**

@paper_q1_full.md:1043-1141 trong phần này cmt thêm mục nào lý thuyết ở trên để đối chiếu được không 

---

**Cursor**

Tôi sẽ thêm các comment cross-reference đến lý thuyết tương ứng trong pseudocode để người đọc dễ đối chiếu.

Đã thêm cross-reference chi tiết vào toàn bộ Algorithm 1. Đây là tóm tắt những gì đã bổ sung:

### Phase 1 — Initialization
- **Line 1**: Thêm ref đến 3 heuristic H1/H2/H3 và equations tương ứng (Eq.18, 19)
- **Line 2**: Ref đến 5 mục tiêu (Section 3.2) + penalty (Section 3.4)
- **Line 5-6**: Ref chi tiết dual archive gồm A_conv (epsilon-dom) và A_div (SDE prune)
- **Line 7**: Ghi chú tỷ lệ 70% ROI / 30% uniform cho reference directions

### Phase 2 — Main Loop
- **Step A**: Tách rõ 3 component: NDS (Section 5.1), SDE (Section 5.2), Niching (Section 5.3)
- **Step B**: Ref đến ASF augmented (Section 6.1) + stagnation detection (Section 10.2)
- **Step D — ALNS path**: Ref chi tiết từng bước: Destroy D1-D5, Repair R1-R4, SA acceptance, score update, kèm equation numbers
- **Step D — SSO path**: Ref đến R-dominance cho gBest selection, 4 branches (exploit/conserve/Levy/DE) với equation numbers
- **Step D — Local search**: Ref đến Section 4.3 với danh sách operators, ghi chú tỷ lệ 10% elite vs 3% non-elite
- **Step E**: Tách rõ A_conv (epsilon-box + ASF) vs A_div (Pareto + SDE)
- **Step F**: Thêm ví dụ giá trị sigmoid (s=0 -> p=0.12, s=20 -> p=0.88)
- **Step G**: Tách 3 phase của Algorithm 6 (NDS fronts, fill, niching+SDE)

### Phase 3 — Finalization
- Thêm ref sections cho final ranking và archive update

Giờ mỗi dòng trong pseudocode đều có thể truy ngược về section lý thuyết + equation number cụ thể, giúp reviewer và người đọc đối chiếu dễ dàng.

---

**User**

tóm lại điều gì làm nổi bật thuật toán của tôi để apply Q1

---

**Cursor**

Dựa trên toàn bộ tài liệu, đây là bức tranh tổng thể về những gì làm thuật toán của bạn nổi bật:

---

## Điểm cốt lõi: "Chưa ai làm" + "Kết hợp thông minh"

### 1. Khoảng trống chưa ai chạm — MaO-VRPTW 5 mục tiêu + Preference

Hiện tại trong literature:
- MO-VRPTW chỉ xét 2-3 mục tiêu (Wang 2025, Abdelmaguid 2024)
- Many-objective VRP có Chen 2025 (6 mục tiêu) nhưng **không có time windows, không có preference**
- Preference-based MaO có (Liu 2025, Pre-DEMO 2023) nhưng **chỉ trên benchmark functions, chưa ai áp dụng cho routing**

**Bạn là người đầu tiên** kết hợp cả 3: many-objective (M=5) + VRPTW + preference-based framework. Đây là novelty claim mạnh nhất.

### 2. SSO lần đầu áp dụng cho VRP

SSO (2019) đã có nhiều cải tiến (RSSA, FSSSA, dimensional learning) nhưng **chưa bao giờ được dùng cho bất kỳ variant VRP nào**. Bạn không chỉ áp dụng mà còn cải tiến nó bằng 2 cơ chế bổ sung:

| Thành phần | Vai trò | Tại sao cần cả hai |
|---|---|---|
| **Levy flight** | Nhảy xa, vô hướng, heavy-tailed | Thoát local optima trong landscape gồ ghề |
| **DE/rand/1** | Nhảy có hướng, dựa trên population | Khai thác thông tin từ quần thể |

Levy (undirected superdiffusion) + DE (directed mutation) = **exploration toàn diện** mà SSO gốc (chỉ random U(0,1)) không có.

### 3. ALNS tích hợp vào framework MaO — Chưa từng có

ALNS rất phổ biến cho VRP đơn mục tiêu (211 bài báo theo Turkes 2025), nhưng **chưa ai tích hợp ALNS vào một framework many-objective evolutionary**. Đây là cầu nối giữa:
- **Domain knowledge** (destroy/repair operators hiểu cấu trúc VRPTW)
- **MaO search** (NDS + SDE + reference directions)

Adaptive switching giữa SSO path và ALNS path (Eq. 62) cho phép thuật toán **tự chuyển đổi** giữa global search (SSO) và local search (ALNS) tùy tình trạng stagnation.

### 4. Dual Archive giải quyết Convergence-Diversity Dilemma

Ishibuchi (2017) đã chứng minh: khi M >= 4, một archive duy nhất **không thể** đồng thời tối ưu convergence và diversity. Giải pháp:

| Archive | Mục tiêu | Cơ chế |
|---|---|---|
| A_conv | Hội tụ về ROI | epsilon-dominance + ASF |
| A_div | Phủ rộng Pareto front | Pareto + SDE pruning |
| Sigmoid injection | Cân bằng thích ứng | Stagnation cao -> inject convergence |

Ma et al. (2025), Fischer et al. (2025) dùng dual archive nhưng **chỉ trên benchmark functions**. Bạn là người đầu tiên áp dụng cho VRPTW.

### 5. R-Dominance khôi phục selection pressure

Với M=5, ~80-90% solutions đều non-dominated (Eq. 84) -> Pareto dominance gần như vô dụng. R-Dominance thêm 3 điều kiện (Pareto + ROI membership + ASF comparison) -> **giảm non-dominated xuống ~10-20%** -> selection có ý nghĩa trở lại. Kết hợp với SDE (thay CD vốn mất hiệu lực khi M >= 4), framework many-objective hoạt động thực sự.

---

## Tóm lại bằng 1 câu cho reviewer

> **"First preference-based many-objective framework for VRPTW that hybridizes an enhanced SSO (Levy + DE) with ALNS local search, managed by a dual-archive system — each component addresses a specific, identified gap in current literature."**

## Tại sao đủ cho Q1?

| Tiêu chí Q1 | Đáp ứng |
|---|---|
| **Novelty** | 6 contributions, mỗi cái fill 1 gap cụ thể (G1-G6) |
| **Lý thuyết** | 87 equations, superdiffusion proof, convergence sketch |
| **Thực nghiệm** | 7 thuật toán so sánh, 56 instances, 3 scales, 7 metrics |
| **Ablation** | 9 variants chứng minh từng component đóng góp |
| **Thống kê** | Wilcoxon + Friedman + Bonferroni + effect size |
| **Literature** | 70 refs, 35 từ 2024-2026 (50% rất mới) |
| **Tái tạo** | Pseudocode chi tiết cho tất cả 6 algorithms |

Điểm mạnh nhất của bài: **không phải 1 novelty đơn lẻ mà là sự kết hợp có hệ thống** — mỗi component giải quyết 1 vấn đề cụ thể, và chúng **tương tác synergy** (SSO explore + ALNS exploit, A_conv converge + A_div diversify, Levy undirected + DE directed).

---

**User**

 Khoảng trống chưa ai chạm — MaO-VRPTW 5 mục tiêu + Preference
Hiện tại trong literature:

MO-VRPTW chỉ xét 2-3 mục tiêu (Wang 2025, Abdelmaguid 2024)
Many-objective VRP có Chen 2025 (6 mục tiêu) nhưng không có time windows, không có preference
Preference-based MaO có (Liu 2025, Pre-DEMO 2023) nhưng chỉ trên benchmark functions, chưa ai áp dụng cho routing
Bạn là người đầu tiên kết hợp cả 3: many-objective (M=5) + VRPTW + preference-based framework. Đây là novelty claim mạnh nhất.
đưa cụ thể tên bài báo cho tôi để tìm kiếm

---

**Cursor**

Dựa trên danh mục tham khảo trong tài liệu của bạn, đây là tên đầy đủ từng bài:

---

### MO-VRPTW chỉ 2-3 mục tiêu

**[3] Wang et al., 2025:**
> "Multiobjective vehicle routing optimization with time windows: A hybrid approach using deep reinforcement learning and NSGA-II"
> *IEEE Transactions on Intelligent Transportation Systems*, vol. 26, pp. 4032–4045, 2025.

**[12] Abdelmaguid, 2024:**
> "An improved multiobjective evolutionary algorithm for time-dependent vehicle routing problem with time windows"
> *Alexandria Engineering Journal*, vol. 92, pp. 1–15, 2024.

**[35] Feng et al., 2023:**
> "Solving multi-objective vehicle routing problems with time windows: A decomposition-based multiform optimization approach"
> *Tsinghua Science and Technology*, vol. 28, no. 5, pp. 1–14, 2023.

---

### Many-objective VRP nhưng KHÔNG có time windows + KHÔNG preference

**[4] Chen et al., 2025:**
> "A local search with chain search path strategy for real-world many-objective vehicle routing problem"
> *Complex & Intelligent Systems*, vol. 11, art. 1825, 2025.

**[36] Liu et al., 2025:**
> "Research on multi-objective green vehicle routing problem with time windows based on the improved non-dominated sorting genetic algorithm III"
> *Symmetry*, vol. 17, no. 5, p. 734, 2025.
> (Có time windows nhưng chỉ 3 mục tiêu, chưa phải many-objective)

**[37] Ding et al., 2025:**
> "Practice of an improved many-objective route optimization algorithm in a multimodal transportation case under uncertain demand"
> *Complex & Intelligent Systems*, vol. 10, pp. 1–18, 2025.
> (Many-objective nhưng multimodal transportation, không phải VRPTW thuần)

---

### Preference-based MaO nhưng CHỈ trên benchmark functions

**[10] Liu et al., 2025:**
> "Preference-based expensive multi-objective optimization without using an ideal point"
> *Complex & Intelligent Systems*, vol. 11, art. 1905, 2025.

**[11] Li, Cheng & Deb, 2023:**
> "Pre-DEMO: Preference-inspired differential evolution for multi/many-objective optimization"
> *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 53, no. 10, pp. 6268–6280, 2023.

**[31] Yadav, Ramu & Deb, 2024:**
> "Updated preference-based hypervolume metric for evaluating preference-based evolutionary multi-objective optimization"
> *Technical Report*, Michigan State University, 2024.

**[54] Tanabe & Ishibuchi, 2025:**
> "Multi-start via scalarization with target-point-based Tchebycheff distance"
> *Proc. GECCO 2025*, 2025.

---

### Bảng tóm tắt khoảng trống

| Bài báo | Many-obj (M>=4) | Time Windows | Preference | Khoảng trống |
|---|---|---|---|---|
| Wang [3] 2025 | M=2 | Co | Khong | Thiếu MaO + preference |
| Abdelmaguid [12] 2024 | M=2 | Co | Khong | Thiếu MaO + preference |
| Chen [4] 2025 | **M=6** | **Khong** | **Khong** | Thiếu TW + preference |
| Liu [36] 2025 | M=3 | Co | Khong | Chưa MaO |
| Liu [10] 2025 | M>=4 | Khong | **Co** | Chỉ benchmark, không routing |
| Pre-DEMO [11] 2023 | M>=4 | Khong | **Co** | Chỉ benchmark, không routing |
| **iNSSSO (bạn)** | **M=5** | **Co** | **Co** | **Fill tất cả gaps** |

Bạn có thể search trực tiếp tên bài trên Google Scholar hoặc DOI để tìm full text.

---

**User**

Adaptive switching giữa SSO path và ALNS path (Eq. 62) cho phép thuật toán tự chuyển đổi giữa global search (SSO) và local search (ALNS) tùy tình trạng stagnation SSO nâng cao chứ nhỉ

---

**Cursor**

Đúng rồi, SSO ở đây là **SSO nâng cao (Enhanced SSO)**, không phải SSO gốc. Cụ thể:

---

### SSO gốc (Jain 2019) — 3 nhánh

```
x_new = gbest          nếu ρ ≤ c_g     → exploitation
x_new = x_i            nếu c_g < ρ ≤ c_w → conservation  
x_new = U(0,1)         nếu ρ > c_w     → random (VÔ HƯỚNG, KÉM)
```

Nhánh thứ 3 chỉ là **random đều U(0,1)** — không có hướng, không dùng thông tin từ quần thể, không có khả năng nhảy xa có chiến lược.

---

### Enhanced SSO (đề xuất) — 4 nhánh

```
x_new = gbest                              nếu ρ ≤ c_g     → exploitation
x_new = x_i                                nếu c_g < ρ ≤ c_w → conservation
x_new = x_i + L × (gbest - x_i) × 0.01    nếu c_w < ρ ≤ c_l → Lévy flight
x_new = x_i + F × (x_r1 - x_r2)           nếu ρ > c_l     → DE/rand/1
```

Nhánh random U(0,1) bị **thay thế hoàn toàn** bằng 2 cơ chế:

| | SSO gốc | Lévy flight (thay thế) | DE/rand/1 (thay thế) |
|---|---|---|---|
| **Hướng** | Vô hướng | Vô hướng nhưng hướng về gbest | **Có hướng** (dựa trên x_r1 - x_r2) |
| **Bước nhảy** | Cố định [0,1] | Heavy-tailed (superdiffusion) | Scale theo diversity quần thể |
| **Thông tin dùng** | Không | gbest | 2 donors (r1, r2) |
| **Thoát local optima** | Kém | **Mạnh** (occasional long jumps) | **Trung bình** (directed escape) |

---

### Luồng tổng thể khi chạy

```
Mỗi cá thể i trong quần thể:
│
├── U(0,1) < n_abs?  ──Yes──→  ALNS path (§8)
│                                 Domain-specific local search
│                                 Destroy + Repair + 2-opt
│                                 Hiểu cấu trúc VRPTW
│
└── No ──→  Enhanced SSO path (§7)
              ├── ρ ≤ c_g     → Copy gbest (exploitation)
              ├── ρ ≤ c_w     → Giữ nguyên (conservation)
              ├── ρ ≤ c_l     → Lévy flight (global exploration)
              └── ρ > c_l     → DE perturbation (directed exploration)
```

Và `n_abs` **tự tăng khi stagnation** (Eq. 62):

```
Bình thường:  n_abs = 0.2  → 80% SSO, 20% ALNS
Stagnation 5: n_abs = 0.45 → 55% SSO, 45% ALNS  
Stagnation max: n_abs = 0.5 → 50% SSO, 50% ALNS
```

Khi thuật toán bị kẹt -> tăng ALNS (local search chuyên sâu cho VRPTW) -> phá vỡ stagnation -> stagnation reset -> quay lại SSO nhiều hơn (global search). Đây là **vòng phản hồi tự điều chỉnh**.

---

### Tóm lại

SSO trong thuật toán của bạn là **Enhanced SSO** với 2 cải tiến cốt lõi:
1. **Lévy flight** thay random U(0,1) ở nhánh exploration vô hướng
2. **DE/rand/1** thêm nhánh exploration có hướng hoàn toàn mới

Và toàn bộ Enhanced SSO này lại được đặt trong **adaptive switching** với ALNS — tạo thành hệ thống **global search (Enhanced SSO) + local search (ALNS)** tự cân bằng theo stagnation.

---

**User**

DE/rand/1 trình bày chi tiết về ý tưởng cái này và tại sao cần có nó, nếu không có thì sao

---

**Cursor**

## DE/rand/1 Perturbation — Giải thích chi tiết

---

### 1. DE/rand/1 là gì?

DE (Differential Evolution) là thuật toán tiến hóa của Storn & Price (1997). "rand/1" là chiến lược đơn giản nhất: lấy **sự khác biệt giữa 2 cá thể ngẫu nhiên** làm hướng di chuyển.

Công thức trong thuật toán của bạn (Eq. 43):

```
x_new = x_i + F × (x_r1 - x_r2)
```

Trong đó:
- `x_i`: vị trí hiện tại của cá thể
- `x_r1, x_r2`: 2 cá thể **ngẫu nhiên khác** trong quần thể
- `F = 0.5`: hệ số scale
- `(x_r1 - x_r2)`: **difference vector** — chính là "ý tưởng cốt lõi"

---

### 2. Ý tưởng cốt lõi: "Học hướng đi từ quần thể"

Hãy tưởng tượng bạn đang tìm đường trong sương mù:

**Random U(0,1) — SSO gốc:**
> "Tôi nhắm mắt nhảy đại một bước ngẫu nhiên"
> -> Không biết nhảy đi đâu, không dùng bất kỳ thông tin nào

**Lévy flight:**
> "Tôi nhắm mắt nhưng nhảy theo kiểu thông minh — nhiều bước nhỏ xen kẽ vài bước rất xa"
> -> Khám phá tốt hơn nhưng vẫn **vô hướng**

**DE/rand/1:**
> "Tôi nhìn 2 người khác trong nhóm, thấy họ đứng ở đâu, rồi đi theo **hướng nối giữa họ**"
> -> **Có hướng**, hướng đó dựa trên phân bố thực tế của quần thể

Cụ thể, vector `(x_r1 - x_r2)` chứa thông tin:
- **Hướng**: từ r2 đến r1 trong không gian tìm kiếm
- **Độ lớn**: khoảng cách giữa r1 và r2 — phản ánh **diversity hiện tại** của quần thể

---

### 3. Tính chất đặc biệt: Implicit Adaptive Step Size

Đây là điểm mạnh nhất mà random và Lévy đều không có (Eq. 81 trong tài liệu):

```
Var[x_r1 - x_r2] = 2 × Var[population]
```

Điều này có nghĩa:

| Giai đoạn | Diversity quần thể | Step size DE | Hành vi |
|---|---|---|---|
| **Đầu** (quần thể rải rác) | Cao | **Lớn** | Exploration mạnh |
| **Giữa** (đang hội tụ) | Trung bình | **Vừa** | Cân bằng |
| **Cuối** (quần thể tụ lại) | Thấp | **Nhỏ** | Exploitation tinh chỉnh |

Step size **tự động co giãn** theo trạng thái quần thể mà không cần parameter nào điều khiển. Random U(0,1) luôn nhảy trong [0,1] bất kể quần thể đang ở đâu.

---

### 4. Tại sao cần cả Lévy VÀ DE? Không chỉ 1 trong 2?

Hai cơ chế này **bổ sung cho nhau**, không thay thế nhau:

```
                    Vô hướng          Có hướng
                 (isotropic)       (anisotropic)
                ┌──────────────┬──────────────────┐
Heavy-tailed    │  LÉVY FLIGHT │     (không có)   │
(occasional     │  Nhảy xa,    │                  │
 long jumps)    │  mọi hướng   │                  │
                ├──────────────┼──────────────────┤
Gaussian-tailed │  Random U(0,1)│  DE/rand/1      │
(normal steps)  │  SSO gốc     │  Nhảy theo hướng │
                │  (bị thay thế)│  population      │
                └──────────────┴──────────────────┘
```

- **Lévy**: giỏi **thoát local optima** (nhảy xa bất ngờ) nhưng không biết nên nhảy **hướng nào**
- **DE**: biết nên nhảy **hướng nào** (dựa trên quần thể) nhưng bước nhảy **bình thường** (Gaussian), ít khi nhảy xa

Kết hợp cả hai -> thuật toán vừa có khả năng nhảy xa (Lévy) vừa biết nhảy hướng nào (DE).

---

### 5. Nếu KHÔNG có DE/rand/1 thì sao?

Đây chính là variant **V2** trong Ablation Study (Section 16):

> **V2: No DE perturbation** — thay DE bằng random U(0,1)

Kỳ vọng kết quả:

**Mất hướng ở nhánh exploration cuối cùng:**
```
Enhanced SSO (đầy đủ):
  ρ ≤ c_g  → gbest (có hướng ✓)
  ρ ≤ c_w  → giữ nguyên
  ρ ≤ c_l  → Lévy (vô hướng, nhưng heavy-tailed ✓)  
  ρ > c_l  → DE (CÓ HƯỚNG ✓)  ← mất cái này

V2 (không DE):
  ρ ≤ c_g  → gbest (có hướng ✓)
  ρ ≤ c_w  → giữ nguyên
  ρ ≤ c_l  → Lévy (vô hướng ✓)
  ρ > c_l  → U(0,1) (vô hướng, bước cố định ✗)  ← quay lại như SSO gốc
```

**Hậu quả cụ thể:**

| Vấn đề | Giải thích |
|---|---|
| **Mất adaptive step size** | U(0,1) luôn trong [0,1], không scale theo diversity quần thể |
| **Mất directed search** | Không tận dụng thông tin vị trí các cá thể khác |
| **Convergence chậm hơn** | Đặc biệt ở giai đoạn cuối khi cần fine-tune nhỏ |
| **Exploration kém hướng** | Chỉ còn Lévy (vô hướng) cho exploration, thiếu chiều "có hướng" |

**Ước tính impact:** -3% đến -7% HV (theo kỳ vọng trong Section 16.5). Không phải component quan trọng nhất (ALNS quan trọng hơn với -15% đến -25%), nhưng **có ý nghĩa thống kê**.

---

### 6. Ví dụ trực quan với VRPTW

Giả sử quần thể 100 solutions đang tối ưu routing cho 100 khách hàng:

```
Solution r1: routes tốt cho cluster phía Bắc
Solution r2: routes tốt cho cluster phía Nam

Difference vector (r1 - r2): 
  → Mã hóa sự khác biệt giữa "ưu tiên Bắc" vs "ưu tiên Nam"

x_new = x_i + 0.5 × (r1 - r2):
  → Di chuyển x_i theo hướng "từ chiến lược Nam sang chiến lược Bắc"
  → Tạo ra solution mới thử nghiệm vùng chuyển tiếp
```

Trong khi đó:
- **U(0,1)** sẽ tạo random key hoàn toàn mới -> route mới **không liên quan** đến bất kỳ solution tốt nào
- **Lévy** sẽ nhảy xa theo hướng gbest nhưng **không biết có cluster Bắc-Nam**

---

### Tóm lại

DE/rand/1 đóng vai trò **exploration có hướng dựa trên trí tuệ tập thể** của quần thể:
1. Hướng di chuyển: học từ sự khác biệt giữa 2 cá thể
2. Bước nhảy: tự co giãn theo diversity (implicit adaptive)
3. Bổ sung cho Lévy: Lévy lo "nhảy xa", DE lo "nhảy đúng hướng"
4. Nếu bỏ: mất kênh exploration có hướng duy nhất ngoài gbest

---

**User**

vậy giờ cái thuật toán này không còn là GA nữa nhỉ

---

**Cursor**

Đúng, thuật toán này **không phải GA** (Genetic Algorithm). Phân biệt rõ:

---

### GA truyền thống dùng gì

```
Parent A:  [0.73, 0.12, 0.89, 0.45, 0.31]
Parent B:  [0.21, 0.88, 0.34, 0.67, 0.55]
                        ↓
            Crossover (cắt ghép gen)
                        ↓
Child:     [0.73, 0.12, 0.34, 0.67, 0.55]
                        ↓
            Mutation (đột biến ngẫu nhiên)
                        ↓
Child':    [0.73, 0.12, 0.34, 0.91, 0.55]
```

GA dựa trên **chọn lọc + lai ghép + đột biến** — mô phỏng di truyền sinh học.

---

### iNSSSO dùng gì

```
x_i:       [0.73, 0.12, 0.89, 0.45, 0.31]  ← cá thể hiện tại
                        ↓
         ┌──── 80% thời gian ────┐  ┌──── 20% thời gian ────┐
         │   Enhanced SSO path   │  │      ALNS path         │
         │                       │  │                        │
         │  ρ ≤ 0.5: copy gbest │  │  Destroy routes        │
         │  ρ ≤ 0.7: giữ nguyên │  │  Repair routes         │
         │  ρ ≤ 0.88: Lévy jump │  │  2-opt cải thiện       │
         │  ρ > 0.88: DE vector  │  │  SA acceptance         │
         └───────────────────────┘  └────────────────────────┘
                        ↓
              Polynomial mutation (chỉ khi stagnation)
```

**Không có crossover**. Không có chọn 2 parents lai ghép. Cơ chế hoàn toàn khác.

---

### Phân loại chính xác

| Thành phần | Thuộc họ | Không phải |
|---|---|---|
| **SSO** (Squirrel Search) | Swarm Intelligence | Evolutionary/GA |
| **Lévy flight** | Random walk theory | Genetic operator |
| **DE/rand/1** | Differential Evolution | Crossover |
| **ALNS** | Local search / Neighbourhood search | Evolutionary |
| **NDS + SDE** | Multi-objective framework | GA-specific |
| **Polynomial mutation** | Borrowed từ NSGA-II, nhưng chỉ phụ | GA core |

Thuật toán của bạn là **Swarm-based metaheuristic hybrid**:

```
iNSSSO = SSO (swarm intelligence)
       + Lévy flight (random walk)
       + DE perturbation (differential evolution)  
       + ALNS (neighbourhood search)
       + MaO framework (NDS + SDE + reference directions)
       + Preference (ASF + R-dominance + ROI)
```

---

### Tại sao điều này quan trọng cho bài báo

Trong literature, các thuật toán so sánh được phân loại rõ:

| Thuật toán | Loại |
|---|---|
| NSGA-II, NSGA-III, SPEA2 | **Evolutionary Algorithm (EA)** — dùng crossover + mutation |
| MOEA/D | **Decomposition EA** |
| MOPSO | **Swarm Intelligence** — dùng velocity + position |
| **iNSSSO** | **Swarm Intelligence + Local Search hybrid** |

Bạn **không nên** gọi iNSSSO là GA hay EA. Trong bài báo, khi mô tả, nên dùng:

> *"...a swarm-based metaheuristic that hybridizes enhanced Squirrel Search Optimization with Adaptive Large Neighbourhood Search..."*

Cái duy nhất "mượn" từ thế giới EA là **polynomial mutation** (Eq. 64-65), nhưng nó chỉ đóng vai trò phụ — chỉ kích hoạt khi stagnation > 3 và với xác suất thấp (5-15%). Đây là thực hành phổ biến — nhiều swarm algorithms mượn mutation từ EA để tăng diversity mà không vì thế trở thành GA.

---

**User**

tóm lại mục đích của DualArchive Logic để làm gì

---

**Cursor**

## Dual Archive — Mục đích cốt lõi

Một câu duy nhất:

> **Giữ lại 2 loại solution tốt nhất mà 1 archive đơn lẻ không thể giữ đồng thời.**

---

### Vấn đề: Convergence-Diversity Dilemma

Khi có 5 mục tiêu (M=5), bạn phải chọn 1 trong 2:

```
Chiến lược A: "Giữ solutions gần preference của DM nhất"
  → HỘI TỤ tốt (convergence) 
  → Nhưng MẤT solutions ở rìa Pareto front
  
Chiến lược B: "Giữ solutions trải đều trên toàn bộ Pareto front"  
  → ĐA DẠNG tốt (diversity)
  → Nhưng LOÃNG vùng preference, DM không có gì tập trung để chọn
```

**Với 1 archive, bạn PHẢI chọn A hoặc B. Không thể cả hai.**

Ishibuchi (2017) đã chứng minh toán học điều này. Đây không phải vấn đề thiết kế — đây là **giới hạn cấu trúc**.

---

### Giải pháp: 2 archive, mỗi cái lo 1 việc

```
┌─────────────────────────────┐  ┌─────────────────────────────┐
│        A_conv               │  │        A_div                │
│   (Convergence Archive)     │  │   (Diversity Archive)       │
│                             │  │                             │
│  Mục đích: HỘI TỤ          │  │  Mục đích: ĐA DẠNG         │
│  Giữ solutions GẦN ROI nhất │  │  Giữ solutions TRẢI ĐỀU    │
│                             │  │  trên toàn bộ Pareto front  │
│  Cơ chế vào:                │  │                             │
│    ε-dominance boxing       │  │  Cơ chế vào:               │
│    (chia objective space    │  │    Pareto dominance thuần   │
│     thành ô lưới)           │  │    (non-dominated thì nhận) │
│                             │  │                             │
│  Cơ chế loại:               │  │  Cơ chế loại:              │
│    ASF cao nhất bị loại     │  │    SDE thấp nhất bị loại   │
│    (xa preference nhất)     │  │    (chỗ đông nhất)          │
│                             │  │                             │
│  Kết quả: ●●●● tập trung   │  │  Kết quả: ●  ●  ●  ●  ●   │
│           quanh ROI         │  │           trải đều PF       │
└─────────────────────────────┘  └─────────────────────────────┘
```

---

### Dùng 2 archive này vào việc gì?

**Injection vào quần thể** — bơm solution tốt từ archive vào để hướng dẫn tìm kiếm:

```
Thuật toán đang chạy tốt (stagnation thấp):
  → Bơm từ A_div (đa dạng) → khám phá thêm vùng mới

Thuật toán bị kẹt (stagnation cao):  
  → Bơm từ A_conv (hội tụ) → tập trung vào vùng preference
```

Xác suất chọn archive nào dựa trên sigmoid (Eq. 57):

```
stagnation = 0   → 88% A_div,  12% A_conv   (khám phá)
stagnation = 10  → 50% A_div,  50% A_conv   (cân bằng)
stagnation = 20  → 12% A_div,  88% A_conv   (tập trung)
```

**Kết quả cuối cùng** trả về DM:

```
PF_approx = A_conv ∪ A_div  (gộp cả hai, lọc dominated)
```

DM nhận được Pareto front vừa **tập trung quanh preference** (nhờ A_conv) vừa **có bức tranh toàn cảnh** (nhờ A_div).

---

### Nếu chỉ dùng 1 archive?

Đây là variant **V4** trong Ablation Study:

| | Dual Archive | Single Archive (V4) |
|---|---|---|
| Solutions quanh ROI | Nhiều, chất lượng cao | Bị loãng bởi solutions xa |
| Solutions ở rìa PF | Được bảo toàn trong A_div | Có thể bị pruning mất |
| Khi stagnation | Chuyển sang bơm A_conv | Không có nguồn tập trung |
| HV kỳ vọng | Baseline | **-8% đến -12%** |

Mất dual archive = mất khả năng **vừa hội tụ vừa đa dạng** cùng lúc.

---

**User**

vòng đời của từng cái ra sao, cái nào bị mất qua mỗi vòng lặp cái nào được thêm qua mỗi vòng lặp hay như nào

---

**Cursor**

Câu hỏi rất hay — đây là **dòng chảy dữ liệu qua từng vòng lặp**, ai sống ai chết ai được sinh ra:

---

## Vòng đời 1 Generation — Từng bước

```
GEN t                                          GEN t+1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POPULATION P (100 con)                         POPULATION P' (100 con)
A_conv (tối đa 200)                            A_conv' (tối đa 200)
A_div  (tối đa 200)                            A_div'  (tối đa 200)
```

Giờ đi qua từng bước trong 1 vòng lặp:

---

### Bước 1: Ranking quần thể hiện tại

```
P = {s₁, s₂, ..., s₁₀₀}   ← 100 solutions từ gen trước
         │
         ▼
    NDS + SDE ranking
         │
         ▼
  Front 0: {s₃, s₇, s₁₂, ...}   ← non-dominated (tốt nhất)
  Front 1: {s₁, s₅, s₂₀, ...}   ← bị front 0 dominate
  Front 2: {s₈, s₉, ...}         ← bị front 0+1 dominate
  ...

KHÔNG AI BỊ LOẠI. Chỉ gán rank + SDE score.
```

---

### Bước 2: Sinh 100 offspring (Q)

```
Với MỖI cá thể i = 1..100 trong P:
│
├─ 20% xác suất → ALNS path
│   P[i] decode → routes → destroy → repair → 2-opt → encode
│   → offspring y_i (MỚI HOÀN TOÀN về routes)
│
└─ 80% xác suất → Enhanced SSO path  
    P[i] + gbest + r1,r2 → Eq.40 → offspring y_i
    (CẬP NHẬT từ P[i], không phải tạo mới hoàn toàn)

Kết quả: Q = {y₁, y₂, ..., y₁₀₀}   ← 100 offspring MỚI
```

**P vẫn còn nguyên.** Q là thế hệ con, tồn tại song song.

---

### Bước 3: Mutation (tùy điều kiện)

```
Nếu stagnation > 3:
  Một số y_i trong Q bị polynomial mutation
  (xác suất 5-15%, thay đổi trực tiếp trên y_i)

Q vẫn 100 con, một số bị biến đổi thêm.
```

---

### Bước 4: Local search (tùy điều kiện)

```
Với mỗi y_i trong Q:
  Nếu feasible + rank 0 → 10% xác suất local search
  Nếu không              → 3% xác suất local search

Khoảng 5-10 con trong Q được cải thiện thêm bởi 2-opt, merge.
Q vẫn 100 con.
```

---

### Bước 5: CẬP NHẬT ARCHIVE (đây là phần quan trọng)

```
Với MỖI offspring y_i trong Q:
│
├──→ Thử vào A_conv:
│      Box(y_i) = ⌊f(y_i) / ε⌋
│      │
│      ├─ Box mới, không bị dominated → THÊM vào A_conv ✅
│      │   + Loại mọi z trong A_conv mà y_i dominate ❌
│      │
│      ├─ Box đã có solution z:
│      │   ASF(y_i) < ASF(z) → y_i THAY THẾ z ✅↔❌
│      │   ASF(y_i) ≥ ASF(z) → y_i bị BỎ QUA ✗
│      │
│      └─ y_i bị dominated → BỎ QUA ✗
│
│      Nếu |A_conv| > 200 → Sort theo ASF, GIỮ 200 tốt nhất
│                            Phần dư bị LOẠI ❌
│
└──→ Thử vào A_div (SONG SONG, KHÔNG LIÊN QUAN A_conv):
       │
       ├─ y_i non-dominated trong A_div → THÊM ✅
       │   + Loại mọi z bị y_i dominate ❌
       │
       └─ y_i bị dominated → BỎ QUA ✗

       Nếu |A_div| > 200 → Tính SDE, LOẠI con đông nhất ❌
```

**Tóm lại archive mỗi gen:**

| Sự kiện | A_conv | A_div |
|---|---|---|
| Solution mới tốt hơn | **Thêm** hoặc **thay thế** | **Thêm** |
| Solution cũ bị dominated bởi mới | **Bị loại** | **Bị loại** |
| Quá đông (>200) | Loại ASF cao nhất | Loại SDE thấp nhất |
| Solution tồi | Không vào | Không vào |

**Archive KHÔNG BAO GIỜ bị reset.** Nó chỉ lớn dần và được prune khi quá 200. Solutions tốt **sống mãi** trong archive cho đến khi bị solution tốt hơn thay thế.

---

### Bước 6: Injection từ archive

```
Lấy 1 solution từ archive bơm vào Q:

  stagnation thấp → lấy từ A_div  (khám phá)
  stagnation cao  → lấy từ A_conv (tập trung)

Q: 100 con → 101 con (thêm 1 từ archive)
```

---

### Bước 7: Environmental Selection (AI SỐNG AI CHẾT)

```
merged = P ∪ Q = 100 + 101 = 201 solutions
                    │
                    ▼
            NDS + SDE + Niching
                    │
                    ▼
         CHỌN ĐÚNG 100 CON TỐT NHẤT → P'

  Ưu tiên: Front 0 trước → Front 1 → ...
  Front cuối (biên): dùng Niching + SDE phá tie
```

**Đây là lúc "chết":**

```
201 con vào → 100 con ra

101 con BỊ LOẠI VĨNH VIỄN khỏi quần thể
(nhưng có thể vẫn sống trong archive nếu đã vào được)
```

---

### Bước 8: Cập nhật normalizer

```
ideal, nadir được cập nhật bằng EMA từ P' mới
→ Ảnh hưởng đến SDE, ASF, ROI ở gen sau
```

---

## Sơ đồ tổng thể 1 vòng

```
GEN t
═══════════════════════════════════════════════════════════

P (100)  ──ranking──→  P (100, có rank + SDE)
                           │
                    ┌──────┴──────┐
                    │ Sinh offspring│
                    └──────┬──────┘
                           ▼
                       Q (100 mới)
                           │
                    ┌──────┴──────┐
                    │ Mutation +   │
                    │ Local search │
                    └──────┬──────┘
                           ▼
                       Q (100, cải thiện)
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          A_conv        A_div       Injection
          (cập nhật)   (cập nhật)  (lấy 1 con)
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Q (101 = 100 + 1 injected)
                           │
                    ┌──────┴──────┐
                    │   P ∪ Q     │
                    │  201 con    │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Chọn 100   │
                    │  NDS+SDE    │
                    │  +Niching   │
                    └──────┬──────┘
                           ▼
                       P' (100)  ──→  GEN t+1

═══════════════════════════════════════════════════════════
```

---

## Ai sống, ai chết, ai bất tử

| Đối tượng | Vòng đời | Ghi chú |
|---|---|---|
| **P (quần thể)** | 100 con mỗi gen. **101 con chết** mỗi gen (từ merged 201) | Cạnh tranh khốc liệt |
| **Q (offspring)** | Sinh ra đầu gen, **sống hoặc chết** cuối gen tại selection | Tạm thời |
| **A_conv** | **Tích lũy qua mọi gen.** Chỉ chết khi bị thay thế bởi tốt hơn hoặc prune | Gần như bất tử |
| **A_div** | **Tích lũy qua mọi gen.** Chỉ chết khi bị dominated hoặc prune đông nhất | Gần như bất tử |
| **gbest** | Chọn lại mỗi gen từ Front 0 bằng ASF | Thay đổi liên tục |
| **ideal/nadir** | Cập nhật EMA mỗi gen, **không bao giờ reset** | Monotonic (ideal chỉ giảm) |
| **Operator scores (ALNS)** | Cập nhật mỗi lần dùng, **tích lũy qua gen** | Học dần |
| **stagnation** | Tăng mỗi gen nếu kẹt, **reset về 0** khi cải thiện | Dao động |

**Điểm mấu chốt:** Archive là **bộ nhớ dài hạn** — solution tốt nhất từng tìm được không bao giờ mất. Quần thể là **bộ nhớ ngắn hạn** — cạnh tranh mỗi gen, 50% bị loại.

---

**User**

vậy A_conv là ngon còn A_div là không ngon, khi mà ngon nhiều quá sẽ cho không ngon vào để khám phá tiếp đúng không

---

**Cursor**

Gần đúng nhưng cần chỉnh lại một chút — **cả hai đều ngon, nhưng ngon theo kiểu khác nhau:**

---

## A_conv vs A_div — Không phải ngon vs không ngon

```
A_conv = ngon theo MẮT CỦA BẠN (preference)
A_div  = ngon theo TOÁN HỌC (Pareto optimal, trải đều)
```

Cụ thể:

```
Objective space (2D đơn giản hóa):

    Z₂ (distance)
    ▲
    │  ○                          ○  ← A_div giữ (rìa PF)
    │     ○
    │        ●●●●                    ← A_conv giữ (gần preference)
    │           ●●●  ★ ← preference point (DM muốn ở đây)
    │              ●●
    │                 ○              ← A_div giữ
    │                    ○           ← A_div giữ (rìa PF)
    └──────────────────────────▶ Z₁ (số xe)

    ● = A_conv (tập trung quanh ★)
    ○ = A_div  (trải đều toàn bộ mặt Pareto)
```

**A_div không phải solution tồi.** Nó cũng non-dominated (không ai dominate nó). Chỉ là nó **xa chỗ bạn muốn**.

---

## Logic injection — Bạn hiểu đúng hướng

```
Thuật toán đang chạy tốt (chưa bị kẹt):
  → "Tôi đang tìm tốt, khám phá thêm vùng mới đi"
  → Bơm từ A_div (solutions ở xa, mở rộng tầm nhìn)

Thuật toán bị KẸT (stagnation cao):
  → "Tôi bị kẹt rồi, quay về chỗ ngon nhất tập trung đào sâu"
  → Bơm từ A_conv (solutions gần preference, đào sâu ROI)
```

Nói cách khác:

| Trạng thái | Bơm gì | Tại sao |
|---|---|---|
| Đang khỏe | A_div (xa preference) | Khám phá vùng mới, tránh bị kẹt sớm |
| Bị kẹt | A_conv (gần preference) | Quay về vùng tốt nhất, đào sâu thêm |

---

## Ví dụ đời thực

Bạn đang tìm nhà hàng ngon:

```
A_conv = Danh sách nhà hàng BẠN THÍCH (gần nhà, đúng khẩu vị, đúng giá)
A_div  = Danh sách nhà hàng TOP ĐÁNH GIÁ (có thể xa, có thể đắt, 
         nhưng đều 5 sao theo tiêu chí nào đó)

Bình thường: "Thử chỗ mới đi, lấy gợi ý từ top đánh giá" → A_div
Chán rồi, không tìm ra gì mới: "Quay lại chỗ mình thích nhất" → A_conv
```

---

## Tại sao cần A_div nếu đã có A_conv?

Nếu chỉ có A_conv (chỉ bơm solution gần preference):

```
Gen 1:   tìm quanh ★
Gen 10:  vẫn quanh ★  
Gen 50:  vẫn quanh ★ ← BỊ KẸT, không thoát ra được
Gen 100: vẫn quanh ★ ← mất cơ hội tìm solution tốt hơn ở xa
```

Có A_div:

```
Gen 1:   tìm quanh ★
Gen 10:  bơm ○ từ A_div → nhảy sang vùng mới
Gen 15:  tìm thấy vùng mới có ●● tốt hơn cả ★ cũ!
Gen 20:  preference cập nhật, A_conv giờ tốt hơn trước
```

**A_div là bảo hiểm** — đảm bảo thuật toán không bỏ lỡ vùng tốt nào trên Pareto front mà chỉ vì nó xa preference ban đầu.

---

**User**

A_div và A_con theo lần lượt công thức nào ở trong tài liệu

---

**Cursor**

Đây là mapping chính xác từng công thức cho từng archive:

---

## A_conv (Convergence Archive)

| Bước | Công thức | Section | Mục đích |
|---|---|---|---|
| **Chia ô lưới** | **Eq. 54** — `box(f) = ⌊f_m / (ε + 1e-15)⌋` | §9.3 | Chia objective space thành ε-box |
| **Thay thế trong box** | **Eq. 55** — `box(x) = box(y) ∧ ASF_aug(x) < ASF_aug(y)` | §9.3 | Trong cùng box, giữ con có ASF thấp hơn |
| **Tính ASF** | **Eq. 33** — `ASF(x) = max_m { w_m · (f_m(x) - g_m) }` | §6.1 | Đo khoảng cách đến preference |
| **Tính ASF tăng cường** | **Eq. 34** — `ASF_aug = max{...} + ρ·Σ{...}` | §6.1 | Phá tie khi max bằng nhau |
| **Pruning khi quá 200** | Sort theo **Eq. 34**, giữ top N_A | §9.2 | Loại solutions xa preference nhất |

**Tóm lại A_conv:** Eq. 54 (chia box) → Eq. 55 (thay thế) → Eq. 33-34 (ASF ranking)

---

## A_div (Diversity Archive)

| Bước | Công thức | Section | Mục đích |
|---|---|---|---|
| **Vào archive** | **Eq. 20** — Pareto dominance `x ≺ y` | §5.1 | Non-dominated thì nhận |
| **Chuẩn hóa** | **Eq. 24** — `f̂_m = (f_m - f_min) / (f_max - f_min + ε)` | §5.2 | Chuẩn hóa trước khi tính SDE |
| **Shift operation** | **Eq. 25** — `shifted_{i,j,m} = max(f̂_m(j), f̂_m(i))` | §5.2 | Dịch chuyển để phạt solution bị dominated |
| **Khoảng cách SDE** | **Eq. 26** — `d_SDE(i,j) = ‖shifted - f̂(i)‖₂` | §5.2 | Đo mật độ quanh mỗi solution |
| **Giá trị SDE** | **Eq. 27** — `SDE(i) = min_{j≠i} d_SDE(i,j)` | §5.2 | SDE thấp = chỗ đông, SDE cao = chỗ vắng |
| **Pruning khi quá 200** | **Eq. 56** — `remove = argmin_i SDE(i)` | §9.4 | Loại solution ở chỗ đông nhất |

**Tóm lại A_div:** Eq. 20 (Pareto check) → Eq. 24-27 (tính SDE) → Eq. 56 (prune đông nhất)

---

## Injection — Chọn bơm từ archive nào

| Bước | Công thức | Section | Mục đích |
|---|---|---|---|
| **Xác suất chọn** | **Eq. 57** — `p_conv = 1 / (1 + e^-(s/5 - 2))` | §9.5 | Sigmoid dựa trên stagnation |

---

## Pseudocode tổng hợp

Toàn bộ flow nằm trong **Algorithm 4** (§9.7):

```951:993:g:\vrptw-for-pisso\paper_q1_full.md
Algorithm 4: Dual Archive Update
// ...
 2: box_x ← ⌊f(x) / (ε + 1e-15)⌋        // Eq. 54  ← A_conv
 7:         if ASF_aug(x) < ASF_aug(y) then  // Eq. 55  ← A_conv
20:     Sort A_conv by ASF_aug ascending      // Eq. 34  ← A_conv prune
25: if ¬∃y ∈ A_div : y ≺ x then              // Eq. 20  ← A_div
30:     sde ← VectorisedSDE(f(A_div))        // Eq. 24-27 ← A_div
31:     Remove argmin_i sde(i) from A_div     // Eq. 56  ← A_div prune
```

---

## Bản đồ nhanh

```
A_conv: Eq.54 → Eq.55 → Eq.33-34         (ε-box + ASF)
A_div:  Eq.20 → Eq.24-27 → Eq.56         (Pareto + SDE)
Injection: Eq.57                           (Sigmoid chọn archive)
```

---

**User**

5.2 Vectorised Shift-based Density Estimation (SDE) giải thích kỹ hơn cái này đi

---

**Cursor**

Giờ tôi giải thích kỹ từng bước:

---

## SDE — Tại sao cần nó?

### Vấn đề của Crowding Distance (CD)

CD của NSGA-II tính mật độ bằng cách xét **từng mục tiêu riêng lẻ**, rồi cộng lại:

```
Ví dụ M=2: CD hoạt động tốt
                                    
  Z₂ ▲                            
     │  A ────── khoảng cách trên Z₂
     │  │                          
     │  B ← tính CD               
     │  │                          
     │  C ────── khoảng cách trên Z₂
     │                             
     └──┼──┼──┼──────────▶ Z₁     
        A  B  C  khoảng cách trên Z₁

CD(B) = (C.Z₁ - A.Z₁)/(max-min) + (A.Z₂ - C.Z₂)/(max-min)
→ Đo được B đông hay vắng ✓
```

Nhưng khi M=5:

```
CD(i) = CD_Z₁(i) + CD_Z₂(i) + CD_Z₃(i) + CD_Z₄(i) + CD_Z₅(i)

Mỗi chiều tính riêng → 5 con số cộng lại
Theo Central Limit Theorem, khi M lớn:
  Tổng 5 khoảng cách 1-chiều → gần như bằng nhau cho mọi solution
  → CD ≈ hằng số → KHÔNG PHÂN BIỆT ĐƯỢC AI ĐÔNG AI VẮNG
```

---

## SDE — Giải thích từng bước bằng ví dụ

Giả sử 3 solutions, 2 mục tiêu (đơn giản hóa để dễ thấy):

```
Solution A: f = (0.2, 0.8)   ← non-dominated
Solution B: f = (0.3, 0.7)   ← non-dominated  
Solution C: f = (0.5, 0.9)   ← bị A dominate (cả hai mục tiêu đều tệ hơn A)
```

---

### Bước 1 — Chuẩn hóa (Eq. 24)

Đưa mọi mục tiêu về [0, 1]:

```
f_min = (0.2, 0.7)    f_max = (0.5, 0.9)

Â: f̂ = ((0.2-0.2)/(0.5-0.2), (0.8-0.7)/(0.9-0.7)) = (0.0, 0.5)
B̂: f̂ = ((0.3-0.2)/(0.5-0.2), (0.7-0.7)/(0.9-0.7)) = (0.33, 0.0)
Ĉ: f̂ = ((0.5-0.2)/(0.5-0.2), (0.9-0.7)/(0.9-0.7)) = (1.0, 1.0)
```

---

### Bước 2 — Shift operation (Eq. 25) — ĐÂY LÀ BƯỚC THEN CHỐT

Khi tính khoảng cách từ solution i đến j, **dịch j ra xa gốc nếu j tốt hơn i**:

```
shifted_{i,j,m} = max(f̂_m(j), f̂_m(i))
```

Ý nghĩa: "Nếu j tốt hơn i ở mục tiêu m, giả vờ j ở cùng vị trí với i ở mục tiêu đó."

**Ví dụ: Tính shifted cho cặp (C, A):**

```
C = (1.0, 1.0),  A = (0.0, 0.5)

shifted_{C,A,Z₁} = max(f̂_Z₁(A), f̂_Z₁(C)) = max(0.0, 1.0) = 1.0
shifted_{C,A,Z₂} = max(f̂_Z₂(A), f̂_Z₂(C)) = max(0.5, 1.0) = 1.0

shifted_{C,A} = (1.0, 1.0)  ← GIỐNG HỆT C!
```

**Ví dụ: Tính shifted cho cặp (A, B):**

```
A = (0.0, 0.5),  B = (0.33, 0.0)

shifted_{A,B,Z₁} = max(f̂_Z₁(B), f̂_Z₁(A)) = max(0.33, 0.0) = 0.33
shifted_{A,B,Z₂} = max(f̂_Z₂(B), f̂_Z₂(A)) = max(0.0, 0.5) = 0.5

shifted_{A,B} = (0.33, 0.5)  ← B bị đẩy ra xa A
```

---

### Bước 3 — Distance (Eq. 26)

```
d_SDE(i, j) = ‖shifted_{i,j} - f̂(i)‖₂
```

**Cho C (bị dominated bởi A):**

```
d_SDE(C, A) = ‖(1.0, 1.0) - (1.0, 1.0)‖ = 0.0  ← BẰNG 0!
```

**Cho A (non-dominated):**

```
d_SDE(A, B) = ‖(0.33, 0.5) - (0.0, 0.5)‖ = 0.33
```

**Cho B (non-dominated):**

```
d_SDE(B, A) = ‖(0.0, 0.33) - shifted...‖ 
shifted_{B,A} = (max(0.0, 0.33), max(0.5, 0.0)) = (0.33, 0.5)
d_SDE(B, A) = ‖(0.33, 0.5) - (0.33, 0.0)‖ = 0.5
```

---

### Bước 4 — SDE value (Eq. 27)

```
SDE(i) = min_{j≠i} d_SDE(i, j)
```

```
SDE(A) = min(d(A,B), d(A,C)) = min(0.33, ...) = 0.33   ← vắng
SDE(B) = min(d(B,A), d(B,C)) = min(0.5, ...)  = 0.5    ← rất vắng
SDE(C) = min(d(C,A), d(C,B)) = min(0.0, ...)  = 0.0    ← ĐÔNG (≈ bị dominated)
```

---

### Kết quả

```
SDE(B) = 0.5  > SDE(A) = 0.33  > SDE(C) = 0.0

Ưu tiên giữ: B > A > C
Ưu tiên loại: C (SDE thấp nhất)
```

**C bị dominated bởi A → shift operation khiến d_SDE(C,A) = 0 → SDE(C) = 0 → bị loại đầu tiên.**

Đây chính là magic: **SDE tự động phạt solution bị dominated** mà không cần check dominance riêng!

---

## Tại sao gọi là "Shift"?

```
Không gian objective (đã chuẩn hóa):

     Z₂ ▲
    1.0 │        C (1.0, 1.0)
        │       ╱
        │      ╱  ← Shift đẩy A lên vị trí C
    0.5 │  A (0.0, 0.5)          khi nhìn từ C
        │    ╲
        │     ╲
    0.0 │      B (0.33, 0.0)
        └──────────────────▶ Z₁
       0.0   0.33        1.0
```

Khi tính d_SDE(C, A):
- A tốt hơn C ở cả 2 mục tiêu
- Shift **đẩy A lên vị trí C** → khoảng cách = 0
- Nghĩa là: "Từ góc nhìn của C, A đè lên đầu nó"

Khi tính d_SDE(A, B):
- B tốt hơn A ở Z₂, A tốt hơn B ở Z₁ (trade-off)
- Shift chỉ đẩy **phần tốt hơn** → khoảng cách > 0
- Nghĩa là: "A và B không đè nhau, có khoảng cách thực"

---

## Tóm lại bằng 1 câu

> **SDE = "khoảng cách đến hàng xóm gần nhất, nhưng nếu hàng xóm tốt hơn tôi thì giả vờ nó đè lên tôi."**

- SDE cao → solution cô lập, quý giá → **giữ**
- SDE thấp → solution bị đè hoặc quá đông → **loại**
- Khác CD: SDE kết hợp cả **convergence** (phạt dominated) lẫn **diversity** (phạt đông) trong 1 con số duy nhất

---

**User**

Trình bày rõ hơn về DE và tại sao lại cần Lévy kết hợp với DE

---

**Cursor**

## DE (Differential Evolution) — Giải thích từ gốc

### DE là gì?

DE (Storn & Price, 1997) là thuật toán tiến hóa dựa trên 1 ý tưởng cực kỳ đơn giản:

> **"Hướng đi tốt = sự khác biệt giữa 2 cá thể trong quần thể"**

```
Quần thể có 100 solutions, mỗi solution là 1 điểm trong không gian tìm kiếm

Chọn ngẫu nhiên r1 và r2:
  r1 = [0.7, 0.3, 0.8, 0.1, 0.5]   ← solution tốt về distance
  r2 = [0.2, 0.9, 0.4, 0.6, 0.3]   ← solution tốt về balance

Difference vector:
  r1 - r2 = [0.5, -0.6, 0.4, -0.5, 0.2]
             ↑
             Mã hóa sự khác biệt giữa 2 chiến lược routing

Cá thể x_i di chuyển theo hướng này:
  x_new = x_i + 0.5 × (r1 - r2)
                 ↑
                 F = scaling factor
```

---

### Difference vector chứa thông tin gì?

```
r1 tốt về distance:    routes ngắn, gom khách gần nhau
r2 tốt về balance:     routes đều tải, nhưng có thể dài hơn

(r1 - r2) = "chuyển từ chiến lược balance sang chiến lược distance"

x_i + F × (r1 - r2) = "thử dịch x_i một chút theo hướng đó"
```

Mỗi lần chọn r1, r2 khác nhau → **hướng đi khác nhau** → khám phá nhiều chiều của không gian.

---

### Tính chất quan trọng nhất: Implicit Adaptive Step Size

```
ĐẦU quá trình (quần thể rải rác):

  ○         ○                    ○
       ○          ○        ○
  ○        ○           ○         ○

  ‖r1 - r2‖ LỚN → bước nhảy LỚN → exploration mạnh


CUỐI quá trình (quần thể hội tụ):

              ○○○
             ○○○○○
              ○○○

  ‖r1 - r2‖ NHỎ → bước nhảy NHỎ → exploitation tinh chỉnh
```

**Không cần parameter nào điều khiển.** Step size tự co giãn theo trạng thái quần thể.

So sánh:

```
Random U(0,1):  luôn nhảy trong [0,1] bất kể quần thể ở đâu
                ĐẦU: OK     CUỐI: quá lớn, phá solution tốt

Lévy flight:    step size cố định theo phân phối heavy-tailed
                ĐẦU: OK     CUỐI: occasional long jump có thể phá

DE:             step size = f(diversity quần thể)
                ĐẦU: lớn ✓  CUỐI: nhỏ ✓  TỰ ĐỘNG ✓
```

---

### Tính chất thứ hai: Directed (Có hướng)

```
Không gian 5 chiều (5 objectives):

Random/Lévy:  nhảy theo MỌI HƯỚNG với xác suất bằng nhau
              ↗ ↑ ↖ ← ↙ ↓ ↘ → 
              Như ném đá vào bóng tối

DE:           nhảy theo HƯỚNG NỐI 2 solutions tốt
              →→→  (hướng từ r2 đến r1)
              Như đi theo bản đồ
```

Mỗi cặp (r1, r2) tạo 1 hướng. Với quần thể 100 con → có C(100,2) = 4950 hướng khả thi → rất phong phú.

---

## Lévy Flight — Giải thích từ gốc

### Lévy là gì?

Random walk với bước nhảy theo phân phối **heavy-tailed**:

```
Normal (Gaussian):          Lévy (β=1.5):
Phần lớn bước = trung bình  Phần lớn bước = rất nhỏ
Rất ít bước lớn              Đôi khi bước CỰC LỚN
                             
  ██████████                    ██████████████████
  ██████████                    ██
  ████████                      █
  ██████                        █
  ████                          █
  ██                            █ ← đuôi dài (heavy tail)
  █                             █
  █                             █
─────────────────           ─────────────────────────
  step size                     step size
```

### Trong thuật toán (Eq. 40-42):

```
x_new = x_i + L × (gbest - x_i) × 0.01
              ↑         ↑
         Lévy step   hướng về gbest

L = u / |v|^(1/β)    ← Mantegna's algorithm (Eq. 41)
u ~ N(0, σ²)         ← Gaussian
v ~ N(0, 1)           ← Gaussian

Khi |v| rất nhỏ (hiếm) → L CỰC LỚN → nhảy xa
Khi |v| bình thường    → L nhỏ      → fine-tune quanh vị trí hiện tại
```

---

## Tại sao cần CẢ HAI? Không chỉ 1?

### Nếu CHỈ có DE (không Lévy):

```
Quần thể bị kẹt ở local optimum:

              ○○○○
             ○○○○○○    ← tất cả tụ lại 1 chỗ
              ○○○○

  ‖r1 - r2‖ ≈ 0  → DE step ≈ 0 → KHÔNG THOÁT ĐƯỢC

  Vùng tốt hơn ở xa:         ★★★
                              ★★★★
                              
  DE không bao giờ tới được vì bước nhảy quá nhỏ
```

**DE chết khi quần thể mất diversity.** Nó phụ thuộc hoàn toàn vào sự khác biệt trong quần thể.

### Nếu CHỈ có Lévy (không DE):

```
Quần thể đang hội tụ tốt, cần fine-tune:

              ○○○○
             ○○○○○○    ← gần optimal, cần tinh chỉnh
              ○○○○
                                    ↗ Lévy nhảy xa (phá solution tốt!)
  Lévy: phần lớn OK (bước nhỏ)     
        nhưng đôi khi nhảy VÔ HƯỚNG → lãng phí, đi sai chỗ

  Có 4950 hướng tốt từ quần thể mà Lévy KHÔNG BIẾT
```

**Lévy lãng phí vì nhảy vô hướng.** Nó không biết hướng nào triển vọng.

### Khi có CẢ HAI:

```
TRƯỜNG HỢP 1: Quần thể còn đa dạng
  DE:   ‖r1-r2‖ lớn → bước lớn, CÓ HƯỚNG     → khám phá hiệu quả ✓
  Lévy: bước nhỏ/lớn, VÔ HƯỚNG                → khám phá bổ sung ✓

TRƯỜNG HỢP 2: Quần thể bị kẹt (diversity thấp)  
  DE:   ‖r1-r2‖ ≈ 0 → BẤT LỰC                → ✗
  Lévy: occasional long jump → THOÁT            → cứu cánh ✓✓✓

TRƯỜNG HỢP 3: Gần optimal, cần fine-tune
  DE:   ‖r1-r2‖ nhỏ → bước nhỏ, CÓ HƯỚNG     → tinh chỉnh chính xác ✓✓
  Lévy: phần lớn bước nhỏ                      → tinh chỉnh bổ sung ✓
```

---

## Bảng so sánh tổng hợp

```
                 VÔ HƯỚNG              CÓ HƯỚNG
              (isotropic)           (anisotropic)
            ┌────────────────┬────────────────────┐
HEAVY-TAIL  │                │                    │
(nhảy xa    │  LÉVY FLIGHT   │    (không có)      │
 đôi khi)   │                │                    │
            │  Giỏi: thoát   │                    │
            │  local optima   │                    │
            │                │                    │
            │  Kém: lãng phí │                    │
            │  hướng          │                    │
            ├────────────────┼────────────────────┤
ADAPTIVE    │                │                    │
(scale theo │  Random U(0,1) │  DE/rand/1         │
 context)   │  SSO gốc       │                    │
            │  (BỊ THAY THẾ) │  Giỏi: đúng hướng │
            │                │  + tự scale        │
            │                │                    │
            │                │  Kém: chết khi     │
            │                │  diversity = 0     │
            └────────────────┴────────────────────┘
            
  Lévy bù cho DE khi DE bất lực (diversity thấp)
  DE bù cho Lévy khi Lévy lãng phí (đi sai hướng)
```

---

## Ví dụ cụ thể với VRPTW

```
Gen 1: Quần thể 100 solutions đa dạng
       r1: 8 xe, distance 850, wait 20
       r2: 12 xe, distance 620, wait 45
       
       DE: (r1-r2) = "giảm xe, tăng distance, giảm wait"
           → Hướng rõ ràng, bước lớn → khám phá trade-off xe vs distance ✓
       
       Lévy: nhảy ngẫu nhiên xa → tìm được vùng 10 xe hoàn toàn mới ✓

Gen 50: Quần thể hội tụ, tất cả 9-10 xe, distance 700-720
        r1: 9 xe, distance 708
        r2: 10 xe, distance 712
        
        DE: (r1-r2) rất nhỏ → fine-tune chính xác ✓
            nhưng không thoát được vùng 9-10 xe
        
        Lévy: occasional long jump → tìm thấy solution 7 xe, distance 680! ✓
              (nhảy xa thoát local optimum)

Gen 50 (nếu CHỈ có DE):
        DE step ≈ 0 → kẹt tại 9-10 xe FOREVER ✗

Gen 50 (nếu CHỈ có Lévy):  
        Lévy nhảy xa nhưng vô hướng → 90% nhảy tệ hơn, 10% nhảy tốt
        Lãng phí nhiều evaluations ✗
```

---

## Tóm lại

| | DE/rand/1 | Lévy flight | Kết hợp |
|---|---|---|---|
| **Hướng** | Có (từ quần thể) | Không | Vừa có hướng vừa tự do |
| **Step size** | Tự scale theo diversity | Heavy-tailed cố định | Adaptive + occasional jumps |
| **Khi diversity cao** | Mạnh | Mạnh | Cả hai mạnh |
| **Khi diversity thấp** | **Chết** | Vẫn nhảy được | **Lévy cứu DE** |
| **Hiệu quả hướng** | Cao | Thấp (lãng phí) | **DE dẫn đường, Lévy mở rộng** |
| **Lý thuyết** | Directed mutation [Storn 1997] | Superdiffusion [Viswanathan 1999] | Bổ sung orthogonal |

> **DE là GPS — biết đường đi nhưng chỉ trong phạm vi bản đồ.**
> **Lévy là trực thăng — nhảy được mọi nơi nhưng không biết nên đi đâu.**
> **Kết hợp = GPS + trực thăng: đi đúng hướng, và khi bản đồ hết thì bay ra ngoài tìm.**

---

**User**

nói tóm tắt dễ hiểu hơn đi

---

**Cursor**

## DE + Lévy — Giải thích 30 giây

---

**DE** = Hỏi đường người dân địa phương

> "Anh r1 ở đâu? Anh r2 ở đâu? OK, tôi đi theo hướng từ r2 đến r1."

Ưu: Biết đường. Nhược: Nếu tất cả dân tụ 1 chỗ → không ai chỉ được đường mới.

---

**Lévy** = Nhảy dù ngẫu nhiên

> "99 lần nhảy gần → 1 lần nhảy CỰC XA, rơi vào vùng đất mới."

Ưu: Luôn có thể tìm vùng mới. Nhược: Không biết nên nhảy hướng nào → may rủi.

---

**Kết hợp:**

```
Bình thường → DE dẫn đường (nhanh, chính xác)
Bị kẹt      → Lévy nhảy dù thoát ra (DE bất lực, Lévy cứu)
Vùng mới    → DE lại dẫn đường tiếp
```

Chỉ vậy thôi.

---

**User**

tạo tài liệu chi tiết về những gì tôi vừa hỏi

---

**Cursor**

Đã tạo file `giai_thich_chi_tiet_iNSSSO.md` với 10 phần chi tiết, tổng hợp tất cả những gì chúng ta đã thảo luận:

| # | Nội dung | Từ câu hỏi |
|---|---|---|
| 1 | Phân loại thuật toán — không phải GA | "thuật toán này không còn là GA nữa nhỉ" |
| 2 | Điểm nổi bật để apply Q1 | "điều gì làm nổi bật thuật toán" |
| 3 | Bài báo cụ thể chứng minh khoảng trống | "đưa cụ thể tên bài báo" |
| 4 | NDS — Fast Non-dominated Sorting | "giải thích phần 5.1" |
| 5 | SDE — Shift-based Density Estimation | "giải thích kỹ hơn SDE" |
| 6 | DE/rand/1 Perturbation | "trình bày chi tiết DE" |
| 7 | Lévy Flight | "tại sao cần Lévy kết hợp DE" |
| 8 | Tại sao cần cả DE lẫn Lévy | "tại sao cần Lévy kết hợp DE" |
| 9 | Dual Archive — A_conv và A_div | "mục đích DualArchive" + "công thức nào" |
| 10 | Vòng đời 1 Generation | "cái nào bị mất, cái nào được thêm" |

Tất cả đều có cross-reference về equations và sections trong `paper_q1_full.md` để dễ đối chiếu.

---

**User**

nói rõ hơn về 6 DE/rand/1 Perturbation

---

**Cursor**

Đã mở rộng Section 6 từ ~20 dòng thành phần chi tiết với 12 mục con. Đây là tóm tắt những gì đã thêm:

| Mục | Nội dung mới |
|---|---|
| **6.1** | Nguồn gốc DE, giải thích tên "DE/rand/1", tại sao không dùng DE/best/1 hay DE/rand/2 |
| **6.2** | Công thức Eq. 43 với giải thích từng thành phần |
| **6.3** | Ví dụ số cụ thể: difference vector chứa thông tin gì khi áp dụng lên random-key encoding |
| **6.4** | Tại sao F = 0.5, range hợp lệ, so sánh F nhỏ vs lớn |
| **6.5** | Implicit adaptive step size — toán học + bảng + hình minh họa quần thể rải rác vs hội tụ |
| **6.6** | Directed search — so sánh trực quan với random/Lévy, 4950 hướng khả thi |
| **6.7** | Diversity-preserving — tại sao rand/1 tốt hơn best/1 cho MaO |
| **6.8** | Ví dụ VRPTW cụ thể: 2 solutions có chiến lược routing khác nhau → difference vector mã hóa trade-off |
| **6.9** | Điểm yếu: chết khi diversity = 0, minh họa bằng hình |
| **6.10** | Variant V2 ablation: so sánh trước/sau khi bỏ DE |
| **6.11** | DE trong bối cảnh 4 nhánh Enhanced SSO — xác suất và vai trò từng nhánh |
| **6.12** | References chính về DE |

---

**User**

chỉ cho tôi đoạn code kết hợp giữa lévy và DE

---

**Cursor**

Đây là đoạn code. Giải thích từng dòng:

### File: `algorithm/inssso.py` — Hàm `update_solution`

```445:497:g:\vrptw-for-pisso\algorithm\inssso.py
    # ----- SSO update (Enhanced Eq 2) — with Lévy flight & DE perturbation ---
    def update_solution(self, xi: Solution, gbest: Solution,
                        xr1: Optional[Solution] = None,
                        xr2: Optional[Solution] = None) -> Solution:
        # ... docstring ...
        nvar = xi.nvar
        rho = np.random.rand(nvar)

        # Standard SSO: copy from gBest
        new_keys = np.where(rho <= self.cg, gbest.keys, xi.keys)

        # Lévy flight exploration (replaces pure random for ρ > c_w)
        c_l = self.cw + (1.0 - self.cw) * 0.6  # 60% of exploration band
        levy_mask = (rho > self.cw) & (rho <= c_l)
        if np.any(levy_mask):
            levy_steps = self._levy_flight(nvar, beta=1.5)
            direction = gbest.keys - xi.keys
            levy_keys = xi.keys + levy_steps * direction * 0.01
            new_keys = np.where(levy_mask, levy_keys, new_keys)

        # Differential perturbation (remaining exploration band)
        de_mask = rho > c_l
        if np.any(de_mask) and xr1 is not None and xr2 is not None:
            F = 0.5
            de_keys = xi.keys + F * (xr1.keys - xr2.keys)
            new_keys = np.where(de_mask, de_keys, new_keys)
        else:
            random_keys = np.random.rand(nvar)
            new_keys = np.where(de_mask, random_keys, new_keys)

        new_keys = np.clip(new_keys, 0.0, 0.999)
        return Solution(keys=new_keys, ...)
```

### Mapping code → lý thuyết

```
Line 468:  rho = np.random.rand(nvar)
           ↑ Sinh ρ_j cho MỖI gene j (Eq. 40)

Line 471:  new_keys = np.where(rho <= self.cg, gbest.keys, xi.keys)
           ↑ NHÁNH 1+2: ρ ≤ c_g → gbest (exploitation)
                         c_g < ρ ≤ c_w → giữ nguyên (conservation)
             np.where xử lý cả 2 nhánh cùng lúc vì xi.keys là default

Line 474:  c_l = self.cw + (1.0 - self.cw) * 0.6
           ↑ Ranh giới Lévy/DE: c_l = c_w + 0.6(1 - c_w)
             Với c_w = 0.7: c_l = 0.7 + 0.6 × 0.3 = 0.88

Line 475:  levy_mask = (rho > self.cw) & (rho <= c_l)
           ↑ NHÁNH 3: c_w < ρ ≤ c_l → Lévy flight
             Xác suất: c_l - c_w = 0.18 → 18% genes

Line 477:  levy_steps = self._levy_flight(nvar, beta=1.5)
           ↑ Mantegna's algorithm (Eq. 41-42)
             Trả về array heavy-tailed steps

Line 478:  direction = gbest.keys - xi.keys
           ↑ Hướng từ xi đến gbest

Line 479:  levy_keys = xi.keys + levy_steps * direction * 0.01
           ↑ Eq. 40 nhánh Lévy: x_i + L × (gbest - x_i) × 0.01
             0.01 giữ bước nhảy nhỏ (Lévy steps có thể rất lớn)

Line 483:  de_mask = rho > c_l
           ↑ NHÁNH 4: ρ > c_l → DE perturbation
             Xác suất: 1 - c_l = 1 - 0.88 = 0.12 → 12% genes

Line 485-486: F = 0.5
              de_keys = xi.keys + F * (xr1.keys - xr2.keys)
           ↑ Eq. 43: x_i + F × (r1 - r2)
             Difference vector từ 2 donors

Line 488-490: else: random_keys (fallback nếu r1, r2 = None)
           ↑ An toàn: nếu không có donors thì dùng random

Line 492:  new_keys = np.clip(new_keys, 0.0, 0.999)
           ↑ Giữ keys trong [0, 1) cho random-key encoding
```

### Hàm `_levy_flight` — Mantegna's Algorithm

```499:515:g:\vrptw-for-pisso\algorithm\inssso.py
    @staticmethod
    def _levy_flight(n: int, beta: float = 1.5) -> np.ndarray:
        # ... Eq. 41-42 ...
        sigma_u = (
            _gamma(1 + beta) * np.sin(np.pi * beta / 2)
            / (_gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
        ) ** (1.0 / beta)
        u = np.random.normal(0, sigma_u, n)
        v = np.random.normal(0, 1, n)
        return u / (np.abs(v) ** (1.0 / beta))
```

```
sigma_u  → Eq. 42: σ_u = [Γ(1+β)sin(πβ/2) / Γ((1+β)/2)·β·2^((β-1)/2)]^(1/β)
u ~ N(0, σ_u²)  → Gaussian với variance đặc biệt
v ~ N(0, 1)      → Gaussian chuẩn
return u/|v|^(1/β) → Eq. 41: L = u / |v|^(1/β)

Khi |v| rất nhỏ (hiếm) → L CỰC LỚN → occasional long jump
Khi |v| bình thường    → L nhỏ      → fine-tune cục bộ
```

### Phân bổ xác suất thực tế (với c_g=0.5, c_w=0.7)

```
Gene j bất kỳ:

  ρ ∈ [0.00, 0.50] → gbest      (50% — exploitation)
  ρ ∈ (0.50, 0.70] → giữ nguyên (20% — conservation)
  ρ ∈ (0.70, 0.88] → Lévy       (18% — undirected exploration)
  ρ ∈ (0.88, 1.00] → DE         (12% — directed exploration)
  ─────────────────────────────────────────────────
  0.0      0.5      0.7     0.88     1.0
  ████████████|██████████|█████████|██████|
   exploitation  conserve    Lévy     DE
```

Lévy và DE **cùng xử lý trên 1 vector keys**, mỗi gene **độc lập** chọn nhánh nào → solution mới là **hỗn hợp** 4 cơ chế, không phải chọn 1 cơ chế cho toàn bộ solution.

---

**User**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm 2: Enhanced SSO Update Rule
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  x_i (current), gbest, population P, c_g, c_w
Output: x_i^new (updated solution)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1: c_l ← c_w + 0.6 × (1 - c_w)
 2: Select r1, r2 ∈ P randomly, r1 ≠ r2 ≠ i
 3: Compute σ_u via Eq. 42  // Mantegna parameter
 4:
 5: for j = 1 to dim do
 6:     ρ_j ← U(0, 1)
 7:     if ρ_j ≤ c_g then
 8:         x_i,j^new ← gbest_j            // Exploitation
 9:     else if ρ_j ≤ c_w then
10:         x_i,j^new ← x_i,j              // Conservation
11:     else if ρ_j ≤ c_l then
12:         u ← N(0, σ_u²);  v ← N(0, 1)
13:         L_j ← u / |v|^(1/β)            // Lévy step (Eq. 41)
14:         x_i,j^new ← x_i,j + L_j × (gbest_j - x_i,j) × 0.01
15:     else
16:         x_i,j^new ← x_i,j + F × (x_{r1,j} - x_{r2,j})  // DE
17:     end if
18: end for
19:
20: x_i^new ← clip(x_i^new, 0, 0.999)
21: return x_i^new
có thể giải thích chi tiết và lấy ví dụ cụ thể giúp tôi được không, bạn hãy mô tả bài toán rõ ràng ra nhé ví dụ có 100 khách hàng

---

**Cursor**

## Algorithm 2 — Ví dụ cụ thể với 100 khách hàng

---

### Thiết lập bài toán

```
Solomon instance C101: 100 khách hàng, tối đa 25 xe
Capacity Q = 200, mỗi khách hàng có [e_i, l_i] time window

Random-key encoding:
  dim = n + K - 1 = 100 + 24 = 124 keys
  Vị trí 1-100:  ứng với 100 khách hàng
  Vị trí 101-124: 24 separator keys (phân cách routes)
```

---

### Đầu vào Algorithm 2

Giả sử đang xử lý cá thể thứ i = 37 trong quần thể 100 con:

```
x_i (cá thể 37):
  keys = [0.73, 0.12, 0.89, 0.45, 0.31, ..., 0.67, 0.08, 0.95]
                                                          (124 số)
  Decode ra: Route1: 0→5→2→8→0 | Route2: 0→1→4→3→0 | ... (10 routes)
  Objectives: Z₁=10 xe, Z₂=850km, Z₃=45 phút chờ, Z₄=18 balance, Z₅=320 makespan

gbest (solution tốt nhất trên Front 0, chọn bằng ASF):
  keys = [0.55, 0.28, 0.91, 0.33, 0.47, ..., 0.72, 0.15, 0.88]
  Decode ra: Route1: 0→2→5→8→0 | Route2: 0→3→1→4→0 | ... (8 routes)
  Objectives: Z₁=8, Z₂=780, Z₃=30, Z₄=12, Z₅=290

r1 (donor 1, chọn ngẫu nhiên, giả sử cá thể 52):
  keys = [0.40, 0.85, 0.22, 0.61, 0.19, ..., 0.50, 0.33, 0.77]
  Objectives: Z₁=9, Z₂=720, Z₃=55, Z₄=22, Z₅=310
  → Chiến lược: distance ngắn nhưng wait time cao

r2 (donor 2, chọn ngẫu nhiên, giả sử cá thể 81):
  keys = [0.15, 0.60, 0.78, 0.29, 0.83, ..., 0.44, 0.91, 0.12]
  Objectives: Z₁=11, Z₂=890, Z₃=15, Z₄=8, Z₅=280
  → Chiến lược: nhiều xe, wait ít, balance tốt
```

---

### Tham số

```
c_g = 0.5     (50% genes copy gbest)
c_w = 0.7     (20% genes giữ nguyên)
c_l = 0.7 + 0.6 × (1 - 0.7) = 0.7 + 0.18 = 0.88
              (18% genes dùng Lévy)
              (12% genes dùng DE)
F = 0.5       (DE scaling factor)
β = 1.5       (Lévy exponent)
```

---

### Bước 1: Tính σ_u cho Lévy (1 lần duy nhất)

```
σ_u = [Γ(1+1.5) × sin(π×1.5/2) / (Γ((1+1.5)/2) × 1.5 × 2^((1.5-1)/2))]^(1/1.5)

Γ(2.5) = 1.3294
sin(3π/4) = 0.7071
Γ(1.25) = 0.9064
2^0.25 = 1.1892

σ_u = [1.3294 × 0.7071 / (0.9064 × 1.5 × 1.1892)]^(1/1.5)
    = [0.9400 / 1.6168]^(0.6667)
    = [0.5813]^(0.6667)
    = 0.6966
```

---

### Bước 2: Lặp qua từng gene j = 1 đến 124

Tôi sẽ minh họa **6 genes** đại diện cho cả 4 nhánh:

---

#### Gene j=1 (khách hàng 1): ρ = 0.32 → **Exploitation**

```
ρ₁ = 0.32 ≤ c_g = 0.5  →  NHÁNH 1: Copy gbest

x_i,1 = 0.73   (vị trí cũ của khách hàng 1)
gbest₁ = 0.55  (vị trí gbest cho khách hàng 1)

x_new,1 = 0.55  ← copy thẳng từ gbest
```

**Ý nghĩa routing:** Khách hàng 1 giờ có key = 0.55 (thay vì 0.73). Khi decode (argsort), khách hàng 1 sẽ được **sắp xếp vào vị trí khác** trong permutation → có thể chuyển sang route khác hoặc thay đổi thứ tự phục vụ, **giống cách gbest sắp xếp**.

---

#### Gene j=2 (khách hàng 2): ρ = 0.45 → **Exploitation**

```
ρ₂ = 0.45 ≤ 0.5  →  NHÁNH 1: Copy gbest

x_i,2 = 0.12
gbest₂ = 0.28

x_new,2 = 0.28
```

---

#### Gene j=3 (khách hàng 3): ρ = 0.63 → **Conservation**

```
0.5 < ρ₃ = 0.63 ≤ c_w = 0.7  →  NHÁNH 2: Giữ nguyên

x_i,3 = 0.89

x_new,3 = 0.89  ← không thay đổi
```

**Ý nghĩa:** Khách hàng 3 giữ nguyên vị trí trong permutation. Thông tin tốt đã có từ x_i được **bảo toàn** — không phá hỏng phần đang tốt.

---

#### Gene j=4 (khách hàng 4): ρ = 0.58 → **Conservation**

```
0.5 < ρ₄ = 0.58 ≤ 0.7  →  NHÁNH 2: Giữ nguyên

x_new,4 = 0.45  ← giữ nguyên
```

---

#### Gene j=5 (khách hàng 5): ρ = 0.79 → **Lévy Flight**

```
0.7 < ρ₅ = 0.79 ≤ c_l = 0.88  →  NHÁNH 3: Lévy flight

Sinh Lévy step:
  u = N(0, 0.6966²) = giả sử u = 0.42
  v = N(0, 1)        = giả sử v = 0.15  ← nhỏ bất thường!

  L₅ = u / |v|^(1/1.5) = 0.42 / |0.15|^(0.667) = 0.42 / 0.282 = 1.49
       ↑ BƯỚC LỚN vì v nhỏ (hiếm gặp)

Tính hướng:
  direction₅ = gbest₅ - x_i,5 = 0.47 - 0.31 = +0.16
               ↑ hướng từ x_i đến gbest (dương = tăng key)

Tính vị trí mới:
  x_new,5 = x_i,5 + L₅ × direction₅ × 0.01
           = 0.31 + 1.49 × 0.16 × 0.01
           = 0.31 + 0.00238
           = 0.3124
```

**Ý nghĩa:** Khách hàng 5 dịch chuyển **rất nhẹ** (0.31 → 0.3124) theo hướng gbest. Dù L₅ lớn (1.49), nhân với 0.01 nên bước thực tế nhỏ. Nhưng nếu L₅ = 50 (rất hiếm, khi v ≈ 0), bước sẽ là 0.08 — đáng kể hơn nhiều.

**Ví dụ khi v cực nhỏ (long jump):**

```
  v = 0.005  (rất hiếm, ~0.4% xác suất)
  L₅ = 0.42 / |0.005|^(0.667) = 0.42 / 0.0293 = 14.33
  
  x_new,5 = 0.31 + 14.33 × 0.16 × 0.01 = 0.31 + 0.0229 = 0.333
  ↑ Nhảy đáng kể → khách hàng 5 đổi vị trí trong permutation
```

---

#### Gene j=100 (khách hàng 100): ρ = 0.93 → **DE Perturbation**

```
ρ₁₀₀ = 0.93 > c_l = 0.88  →  NHÁNH 4: DE/rand/1

r1 (cá thể 52): key₁₀₀ = 0.77
r2 (cá thể 81): key₁₀₀ = 0.12

Difference vector:
  r1₁₀₀ - r2₁₀₀ = 0.77 - 0.12 = +0.65
  ↑ Mã hóa: "r1 đặt khách hàng 100 SAU (key cao) trong permutation,
             r2 đặt TRƯỚC (key thấp)"

DE step:
  x_new,100 = x_i,100 + F × (r1₁₀₀ - r2₁₀₀)
             = 0.95 + 0.5 × 0.65
             = 0.95 + 0.325
             = 1.275  → clip → 0.999
```

**Ý nghĩa:** Khách hàng 100 bị đẩy lên key = 0.999 (vị trí cuối cùng trong argsort). Khi decode, khách hàng 100 sẽ được **phục vụ cuối** hoặc nằm cạnh separator → có thể chuyển sang route khác.

**Ví dụ DE bước nhỏ (quần thể đã hội tụ):**

```
Nếu r1₁₀₀ = 0.94, r2₁₀₀ = 0.96:
  difference = 0.94 - 0.96 = -0.02
  x_new = 0.95 + 0.5 × (-0.02) = 0.95 - 0.01 = 0.94
  ↑ Fine-tune nhẹ — đúng tính chất adaptive step size
```

---

### Bước 3: Clip toàn bộ vector

```
x_new = clip(x_new, 0, 0.999)

Trước clip: [..., 1.275, ..., -0.03, ...]
Sau clip:   [..., 0.999, ..., 0.000, ...]
```

---

### Kết quả cuối: Vector mới 124 keys

```
Gene:    j=1    j=2    j=3    j=4    j=5     ...  j=100   ...  j=124
Nhánh:   gBest  gBest  Giữ    Giữ    Lévy    ...  DE      ...  gBest
Cũ:      0.73   0.12   0.89   0.45   0.31    ...  0.95    ...  0.08
Mới:     0.55   0.28   0.89   0.45   0.3124  ...  0.999   ...  0.15
```

Khi decode (argsort) vector mới → permutation mới → routes mới → objectives mới.

---

### Phân bổ thực tế trên 124 genes

```
124 genes × xác suất:

~62 genes  (50%) → copy từ gbest        (exploitation)
~25 genes  (20%) → giữ nguyên           (conservation)
~22 genes  (18%) → Lévy flight           (undirected exploration)
~15 genes  (12%) → DE perturbation       (directed exploration)
─────────────────────────────────────
= 124 genes

Solution mới = HỖN HỢP 4 nguồn thông tin:
  50% cấu trúc từ gbest (solution tốt nhất)
  20% cấu trúc từ chính nó (bảo toàn)
  18% khám phá vô hướng (Lévy — có thể tìm vùng mới)
  12% khám phá có hướng (DE — theo sự khác biệt trong quần thể)
```

---

### Decode thành routes — Trước vs Sau

```
TRƯỚC (x_i):
  keys = [0.73, 0.12, 0.89, 0.45, 0.31, 0.67, ...]
  argsort → [2, 5, 4, 6, 1, 3, ...]
  Routes: 0→2→5→4→0 | 0→6→1→3→0 | ...
  Z₁=10, Z₂=850, Z₃=45, Z₄=18, Z₅=320

SAU (x_new):
  keys = [0.55, 0.28, 0.89, 0.45, 0.3124, 0.67, ...]
  argsort → [2, 5, 4, 1, 6, 3, ...]  ← thứ tự thay đổi!
                       ↑ KH1 đổi chỗ vì key đổi từ 0.73→0.55
  Routes: 0→2→5→4→1→0 | 0→6→3→0 | ...  ← KH1 chuyển sang Route1
  Z₁=9(?), Z₂=810(?), Z₃=38(?), Z₄=15(?), Z₅=305(?)
  
  → Ít xe hơn, distance giảm, wait giảm (hướng về gbest)
```

---

### Tóm lại bằng hình

```
x_i (cá thể 37)    ══════════════════════════════════════╗
                                                          ║
  50% genes ← gbest (copy cấu trúc tốt nhất)            ║
  20% genes ← chính nó (giữ phần đang tốt)              ║ → x_new
  18% genes ← Lévy (nhảy ngẫu nhiên, đôi khi xa)        ║   (solution mới)
  12% genes ← DE (nhảy có hướng theo r1-r2)              ║
                                                          ║
gbest, r1, r2    ═════════════════════════════════════════╝

x_new → decode → routes mới → evaluate Z₁..Z₅ → so sánh với x_i
```

Mỗi gene **độc lập quyết định** nhánh nào → solution mới là bức tranh ghép (mosaic) từ 4 nguồn thông tin, không phải chọn 1 cơ chế cho toàn bộ.

---

**User**

tức là cái  Enhanced SSO Update Rule này của tôi bản chất cũng chỉ là xáo trộn các xe thôi đúng không nhỉ, xáo trộn xong rồi ALNS sẽ đi sửa lại

---

**Cursor**

Không hẳn vậy. Cần phân biệt rõ: **SSO và ALNS là 2 đường đi song song, không phải nối tiếp.**

---

### Luồng thực tế trong Algorithm 1

```
Mỗi cá thể i:

  U(0,1) < 0.2?  ──Yes──→  ALNS path (20%)
                              Decode → phá routes → sửa routes → encode
                              → offspring y_i
  
  U(0,1) ≥ 0.2?  ──No───→  SSO path (80%)
                              Xáo trộn keys → decode → routes MỚI
                              → offspring y_i

  KHÔNG CÓ: SSO xáo trộn rồi ALNS sửa lại.
  Mỗi cá thể ĐI 1 TRONG 2 ĐƯỜNG, không đi cả 2.
```

---

### Enhanced SSO thực sự làm gì?

Đúng là **xáo trộn random keys** → khi decode sẽ ra routes khác. Nhưng không phải xáo trộn bừa:

```
Gene j=1: copy từ gbest     → khách hàng 1 được SẮP XẾP NHƯ solution tốt nhất
Gene j=2: giữ nguyên        → khách hàng 2 GIỮ vị trí đang tốt
Gene j=5: Lévy flight       → khách hàng 5 NHẢY ngẫu nhiên (thử vị trí mới)
Gene j=100: DE perturbation → khách hàng 100 DI CHUYỂN theo hướng quần thể
```

Kết quả: **routes thay đổi vì thứ tự khách hàng thay đổi**.

```
Trước: keys = [0.73, 0.12, 0.89, ...]
       argsort → KH2, KH5, KH4, KH1, KH3 → Route: 0→2→5→4→0 | 0→1→3→0

Sau:   keys = [0.55, 0.28, 0.89, ...]
       argsort → KH2, KH5, KH1, KH4, KH3 → Route: 0→2→5→1→0 | 0→4→3→0
                              ↑ KH1 đổi chỗ              ↑ routes thay đổi
```

SSO **thay đổi routes gián tiếp** qua việc thay đổi keys → thay đổi permutation → thay đổi phân bổ khách hàng vào xe.

---

### ALNS thực sự làm gì?

ALNS **thay đổi routes trực tiếp** trên cấu trúc routing:

```
Trước: Route1: 0→2→5→8→0 | Route2: 0→1→4→3→0

Destroy (ví dụ Shaw Removal): rút KH2, KH4 ra
  Route1: 0→_→5→8→0 | Route2: 0→1→_→3→0
  Removed = {KH2, KH4}

Repair (ví dụ Regret-2): chèn lại vào vị trí tốt nhất
  Route1: 0→5→4→8→0 | Route2: 0→2→1→3→0
                ↑ KH4 chèn vào Route1    ↑ KH2 chèn vào Route2

Sau: Route1: 0→5→4→8→0 | Route2: 0→2→1→3→0
```

ALNS **hiểu cấu trúc VRPTW**: biết distance, time window, capacity → chèn khách hàng vào chỗ **khả thi và rẻ nhất**.

---

### So sánh cốt lõi

| | Enhanced SSO | ALNS |
|---|---|---|
| **Làm việc trên** | Random keys (số thực [0,1]) | Routes trực tiếp (chuỗi khách hàng) |
| **Cách thay đổi routes** | Gián tiếp: đổi keys → decode → routes mới | Trực tiếp: rút KH ra → chèn lại |
| **Hiểu VRPTW không?** | **Không** — chỉ biết keys là số thực | **Có** — biết distance, TW, capacity |
| **Thay đổi lớn/nhỏ?** | Có thể rất lớn (đổi nhiều routes cùng lúc) | Cục bộ (chỉ sửa vài KH) |
| **Vai trò** | **Global search** — khám phá vùng mới | **Local search** — cải thiện vùng hiện tại |
| **Ví dụ** | Gộp 2 routes, tách 1 route, đảo nhiều KH | Dời 3 KH sang route bên cạnh |

---

### Tại sao 2 cái KHÔNG nối tiếp nhau?

```
NẾU SSO → ALNS (nối tiếp):
  SSO xáo trộn bừa → ALNS sửa lại → mất công SSO
  ALNS phải sửa MỌI lần → chậm
  SSO trở thành "tạo rác" cho ALNS dọn

THỰC TẾ (song song):
  80% cá thể đi SSO → khám phá nhanh nhiều vùng mới
  20% cá thể đi ALNS → đào sâu vùng hiện tại

  → Ai tốt hơn thì sống (environmental selection)
  → Không lãng phí evaluation
```

---

### Tóm lại

SSO **không chỉ xáo trộn bừa**. Nó xáo trộn có chiến lược:
- 50% copy cấu trúc từ solution tốt nhất
- 20% giữ phần tốt
- 18% + 12% khám phá mới (Lévy + DE)

Và SSO với ALNS là **2 con đường song song**, không phải SSO tạo ra rồi ALNS sửa lại. Mỗi cá thể chỉ đi **1 trong 2** đường, rồi tất cả cạnh tranh sống còn ở bước environmental selection.

---

**User**

Nếu như với GA thì sẽ có bước mutation còn thằng này là SSO nhỉ

---

**Cursor**

Đúng. Đây là sự khác biệt cơ bản:

---

### GA: Tạo con = Crossover + Mutation

```
Parent A: [0.73, 0.12, 0.89, 0.45, 0.31]
Parent B: [0.21, 0.88, 0.34, 0.67, 0.55]
                    │
              CROSSOVER (cắt tại vị trí 3)
                    │
Child:     [0.73, 0.12, 0.34, 0.67, 0.55]
                    │
              MUTATION (đột biến gene 4)
                    │
Child':    [0.73, 0.12, 0.34, 0.91, 0.55]
```

GA cần **2 operators riêng biệt**: crossover tạo đa dạng, mutation tránh kẹt.

---

### iNSSSO: Tạo con = Enhanced SSO (tất cả trong 1)

```
x_i:       [0.73, 0.12, 0.89, 0.45, 0.31]
                    │
              ENHANCED SSO (4 nhánh xử lý TỪNG gene)
                    │
              gene 1: copy gbest     ← "crossover" với solution tốt nhất
              gene 2: giữ nguyên     ← bảo toàn
              gene 3: Lévy flight    ← "mutation" heavy-tailed
              gene 4: DE             ← "mutation" có hướng
                    │
x_new:     [0.55, 0.12, 0.92, 0.60, 0.31]
```

Enhanced SSO **gộp tất cả vào 1 bước duy nhất**:

| Vai trò trong GA | Tương đương trong SSO | Nhánh |
|---|---|---|
| Crossover (lấy gene từ parent tốt) | Copy từ gbest | ρ ≤ c_g |
| Elitism (giữ gene tốt) | Conservation | c_g < ρ ≤ c_w |
| Mutation (đột biến ngẫu nhiên) | Lévy flight | c_w < ρ ≤ c_l |
| *(GA không có)* | DE directed mutation | ρ > c_l |

---

### Vậy iNSSSO có mutation không?

**Có, nhưng ở 2 tầng:**

```
Tầng 1 (LUÔN XẢY RA): Enhanced SSO đã có "mutation" built-in
  → Lévy flight (18% genes) = mutation vô hướng, heavy-tailed
  → DE (12% genes) = mutation có hướng
  → Tổng ~30% genes bị thay đổi mỗi lần = mutation rate rất cao

Tầng 2 (CHỈ KHI KẸT): Polynomial mutation bổ sung
  → Kích hoạt khi stagnation > 3
  → Xác suất 5-15%
  → Mượn từ NSGA-II, vai trò phụ
```

So sánh:

```
GA:
  Crossover ──→ Mutation ──→ Child
  (2 bước riêng biệt, nối tiếp)

iNSSSO:
  Enhanced SSO ──→ Child    (bình thường)
  Enhanced SSO ──→ Polynomial Mutation ──→ Child    (khi kẹt)
  (SSO đã bao gồm cả "crossover" và "mutation" trong 1 bước)
```

---

### Tại sao thiết kế này tốt hơn cho VRPTW?

```
GA crossover cho random keys:
  Parent A: [0.73, 0.12, 0.89, 0.45]
  Parent B: [0.21, 0.88, 0.34, 0.67]
  Child:    [0.73, 0.12, │ 0.34, 0.67]   ← cắt giữa
                          │
  Nửa trái từ A, nửa phải từ B
  → Khách hàng 1-2 theo route của A, khách hàng 3-4 theo route của B
  → Có thể tốt, có thể TỆ → không kiểm soát được

SSO cho random keys:
  x_i:     [0.73, 0.12, 0.89, 0.45]
  gbest:   [0.55, 0.28, 0.91, 0.33]
  
  Gene 1: copy gbest 0.55   ← chỉ gene CẦN THAY ĐỔI mới thay
  Gene 2: giữ 0.12          ← gene ĐANG TỐT thì giữ
  Gene 3: Lévy → 0.92       ← khám phá NHẸ
  Gene 4: DE → 0.60         ← khám phá CÓ HƯỚNG
  
  → Kiểm soát TỪNG gene → thay đổi chính xác hơn
```

**SSO thay đổi ở mức gene-by-gene (mỗi gene tự quyết định nhánh nào), GA crossover thay đổi ở mức block (cắt cả đoạn).** Với 124 genes (100 KH + 24 separator), gene-level control cho phép tinh chỉnh chính xác hơn việc khách hàng nào cần đổi route, khách hàng nào nên giữ nguyên.

---

**User**

  gene 1: copy gbest     ← "crossover" với solution tốt nhất
              gene 2: giữ nguyên     ← bảo toàn
              gene 3: Lévy flight    ← "mutation" heavy-tailed
              gene 4: DE             ← "mutation" có hướng
tôi thực sự chưa hiểu gene này ý là đang nói như nào nhỉ, rõ hơn được không 

---

**Cursor**

## "Gene" là gì trong bài toán này?

### Mỗi solution = 1 dãy số thực (random keys)

Với 100 khách hàng + 24 separator = **124 con số**. Mỗi con số gọi là **1 gene**.

```
Solution x_i:

  gene 1   gene 2   gene 3   gene 4   gene 5  ...  gene 100  gene 101 ... gene 124
  [0.73,   0.12,    0.89,    0.45,    0.31,   ...,  0.67,     0.08,   ..., 0.95]
    ↑        ↑        ↑        ↑        ↑             ↑         ↑            ↑
   KH 1    KH 2     KH 3     KH 4     KH 5         KH 100   Separator   Separator
```

**Gene = 1 ô trong dãy = 1 con số = quyết định vị trí của 1 khách hàng.**

---

### Gene quyết định gì?

Khi decode, dãy keys được **sắp xếp tăng dần** (argsort):

```
Keys:     [0.73,  0.12,  0.89,  0.45,  0.31]
            KH1    KH2    KH3    KH4    KH5

Argsort:   KH2(0.12) → KH5(0.31) → KH4(0.45) → KH1(0.73) → KH3(0.89)

Routes:    0 → KH2 → KH5 → KH4 → 0  |  0 → KH1 → KH3 → 0
                                  ↑ separator ở đâu đó
```

**Key nhỏ = được phục vụ trước. Key lớn = được phục vụ sau.**

Vậy khi bạn **thay đổi 1 gene** (1 con số), bạn thay đổi **thứ tự phục vụ** của khách hàng đó → có thể khiến nó **đổi route**.

---

### Ví dụ thay đổi 1 gene

```
TRƯỚC: gene 1 (KH1) = 0.73

Keys:     [0.73,  0.12,  0.89,  0.45,  0.31]
Thứ tự:   KH2 → KH5 → KH4 → KH1 → KH3
                                ↑ KH1 ở vị trí thứ 4

Routes:   0 → KH2 → KH5 → KH4 → 0  |  0 → KH1 → KH3 → 0
          Route 1                       Route 2 (KH1 ở đây)


SAU: gene 1 (KH1) đổi thành 0.20 (copy từ gbest)

Keys:     [0.20,  0.12,  0.89,  0.45,  0.31]
Thứ tự:   KH2 → KH1 → KH5 → KH4 → KH3
                  ↑ KH1 nhảy lên vị trí thứ 2!

Routes:   0 → KH2 → KH1 → KH5 → KH4 → 0  |  0 → KH3 → 0
          Route 1 (KH1 chuyển sang đây!)       Route 2
```

**Chỉ đổi 1 gene (0.73 → 0.20) mà KH1 đã chuyển từ Route 2 sang Route 1.**

---

### 4 nhánh SSO — mỗi gene RIÊNG LẺ quyết định

Quay lại Algorithm 2, với dãy 124 genes:

```
Gene 1 (KH1):  ρ = 0.32 ≤ 0.5  → Copy gbest
  x_i có key = 0.73
  gbest có key = 0.20
  → ĐỔI thành 0.20
  → KH1 sẽ được phục vụ SỚM HƠN (như cách gbest sắp xếp)

Gene 2 (KH2):  ρ = 0.63 → Giữ nguyên
  x_i có key = 0.12
  → GIỮ 0.12
  → KH2 không thay đổi vị trí (đang tốt rồi)

Gene 3 (KH3):  ρ = 0.79 → Lévy flight
  x_i có key = 0.89
  Lévy step → key mới = 0.92
  → KH3 dịch NHẸNHÀNG (0.89 → 0.92)
  → Có thể đổi thứ tự với KH lân cận, có thể không

Gene 4 (KH4):  ρ = 0.93 → DE
  x_i có key = 0.45
  r1 có key = 0.61, r2 có key = 0.29
  DE: 0.45 + 0.5 × (0.61 - 0.29) = 0.45 + 0.16 = 0.61
  → KH4 dịch ĐÁNG KỂ (0.45 → 0.61)
  → KH4 được phục vụ TRỄ HƠN → có thể chuyển sang route khác
```

---

### Hình dung toàn bộ 124 genes

```
Gene:   1     2     3     4     5     6  ...  50  ...  100   101  ...  124
Nhánh: gBest  Giữ  Lévy   DE  gBest  Giữ ... Lévy ...  DE   gBest ...  Giữ
       ████  ░░░░  ▓▓▓▓  ▒▒▒▒ ████  ░░░░    ▓▓▓▓     ▒▒▒▒  ████      ░░░░

████ = Copy gbest     (~62 genes, 50%)  "Đặt KH này giống cách tốt nhất"
░░░░ = Giữ nguyên    (~25 genes, 20%)  "KH này đang ổn, không đổi"
▓▓▓▓ = Lévy flight   (~22 genes, 18%)  "Thử dịch KH này ngẫu nhiên"
▒▒▒▒ = DE            (~15 genes, 12%)  "Dịch KH này theo hướng quần thể"
```

Mỗi gene **tự rút thăm** (ρ = U(0,1)) để quyết định đi nhánh nào. Không phải chọn 1 nhánh cho toàn bộ solution.

---

### Tóm lại

```
1 gene = 1 con số thực = vị trí của 1 khách hàng trong thứ tự phục vụ

Đổi gene → đổi thứ tự → đổi route → đổi objectives

4 nhánh SSO = 4 cách đổi 1 gene:
  Copy gbest:  đặt KH này giống solution tốt nhất
  Giữ nguyên:  không đổi
  Lévy:        dịch ngẫu nhiên (đôi khi nhảy xa)
  DE:          dịch theo hướng 2 cá thể khác trong quần thể
```

---

**User**

giải thích kĩ hơn  ρ là gì sao mỗi gen lại khác nhau

---

**Cursor**

## ρ là gì?

**ρ = 1 số ngẫu nhiên từ 0 đến 1**, sinh ra cho **mỗi gene riêng biệt**.

---

### Cụ thể trong code

```467:468:g:\vrptw-for-pisso\algorithm\inssso.py
        nvar = xi.nvar
        rho = np.random.rand(nvar)
```

`np.random.rand(124)` sinh ra **124 số ngẫu nhiên**, mỗi số cho 1 gene:

```
rho = [0.32, 0.63, 0.79, 0.93, 0.15, 0.88, 0.41, ...]
       ↑      ↑      ↑      ↑      ↑
      gene1  gene2  gene3  gene4  gene5    ... (124 số)
```

Mỗi số là **độc lập** — như **tung 124 đồng xu riêng biệt**.

---

### Tại sao mỗi gene khác nhau?

Hãy tưởng tượng bạn có **124 nhân viên** (124 khách hàng). Bạn muốn quyết định cho mỗi người: làm theo cách mới (gbest), giữ cách cũ, hay thử cách khác.

**Cách 1 (tung 1 lần cho tất cả — KHÔNG dùng):**

```
Tung 1 đồng xu → ra "gbest"
→ TẤT CẢ 124 người đều làm theo gbest
→ Solution mới = bản copy 100% của gbest
→ Mất hết thông tin từ x_i → TỆ
```

**Cách 2 (tung riêng cho mỗi người — ĐANG DÙNG):**

```
Nhân viên 1: tung → 0.32 → "theo gbest"
Nhân viên 2: tung → 0.63 → "giữ cách cũ"
Nhân viên 3: tung → 0.79 → "thử Lévy"
Nhân viên 4: tung → 0.93 → "thử DE"
...

→ Solution mới = HỖN HỢP nhiều nguồn
→ Giữ phần tốt + học phần mới + khám phá thêm
```

---

### Ví dụ cụ thể: ρ quyết định nhánh nào

```
Ngưỡng:  c_g = 0.5     c_w = 0.7     c_l = 0.88

Gene 1:  ρ = 0.32  ──→  0.32 ≤ 0.5?  CÓ  → gbest     ████
Gene 2:  ρ = 0.63  ──→  0.63 ≤ 0.5?  KHÔNG
                         0.63 ≤ 0.7?  CÓ  → giữ       ░░░░
Gene 3:  ρ = 0.79  ──→  0.79 ≤ 0.5?  KHÔNG
                         0.79 ≤ 0.7?  KHÔNG
                         0.79 ≤ 0.88? CÓ  → Lévy      ▓▓▓▓
Gene 4:  ρ = 0.93  ──→  0.93 ≤ 0.5?  KHÔNG
                         0.93 ≤ 0.7?  KHÔNG
                         0.93 ≤ 0.88? KHÔNG → DE       ▒▒▒▒
```

Giống như thang đo:

```
ρ:   0.0 ──────── 0.5 ──── 0.7 ──── 0.88 ──── 1.0
     │   gbest    │  giữ   │  Lévy  │   DE    │
     │   (50%)    │ (20%)  │ (18%)  │  (12%)  │
     
Gene 1: ρ=0.32 ●
Gene 2: ρ=0.63          ●
Gene 3: ρ=0.79                  ●
Gene 4: ρ=0.93                              ●
```

---

### Nếu tung lại → kết quả khác hoàn toàn

Lần chạy thứ 2 với **cùng x_i, cùng gbest**:

```
LẦN 1:                          LẦN 2:
rho = [0.32, 0.63, 0.79, 0.93]  rho = [0.71, 0.44, 0.55, 0.82]
       gBest Giữ   Lévy  DE           Lévy  gBest Giữ   Lévy

Gene 1: gbest → 0.20            Gene 1: Lévy → 0.75
Gene 2: giữ   → 0.12            Gene 2: gbest → 0.28
Gene 3: Lévy  → 0.92            Gene 3: giữ   → 0.89
Gene 4: DE    → 0.61            Gene 4: Lévy  → 0.48

→ 2 solution MỚI hoàn toàn khác nhau
→ Decode ra routes khác nhau
→ Đa dạng offspring
```

Đây chính là nguồn **stochasticity** (tính ngẫu nhiên) của thuật toán. Cùng input nhưng mỗi lần chạy ra kết quả khác → khám phá nhiều vùng khác nhau.

---

### Tóm lại

```
ρ = số ngẫu nhiên U(0,1), sinh RIÊNG cho MỖI gene

Tại sao riêng?
  → Mỗi khách hàng cần chiến lược KHÁC NHAU
  → KH1 có thể cần đổi route (copy gbest)
  → KH2 có thể đang ổn (giữ nguyên)
  → KH3 có thể cần thử vị trí mới (Lévy/DE)
  
  Nếu tung chung → tất cả 124 KH cùng 1 nhánh → quá cứng nhắc
  Tung riêng → mỗi KH tự quyết → linh hoạt, đa dạng
```

---

**User**

copy gbest tức là sao nhỉ, giải thích cụ thể với code hiện tại của tôi 

---

**Cursor**

Giờ tôi trace toàn bộ luồng **từ chọn gbest đến copy gene**:

---

## Bước 1: gbest được chọn như nào?

```655:663:g:\vrptw-for-pisso\algorithm\inssso.py
                    if self.pref is not None:
                        gb_idx = select_gbest_asf(
                            obj_matrix, self.pref, pf_indices
                        )
                    else:
                        gb_idx = select_gbest(pf_indices, sde_vals)

                    gbest = self.population[gb_idx]
```

**`pf_indices`** = danh sách các cá thể thuộc **Front 0** (non-dominated).

Ví dụ quần thể 100 con, Front 0 có 15 con:

```
pf_indices = [3, 7, 12, 18, 25, 31, 42, 48, 55, 60, 67, 73, 80, 88, 95]
               ↑ 15 solutions tốt nhất (không ai dominate ai)
```

Hàm `select_gbest_asf` chọn 1 con từ 15 con này:

```147:169:g:\vrptw-for-pisso\algorithm\r_dominance.py
def select_gbest_asf(...):
    # Chọn ngẫu nhiên 2 ứng viên từ Front 0
    i1, i2 = np.random.choice(n, size=2, replace=False)
    idx1 = candidate_indices[i1]   # ví dụ: cá thể 12
    idx2 = candidate_indices[i2]   # ví dụ: cá thể 48

    # Tính ASF cho mỗi con (gần preference hơn = ASF thấp hơn)
    asf1 = pref.asf_augmented(objectives[idx1])  # ASF = 0.35
    asf2 = pref.asf_augmented(objectives[idx2])  # ASF = 0.52

    # Ai gần preference hơn thì thắng
    return idx1 if asf1 <= asf2 else idx2  # → cá thể 12 thắng
```

**Kết quả:** `gbest = population[12]` — cá thể **gần preference nhất** trong 2 ứng viên.

---

## Bước 2: "Copy gbest" nghĩa là gì?

```471:471:g:\vrptw-for-pisso\algorithm\inssso.py
        new_keys = np.where(rho <= self.cg, gbest.keys, xi.keys)
```

`np.where(điều_kiện, giá_trị_nếu_đúng, giá_trị_nếu_sai)` — xử lý **từng gene**:

```
x_i.keys   = [0.73, 0.12, 0.89, 0.45, 0.31]   ← keys hiện tại
gbest.keys = [0.20, 0.28, 0.91, 0.33, 0.47]   ← keys của solution tốt nhất
rho        = [0.32, 0.63, 0.41, 0.93, 0.15]   ← ngẫu nhiên mỗi gene
c_g = 0.5

Gene 1: rho=0.32 ≤ 0.5? CÓ  → lấy gbest.keys[1] = 0.20  ← COPY
Gene 2: rho=0.63 ≤ 0.5? KHÔNG → lấy xi.keys[2]    = 0.12  ← GIỮ
Gene 3: rho=0.41 ≤ 0.5? CÓ  → lấy gbest.keys[3] = 0.91  ← COPY
Gene 4: rho=0.93 ≤ 0.5? KHÔNG → lấy xi.keys[4]    = 0.45  ← GIỮ
Gene 5: rho=0.15 ≤ 0.5? CÓ  → lấy gbest.keys[5] = 0.47  ← COPY

new_keys = [0.20, 0.12, 0.91, 0.45, 0.47]
            copy  giữ   copy  giữ   copy
```

**"Copy gbest" = lấy con số của gbest đặt vào vị trí tương ứng.** Không phải copy toàn bộ, chỉ copy **từng gene** khi ρ ≤ c_g.

---

## Bước 3: Copy gene → Routes thay đổi thế nào?

```
TRƯỚC (x_i):
  keys     = [0.73, 0.12, 0.89, 0.45, 0.31]
               KH1   KH2   KH3   KH4   KH5
  argsort  → KH2(0.12), KH5(0.31), KH4(0.45), KH1(0.73), KH3(0.89)
  Thứ tự:    KH2 → KH5 → KH4 → KH1 → KH3
  Routes:    0→KH2→KH5→KH4→0 | 0→KH1→KH3→0


SAU (copy gene 1, 3, 5 từ gbest):
  keys     = [0.20, 0.12, 0.91, 0.45, 0.47]
               KH1   KH2   KH3   KH4   KH5
             (copy)       (copy)       (copy)
  argsort  → KH2(0.12), KH1(0.20), KH4(0.45), KH5(0.47), KH3(0.91)
  Thứ tự:    KH2 → KH1 → KH4 → KH5 → KH3
  Routes:    0→KH2→KH1→KH4→0 | 0→KH5→KH3→0
                    ↑              ↑
                 KH1 nhảy lên    KH5 đổi route
```

**Gene 1 (KH1):** key đổi từ 0.73 → 0.20 → KH1 nhảy từ vị trí thứ 4 lên thứ 2 → chuyển từ Route 2 sang Route 1

**Gene 5 (KH5):** key đổi từ 0.31 → 0.47 → KH5 tụt từ vị trí thứ 2 xuống thứ 4 → chuyển từ Route 1 sang Route 2

---

## Toàn bộ luồng bằng 1 hình

```
Quần thể 100 con
       │
       ▼
Front 0 = [cá thể 3, 7, 12, 18, ...]  (15 con non-dominated)
       │
       ▼
Binary tournament: cá thể 12 vs 48  (so ASF)
  ASF(12) = 0.35 < ASF(48) = 0.52
       │
       ▼
gbest = cá thể 12
  keys = [0.20, 0.28, 0.91, 0.33, 0.47, ...]  ← "bản đồ tốt nhất"
       │
       ▼
Xử lý cá thể i = 37:
  x_i.keys = [0.73, 0.12, 0.89, 0.45, 0.31, ...]

  Gene 1: ρ=0.32 ≤ 0.5 → COPY gbest → 0.73 trở thành 0.20
                           "KH1 đặt giống cách gbest đặt"

  Gene 2: ρ=0.63 > 0.5 → GIỮ x_i    → vẫn 0.12
                           "KH2 đang ổn rồi"

  Gene 3: ρ=0.41 ≤ 0.5 → COPY gbest → 0.89 trở thành 0.91
                           "KH3 đặt giống cách gbest đặt"
  ...
       │
       ▼
new_keys = [0.20, 0.12, 0.91, ...]
       │
       ▼
Decode → routes mới → evaluate Z₁..Z₅
```

**"Copy gbest" = với mỗi gene được chọn, thay số cũ bằng số tương ứng của solution tốt nhất gần preference nhất.** Điều này khiến khách hàng đó được **sắp xếp giống cách solution tốt nhất sắp xếp** → routes hướng về cấu trúc tốt.

---

**User**

ok tôi hiểu tổng thể rồi, đơn giản chỉ là tìm ra 1 tập best xong chọn 1 thằng tốt nhất trong đống best đó để làm chuẩn rồi dùng sso update đi biến đổi từng gen 1 với xác suất là P, dựa vào P để chọn 4 trong 4 cách biến đổi, và đồng thời dùng ALNS để sửa các solution, rồi cuối cùng phân chia hợp lý vào thằng A_conv và A_div đúng không

---

**Cursor**

Đúng chính xác. Tóm lại toàn bộ thuật toán chỉ có vậy:

```
1. Tìm Front 0 (tập best)
2. Chọn 1 gbest từ Front 0 (gần preference nhất)
3. Với mỗi cá thể:
   ├── 80%: SSO biến đổi từng gene (4 nhánh theo ρ)
   └── 20%: ALNS phá rồi sửa routes trực tiếp
4. Ai tốt thì sống, ai tệ thì chết (NDS + SDE chọn 100 từ 201)
5. Solutions tốt lưu vào A_conv (gần preference) + A_div (trải đều)
6. Lặp lại từ bước 1
```

Bạn hiểu đúng rồi.

---

**User**

lặp đến khi hết thời gian chạy thuật toán đúng không, hoặc tôi có thể quyết định xem nó loop bao nhiêu lần giống như thằng GA cho biết số lần lặp của quần thể

---

**Cursor**

Đúng, hiện tại dùng **thời gian**. Nhưng bạn hoàn toàn có thể đổi sang **số generation** nếu muốn.

### Code hiện tại: dừng theo thời gian

```617:621:g:\vrptw-for-pisso\algorithm\inssso.py
        while True:
            elapsed = time.time() - start
            if elapsed >= self.t_run:
                break
```

```11:11:g:\vrptw-for-pisso\config\params.yaml
  t_run: 60           # time limit per run (seconds)
```

Chạy **cho đến khi hết 60 giây**. Số generation là bao nhiêu tùy máy — máy nhanh được nhiều gen, máy chậm ít gen.

### Tại sao dùng thời gian thay vì số generation?

| | Theo thời gian (hiện tại) | Theo số generation (GA style) |
|---|---|---|
| **So sánh công bằng** | Mọi thuật toán chạy **cùng 60s** → công bằng | ALNS tốn gấp 10x/gen so với SSO → không công bằng |
| **Reviewer Q1** | Chấp nhận rộng rãi cho metaheuristic | Phải justify tại sao chọn con số đó |
| **Thực tế** | DM nói "tôi có 60 giây" → rõ ràng | DM không biết 1 generation mất bao lâu |

**Lý do chính:** iNSSSO có ALNS (tốn thời gian) và SSO (nhanh). Nếu dùng số generation, 1 gen ALNS tốn gấp nhiều lần 1 gen SSO → so sánh với NSGA-II (không có ALNS) sẽ **không công bằng**.

### Nếu muốn đổi sang số generation

Chỉ cần sửa 1 chỗ:

```python
# Hiện tại (thời gian):
while True:
    if time.time() - start >= self.t_run:
        break

# Đổi thành (số generation):
for generation in range(self.max_gen):
    ...
```

Và thêm `max_gen` vào `params.yaml`:

```yaml
algorithm:
  max_gen: 500       # số generation tối đa
  # t_run: 60        # comment out
```

**Nhưng không nên** cho bài báo Q1, vì reviewer sẽ hỏi "tại sao 500 mà không phải 300 hay 1000?" Còn 60 giây thì ai cũng hiểu.

---

**User**

NDS + SDE chọn 100 từ 201 dựa vào đoạn nào bạn có thể suy ra như này nhỉ

---

**Cursor**

Đây, toàn bộ luồng "chọn 100 từ 201":

---

### Bước 1: Gộp P + Q

```704:709:g:\vrptw-for-pisso\algorithm\inssso.py
            # ── Selection: NDS + SDE + Ref Dir niching ──
            merged = self.population + offspring
            merged_obj = np.array([s.objectives for s in merged])
            best_indices = select_best(merged_obj, self.n_sol, self.ref_dirs)

            self.population = [merged[i] for i in best_indices]
```

```
self.population = 100 con (P)
offspring = 100 con + 1 injected = 101 con (Q)

merged = 100 + 101 = 201 con
select_best(merged, n_select=100) → chọn 100 từ 201
```

---

### Bước 2: Bên trong `select_best` — 3 phase

```161:231:g:\vrptw-for-pisso\algorithm\crowding.py
def select_best(objectives, n_select=100, ref_dirs):
```

**Phase 1: Xếp hạng NDS → chia fronts**

```python
    fronts = fast_nondominated_sort(objectives)  # 201 con → chia thành fronts
    _, sde_vals = assign_rank_and_sde(objectives) # tính SDE cho tất cả
```

```
201 solutions phân thành:
  Front 0: [sol 3, 7, 12, 18, 25, ...]        = 20 con (non-dominated)
  Front 1: [sol 1, 5, 8, 20, 33, ...]         = 35 con
  Front 2: [sol 2, 9, 14, 22, ...]            = 45 con
  Front 3: [sol 4, 6, 11, ...]                = 50 con
  Front 4: [sol 10, 15, ...]                  = 51 con
```

**Phase 2: Lấp đầy từ Front 0 trở đi**

```python
    for rank, front in enumerate(fronts):
        if len(selected) + len(candidates) <= n_select:
            selected.extend(candidates)  # lấy hết front này
```

```
Cần chọn 100 con:

  Lấy hết Front 0 (20 con):  selected = 20   ← chưa đủ 100
  Lấy hết Front 1 (35 con):  selected = 55   ← chưa đủ 100
  Lấy hết Front 2 (45 con):  selected = 100  ← VỪA ĐỦ → dừng

  Front 3 (50 con): BỎ HẾT ❌
  Front 4 (51 con): BỎ HẾT ❌
```

**Phase 3: Nếu Front biên vượt quá → Niching + SDE phá tie**

Giả sử thay vì 45, Front 2 có 60 con:

```
  Lấy hết Front 0 (20 con):  selected = 20
  Lấy hết Front 1 (35 con):  selected = 55
  Front 2 (60 con):          cần thêm 100 - 55 = 45 con
                              nhưng có 60 → phải CHỌN 45 từ 60
```

Lúc này dùng **Niching + SDE** (dòng 202-228):

```python
            if ref_dirs is not None:
                # Gán mỗi solution vào reference direction gần nhất
                # Ưu tiên niche ít thành viên (least crowded)
                # Tie-break bằng SDE (cao hơn = cô lập hơn = ưu tiên)
                chosen = niching_selection(
                    front_indices=candidates,
                    n_select=n_remaining,     # 45
                    ref_dirs=ref_dirs,        # 210 hướng
                    sde_values=sde_vals,      # SDE mỗi con
                    existing_niche_counts=niche_counts,
                )
            else:
                # Fallback: sort SDE giảm dần, lấy 45 đầu
                candidates.sort(key=lambda i: -sde_vals[i])
                selected.extend(candidates[:n_remaining])
```

```
60 con trong Front 2, cần chọn 45:

  Niche A (hướng 1): 8 con → đã đông → chỉ giữ 3 (SDE cao nhất)
  Niche B (hướng 2): 2 con → vắng → giữ hết 2
  Niche C (hướng 3): 0 con → trống → ưu tiên cho con mới vào
  ...
  
  Kết quả: 45 con TRẢI ĐỀU trên các hướng reference
           15 con bị loại (ở chỗ đông + SDE thấp)
```

---

### Con số 201 đến từ đâu?

```
P (quần thể):     100 con    (cố định)
Q (offspring):
  ├── SSO path:    ~80 con   (80% × 100)
  ├── ALNS path:   ~20 con   (20% × 100)
  └── Injection:   1 con     (từ archive)
                   ─────────
  Q tổng:          101 con

merged = P + Q = 100 + 101 = 201 con
select 100 → 101 con BỊ LOẠI
```

---

### Tóm lại

```
201 con
  │
  ▼
NDS: chia thành Front 0, 1, 2, 3, ...
  │
  ▼
Lấy hết Front 0 → Front 1 → ... cho đến gần đủ 100
  │
  ▼
Front biên (vượt 100): Niching + SDE chọn ai ở ai đi
  │              ├── Niche vắng → ưu tiên giữ (diversity)
  │              └── SDE cao → ưu tiên giữ (cô lập)
  │
  ▼
100 con sống → P thế hệ mới
101 con chết (nhưng có thể vẫn sống trong archive)
```

---

**User**

giải thích chi tiết SDE và minh hoạ dễ hiểu 

---

**Cursor**

## SDE — Giải thích từ đầu, cực dễ hiểu

---

### Vấn đề cần giải quyết

Khi chọn 100 từ 201, có nhiều con cùng Front (cùng "giỏi"). Cần tiêu chí phụ: **ai ở chỗ đông thì loại, ai ở chỗ vắng thì giữ**.

SDE = **điểm cô lập** của mỗi solution. Cao = vắng = quý. Thấp = đông = loại.

---

### Tưởng tượng bản đồ 2D (đơn giản hóa từ 5 mục tiêu)

Giả sử 6 solutions trên Front 0, chỉ có 2 mục tiêu: Z₁ (số xe) và Z₂ (distance):

```
Z₂ (distance)
 ▲
 │
900│  A(3, 900)
 │
800│        B(5, 800)
 │           C(5, 780)    ← B và C rất gần nhau
700│
 │                    D(8, 650)
600│
 │                          E(10, 550)
500│
 │                                F(12, 500)
 └──────────────────────────────────────▶ Z₁ (số xe)
   3    5         8      10      12
```

Bằng mắt: **B và C đông** (gần nhau), **A và F vắng** (ở rìa). SDE sẽ cho ra đúng kết quả này.

---

### Bước 1: Chuẩn hóa (Eq. 24)

Đưa tất cả về [0, 1]:

```
Z₁: min=3, max=12  →  chuẩn hóa = (x - 3) / (12 - 3)
Z₂: min=500, max=900 → chuẩn hóa = (x - 500) / (900 - 500)

A: (3, 900)   → (0.00, 1.00)
B: (5, 800)   → (0.22, 0.75)
C: (5, 780)   → (0.22, 0.70)
D: (8, 650)   → (0.56, 0.38)
E: (10, 550)  → (0.78, 0.13)
F: (12, 500)  → (1.00, 0.00)
```

```
Z₂ (chuẩn hóa)
1.0│  A
   │
0.7│     B
   │     C     ← gần nhau
   │
0.4│          D
   │
0.1│               E
0.0│                    F
   └─────────────────────▶ Z₁ (chuẩn hóa)
  0.0  0.2  0.4  0.6  0.8  1.0
```

---

### Bước 2: Shift — BƯỚC THEN CHỐT (Eq. 25)

Khi tính khoảng cách từ **i** đến **j**:

```
shifted_{i,j,m} = max(f̂_m(j), f̂_m(i))
```

Nghĩa là: **nếu j tốt hơn i ở mục tiêu nào, đẩy j lên ngang bằng i ở mục tiêu đó**.

#### Ví dụ: Tính shifted cho cặp (B, C)

```
B = (0.22, 0.75)
C = (0.22, 0.70)    ← C tốt hơn B ở Z₂ (0.70 < 0.75)

shifted_{B,C} = (max(0.22, 0.22), max(0.70, 0.75))
              = (0.22, 0.75)
                       ↑ C bị đẩy LÊN ngang B ở Z₂

Hình dung:
  Trước shift:         Sau shift:
  B ●  (0.22, 0.75)    B ●  (0.22, 0.75)
  C ●  (0.22, 0.70)    C ▲  (0.22, 0.75)  ← đẩy lên ngang B
                              C đè lên B!
```

#### Ví dụ: Tính shifted cho cặp (A, D)

```
A = (0.00, 1.00)
D = (0.56, 0.38)    ← D tốt hơn A ở Z₂, A tốt hơn D ở Z₁

shifted_{A,D} = (max(0.56, 0.00), max(0.38, 1.00))
              = (0.56, 1.00)
                 ↑ D đẩy sang phải    ↑ giữ nguyên (A đã tệ hơn)

Hình dung:
  Trước shift:              Sau shift:
  A ●  (0.00, 1.00)         A ●  (0.00, 1.00)
         D ●  (0.56, 0.38)        D ▲  (0.56, 1.00)  ← đẩy lên
                                   D ở xa A
```

---

### Bước 3: Tính khoảng cách (Eq. 26)

```
d_SDE(i, j) = ‖shifted_{i,j} - f̂(i)‖
            = khoảng cách Euclid từ i đến j (sau khi shift)
```

#### Tính cho mọi cặp liên quan đến B và C:

**d_SDE(B, C):**

```
B = (0.22, 0.75),  C = (0.22, 0.70)
shifted_{B,C} = (0.22, 0.75)    ← C đẩy lên ngang B

d_SDE(B, C) = ‖(0.22, 0.75) - (0.22, 0.75)‖ = 0.0
               shifted          B
               BẰNG 0! C đè lên B.
```

**d_SDE(C, B):**

```
C = (0.22, 0.70),  B = (0.22, 0.75)
shifted_{C,B} = (max(0.22, 0.22), max(0.75, 0.70)) = (0.22, 0.75)

d_SDE(C, B) = ‖(0.22, 0.75) - (0.22, 0.70)‖ = 0.05
               shifted          C
               Rất nhỏ! B ở gần C.
```

**d_SDE(A, B):**

```
A = (0.00, 1.00),  B = (0.22, 0.75)
shifted_{A,B} = (max(0.22, 0.00), max(0.75, 1.00)) = (0.22, 1.00)

d_SDE(A, B) = ‖(0.22, 1.00) - (0.00, 1.00)‖ = 0.22
               → A cách B một khoảng đáng kể
```

**d_SDE(A, F):**

```
A = (0.00, 1.00),  F = (1.00, 0.00)
shifted_{A,F} = (max(1.00, 0.00), max(0.00, 1.00)) = (1.00, 1.00)

d_SDE(A, F) = ‖(1.00, 1.00) - (0.00, 1.00)‖ = 1.00
               → A cách F RẤT XA
```

---

### Bước 4: SDE = khoảng cách đến hàng xóm GẦN NHẤT (Eq. 27)

```
SDE(i) = min_{j≠i} d_SDE(i, j)
```

Tính cho từng solution:

```
SDE(A) = min(d(A,B), d(A,C), d(A,D), d(A,E), d(A,F))
       = min(0.22, 0.22, 0.56, 0.78, 1.00)
       = 0.22    ← hàng xóm gần nhất là B, cách 0.22

SDE(B) = min(d(B,A), d(B,C), d(B,D), d(B,E), d(B,F))
       = min(0.25, 0.0, 0.34, 0.56, 0.78)
       = 0.0     ← C đè lên B! khoảng cách = 0

SDE(C) = min(d(C,A), d(C,B), d(C,D), d(C,E), d(C,F))
       = min(0.30, 0.05, 0.34, 0.57, 0.78)
       = 0.05    ← B ở rất gần

SDE(D) = min(d(D,A), d(D,B), d(D,C), d(D,E), d(D,F))
       = min(0.76, 0.47, 0.42, 0.31, 0.52)
       = 0.31    ← hàng xóm gần nhất là E

SDE(E) = min(d(E,A), d(E,B), d(E,C), d(E,D), d(E,F))
       = min(1.02, 0.76, 0.72, 0.31, 0.25)
       = 0.25    ← hàng xóm gần nhất là F

SDE(F) = min(d(F,A), d(F,B), d(F,C), d(F,D), d(F,E))
       = min(1.41, 1.02, 0.98, 0.52, 0.25)
       = 0.25    ← hàng xóm gần nhất là E
```

---

### Kết quả xếp hạng

```
SDE(D) = 0.31   ← VẮng nhất → ƯU TIÊN GIỮ ★★★
SDE(E) = 0.25   ← Vắng      → ƯU TIÊN GIỮ ★★
SDE(F) = 0.25   ← Vắng      → ƯU TIÊN GIỮ ★★
SDE(A) = 0.22   ← Khá vắng  → GIỮ ★
SDE(C) = 0.05   ← ĐÔNG      → LOẠI ✗
SDE(B) = 0.00   ← ĐÔNG NHẤT → LOẠI ĐẦU TIÊN ✗✗
```

Nếu cần loại 2 con → loại **B** (SDE=0.0) và **C** (SDE=0.05).

```
Trước:                           Sau khi loại B, C:

Z₂ ▲                            Z₂ ▲
   │  A                             │  A
   │     B                          │
   │     C  ← đông, loại           │
   │          D                     │          D        ← TRẢI ĐỀU!
   │               E                │               E
   │                    F           │                    F
   └──────────────────▶ Z₁         └──────────────────▶ Z₁
```

---

### Tại sao Shift quan trọng?

Không shift (Crowding Distance thường): chỉ đo khoảng cách thuần.

Có shift: **phạt thêm solution bị dominated**.

```
Giả sử thêm solution G bị A dominate:

A = (0.00, 1.00)
G = (0.10, 1.00)    ← G tệ hơn A ở Z₁, bằng A ở Z₂

Không shift:
  d(G, A) = ‖(0.00, 1.00) - (0.10, 1.00)‖ = 0.10
  → G cách A = 0.10 → có thể sống

Có shift:
  shifted_{G,A} = (max(0.00, 0.10), max(1.00, 1.00)) = (0.10, 1.00)
                   ↑ A tốt hơn G → A giữ nguyên, không bị đẩy

  d_SDE(G, A) = ‖(0.10, 1.00) - (0.10, 1.00)‖ = 0.0
                 shifted          G

  SDE(G) = 0.0 → LOẠI ĐẦU TIÊN
```

**A đè lên G** → khoảng cách = 0 → G bị loại. Shift tự động phạt solution bị dominated mà không cần check dominance riêng.

---

### Tóm lại SDE bằng 3 câu

> **1. Chuẩn hóa** mọi mục tiêu về [0,1]
>
> **2. Shift:** nếu hàng xóm tốt hơn tôi → giả vờ nó đè lên tôi → khoảng cách giảm
>
> **3. SDE = khoảng cách đến hàng xóm gần nhất (sau shift).** Thấp = đông hoặc bị đè → loại. Cao = vắng → giữ.

---

**User**

ví dụ có 5 thằng như vậy thì vòng lặp phải tính tổ hợp tất cả bao nhiêu lần

---

**Cursor**

## Với 5 solutions → tính bao nhiêu lần?

### Mỗi cặp (i, j) cần tính 1 lần d_SDE

```
5 solutions: A, B, C, D, E

Ma trận khoảng cách (5 × 5):

         j=A      j=B      j=C      j=D      j=E
i=A  [   -     d(A,B)   d(A,C)   d(A,D)   d(A,E) ]
i=B  [ d(B,A)    -      d(B,C)   d(B,D)   d(B,E) ]
i=C  [ d(C,A)  d(C,B)     -      d(C,D)   d(C,E) ]
i=D  [ d(D,A)  d(D,B)   d(D,C)     -      d(D,E) ]
i=E  [ d(E,A)  d(E,B)   d(E,C)   d(E,D)     -    ]

Đường chéo = bỏ (không tính khoảng cách đến chính mình)
```

**Lưu ý:** d_SDE(A,B) ≠ d_SDE(B,A) vì shift **phụ thuộc ai là i, ai là j**.

```
d_SDE(B, C): C tốt hơn B ở Z₂ → C đè lên B → d = 0.0
d_SDE(C, B): B tệ hơn C ở Z₂ → B bị đẩy lên → d = 0.05

Không giống nhau! → phải tính CẢ HAI CHIỀU
```

### Số lần tính

```
N solutions → N × (N - 1) cặp có thứ tự

N = 5:   5 × 4 = 20 lần tính d_SDE
N = 100: 100 × 99 = 9,900 lần
N = 201: 201 × 200 = 40,200 lần
```

Mỗi lần tính d_SDE cần xử lý **M mục tiêu** (shift + Euclid distance):

```
Tổng phép tính = N × (N-1) × M

N=5,   M=5:    5 × 4 × 5     = 100 phép tính
N=100, M=5:    100 × 99 × 5  = 49,500 phép tính
N=201, M=5:    201 × 200 × 5 = 201,000 phép tính
```

### Tại sao không chậm? → Vectorised

Code không dùng vòng lặp. Dùng NumPy broadcasting tính **tất cả cùng lúc**:

```python
# Thay vì:
for i in range(N):          # 201 lần
    for j in range(N):      # × 201 lần
        for m in range(M):  # × 5 lần = 201,000 vòng lặp Python (CHẬM)

# Code thực tế:
norm_i = norm[:, None, :]   # shape (201, 1, 5)
norm_j = norm[None, :, :]   # shape (1, 201, 5)
shifted = np.maximum(norm_j, norm_i)  # shape (201, 201, 5) — 1 lệnh duy nhất
```

1 lệnh NumPy xử lý **201 × 201 × 5 = 201,000 phép tính song song** trên CPU → nhanh gấp 100-1000x so với vòng lặp Python.

### Tóm lại

```
N solutions, M mục tiêu:

Số cặp:      N × (N-1)        = N² - N
Mỗi cặp:    M phép shift + 1 phép Euclid
Tổng:        O(N² × M)

N=5:   20 cặp      → trivial
N=201: 40,200 cặp  → ~0.01 giây (vectorised)
```

---

**User**

như tôi hiểu thì ví dụ xét A thì đều phải tính tất cả các cặp A - B, A-C, A-D, A-E à

---

**Cursor**

Đúng. Để biết SDE(A), phải tính **A với tất cả** rồi lấy **min**:

```
SDE(A) = min( d(A,B), d(A,C), d(A,D), d(A,E) )
              ↑        ↑        ↑        ↑
           tính cả 4 cặp, rồi chọn nhỏ nhất
```

Vì SDE = khoảng cách đến **hàng xóm gần nhất**. Không biết ai gần nhất cho đến khi tính hết.

```
Ví dụ:
  d(A,B) = 0.22
  d(A,C) = 0.22
  d(A,D) = 0.56
  d(A,E) = 0.78

  SDE(A) = min(0.22, 0.22, 0.56, 0.78) = 0.22
                ↑
           B là hàng xóm gần nhất của A
```

Tương tự cho **mọi solution khác**:

```
SDE(A) = min(d(A,B), d(A,C), d(A,D), d(A,E))  → 4 phép tính
SDE(B) = min(d(B,A), d(B,C), d(B,D), d(B,E))  → 4 phép tính
SDE(C) = min(d(C,A), d(C,B), d(C,D), d(C,E))  → 4 phép tính
SDE(D) = min(d(D,A), d(D,B), d(D,C), d(D,E))  → 4 phép tính
SDE(E) = min(d(E,A), d(E,B), d(E,C), d(E,D))  → 4 phép tính
                                                ──────────────
                                                 5 × 4 = 20 lần tổng cộng
```

Chỉ vậy thôi. Tính hết → sort SDE → ai thấp nhất bị loại trước.

---

**User**

chỉ ra đoạn code thực hiện 4 bước này

---

**Cursor**

Đây, toàn bộ SDE trong **1 hàm, 20 dòng code**. Mapping từng dòng vào 4 bước:

---

### Bước 1 — Chuẩn hóa (Eq. 24)

```53:57:g:\vrptw-for-pisso\algorithm\crowding.py
    ideal = objectives.min(axis=0)        # tìm min mỗi mục tiêu
    nadir = objectives.max(axis=0)        # tìm max mỗi mục tiêu
    ranges = nadir - ideal                # khoảng dao động
    ranges = np.where(ranges < 1e-10, 1.0, ranges)  # tránh chia cho 0
    norm = (objectives - ideal) / ranges  # chuẩn hóa về [0, 1]
```

```
Ví dụ 5 solutions, 2 mục tiêu:

objectives:                    norm (sau chuẩn hóa):
  A: (3, 900)                    A: (0.00, 1.00)
  B: (5, 800)                    B: (0.22, 0.75)
  C: (5, 780)                    C: (0.22, 0.70)
  D: (8, 650)                    D: (0.56, 0.38)
  E: (10, 550)                   E: (0.78, 0.13)

ideal = (3, 550)    nadir = (10, 900)    ranges = (7, 350)
```

---

### Bước 2 — Shift (Eq. 25)

```59:62:g:\vrptw-for-pisso\algorithm\crowding.py
    norm_i = norm[:, np.newaxis, :]   # (N, 1, M)  ← mỗi hàng = 1 solution i
    norm_j = norm[np.newaxis, :, :]   # (1, N, M)  ← mỗi cột = 1 solution j
    shifted = np.maximum(norm_j, norm_i)  # (N, N, M) ← TẤT CẢ cặp cùng lúc
```

```
norm_i shape (5, 1, 2):          norm_j shape (1, 5, 2):
  A: [[0.00, 1.00]]               [A, B, C, D, E] theo cột
  B: [[0.22, 0.75]]
  C: [[0.22, 0.70]]
  D: [[0.56, 0.38]]
  E: [[0.78, 0.13]]

np.maximum → broadcast → shape (5, 5, 2):

shifted[i,j] = max(norm_j, norm_i)  cho MỌI cặp (i,j) CÙNG LÚC

  shifted[B,C] = (max(0.22,0.22), max(0.70,0.75)) = (0.22, 0.75)
  shifted[A,D] = (max(0.56,0.00), max(0.38,1.00)) = (0.56, 1.00)
  ... 25 cặp tính SONG SONG trong 1 lệnh
```

---

### Bước 3 — Distance (Eq. 26)

```63:64:g:\vrptw-for-pisso\algorithm\crowding.py
    diff = shifted - norm_i               # (N, N, M)  ← hiệu
    dists = np.sqrt(np.sum(diff ** 2, axis=2))  # (N, N) ← Euclid distance
```

```
diff[B,C] = shifted[B,C] - norm[B]
          = (0.22, 0.75) - (0.22, 0.75)
          = (0.00, 0.00)

dists[B,C] = √(0² + 0²) = 0.0    ← C đè lên B

diff[A,D] = shifted[A,D] - norm[A]
          = (0.56, 1.00) - (0.00, 1.00)
          = (0.56, 0.00)

dists[A,D] = √(0.56² + 0²) = 0.56    ← A cách D khá xa
```

Kết quả: ma trận 5×5 khoảng cách:

```
dists:    A      B      C      D      E
   A  [  -    0.22   0.22   0.56   0.78 ]
   B  [ 0.25   -     0.00   0.34   0.56 ]
   C  [ 0.30  0.05    -     0.34   0.57 ]
   D  [ 0.76  0.47   0.42    -     0.31 ]
   E  [ 1.02  0.76   0.72   0.31    -   ]
```

---

### Bước 4 — SDE = min mỗi hàng (Eq. 27)

```66:69:g:\vrptw-for-pisso\algorithm\crowding.py
    np.fill_diagonal(dists, np.inf)   # đường chéo = ∞ (bỏ qua chính mình)
    sde = dists.min(axis=1)           # min mỗi HÀNG = hàng xóm gần nhất
```

```
Sau fill_diagonal:

dists:    A      B      C      D      E
   A  [  ∞    0.22   0.22   0.56   0.78 ]  → min = 0.22 (B hoặc C)
   B  [ 0.25   ∞     0.00   0.34   0.56 ]  → min = 0.00 (C đè)
   C  [ 0.30  0.05    ∞     0.34   0.57 ]  → min = 0.05 (B gần)
   D  [ 0.76  0.47   0.42    ∞     0.31 ]  → min = 0.31 (E gần)
   E  [ 1.02  0.76   0.72   0.31    ∞   ]  → min = 0.31 (D gần)

sde = [0.22, 0.00, 0.05, 0.31, 0.31]
        A      B      C      D      E
              LOẠI↑  LOẠI↑        GIỮ↑  GIỮ↑
```

---

### Tóm lại: 4 bước → 4 nhóm code

```
Bước 1 (chuẩn hóa):  dòng 53-57  →  norm = (obj - ideal) / ranges
Bước 2 (shift):       dòng 59-62  →  shifted = np.maximum(norm_j, norm_i)
Bước 3 (distance):    dòng 63-64  →  dists = √Σ(shifted - norm_i)²
Bước 4 (min):         dòng 66-69  →  sde = dists.min(axis=1)
```

Cả 4 bước **không có vòng lặp for nào**. Tất cả dùng NumPy broadcasting → 1 lệnh = xử lý tất cả cặp cùng lúc.

---

**User**

thôi tóm lại là thế này có N phần tử thì shift 1 phần tử với N-1 phần tử còn lại để tìm ra N-1 thằng mới, rồi tiếp theo tính khoảng cách từ N-1 thằng mới đó tới thằng 1 ban đầu, rồi cuối cùng lấy min khoảng cách của chúng đúng chưa

---

**Cursor**

Đúng 100%. Chỉ vậy thôi.

```
Xét A:
  Shift A với B → B' → tính khoảng cách A↔B' = 0.22
  Shift A với C → C' → tính khoảng cách A↔C' = 0.22
  Shift A với D → D' → tính khoảng cách A↔D' = 0.56
  Shift A với E → E' → tính khoảng cách A↔E' = 0.78

  SDE(A) = min(0.22, 0.22, 0.56, 0.78) = 0.22

Lặp lại cho B, C, D, E → xong.
```

Shift chỉ có 1 việc: nếu thằng kia tốt hơn thì **đẩy nó lên ngang mình** → khoảng cách bị rút ngắn → bị phạt.

---

**User**

5.4 Algorithm 6: Assign Rank and Density
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm 6: NDS + SDE + Niching Selection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Population P, objectives F, target size N, ref_dirs W
Output: Selected population P' of size N
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1: // Phase 1: Non-dominated Sorting
 2: {F₀, F₁, ...} ← FastNDS(F)    // Eq. 20-23
 3:
 4: // Phase 2: Fill fronts until overflow
 5: P' ← ∅
 6: l ← 0  // front index
 7: while |P' ∪ F_l| ≤ N do
 8:     P' ← P' ∪ F_l
 9:     l ← l + 1
10: end while
11:
12: // Phase 3: Boundary front selection via Niching
13: remaining ← N - |P'|
14: if remaining > 0 then
15:     // Normalize objectives
16:     F_norm ← normalize(F[P' ∪ F_l])   // Eq. 24
17:     // Associate to reference directions
18:     assoc ← associate(F_norm, W)        // Eq. 32
19:     // Compute SDE for F_l members
20:     sde ← VectorisedSDE(F[F_l])         // Eq. 24-27
21:     // Niching selection
22:     selected ← NichingSelect(F_l, assoc, sde, remaining)
23:     P' ← P' ∪ selected
24: end if
25:
26: return P'
thế tiếp theo giải thích thằng này xem nào

---

**Cursor**

Giờ giải thích toàn bộ Algorithm 6 bằng ví dụ cụ thể:

---

## Bài toán: Chọn 10 từ 16 solutions

```
Có 16 solutions, cần giữ 10, loại 6.
5 mục tiêu, 6 reference directions (đơn giản hóa).
```

---

## Phase 1: NDS — Chia fronts

```python
fronts = fast_nondominated_sort(objectives)  # dòng 178
```

```
16 solutions → chia thành fronts:

Front 0: [s1, s2, s3, s4, s5]         = 5 con (không ai dominate ai)
Front 1: [s6, s7, s8, s9, s10, s11]   = 6 con
Front 2: [s12, s13, s14, s15, s16]    = 5 con
```

---

## Phase 2: Lấp đầy từ Front 0

```python
if len(selected) + len(candidates) <= n_select:   # dòng 196
    selected.extend(candidates)                    # dòng 197
```

```
Cần 10 con:

Lấy hết Front 0 (5 con):  selected = [s1,s2,s3,s4,s5]  = 5 ← chưa đủ 10
Thử Front 1 (6 con):      5 + 6 = 11 > 10  ← VƯỢT QUÁ!

→ Front 1 là FRONT BIÊN
→ Cần chọn 10 - 5 = 5 con từ 6 con trong Front 1
→ Phải loại 1 con
```

---

## Phase 3: Niching — Chọn 5 từ 6 trên Front biên

Đây là phần phức tạp nhất. 3 bước:

### Bước 3a: Gán mỗi solution vào reference direction gần nhất

```python
front_assignments = associate_to_directions(front_norm, ref_dirs)  # dòng 250
```

Tưởng tượng 6 reference directions như **6 tia** từ gốc tọa độ:

```
         Z₂
         ▲
         │  ↗ dir2
         │↗ dir1
    dir3 ╱──────→ dir4   Z₁
        ╱↘ dir5
       ↙  ↘ dir6

Mỗi solution gán vào tia GẦN NHẤT (theo khoảng cách vuông góc):
```

```python
# Với mỗi solution i, với mỗi direction j:
proj_scalar = np.dot(p, d) / np.dot(d, d)  # chiếu p lên d   (dòng 200)
proj = proj_scalar * d                       # điểm chiếu       (dòng 201)
perp_dist = np.linalg.norm(p - proj)         # khoảng cách ⊥    (dòng 202)
```

```
Kết quả:
  s6  → dir1  (gần dir1 nhất)
  s7  → dir1  (cũng gần dir1)
  s8  → dir3  (gần dir3 nhất)
  s9  → dir4  (gần dir4 nhất)
  s10 → dir4  (cũng gần dir4)
  s11 → dir6  (gần dir6 nhất)
```

### Bước 3b: Đếm mỗi niche có bao nhiêu con

```
Niche counts (gồm cả 5 con từ Front 0 đã chọn):

  dir1: 2 con (s6, s7)     + 1 từ Front 0 = 3 ← ĐÔNG
  dir2: 0 con               + 1 từ Front 0 = 1
  dir3: 1 con (s8)          + 0 từ Front 0 = 1
  dir4: 2 con (s9, s10)     + 2 từ Front 0 = 4 ← ĐÔNG NHẤT
  dir5: 0 con               + 0 từ Front 0 = 0 ← TRỐNG
  dir6: 1 con (s11)         + 1 từ Front 0 = 2
```

### Bước 3c: Lặp chọn từng con — ưu tiên niche vắng nhất

```python
for _ in range(n_select):                          # dòng 258
    # Tìm niche ít thành viên nhất
    min_count = ...
    candidate_niches = {niche có count = min_count}

    # Trong niche đó, chọn con có SDE phù hợp nhất
    best_r = con có SDE thấp nhất trong candidate_niches
    
    selected.append(best_r)
    niche_counts[niche của best_r] += 1            # dòng 289
```

**Vòng 1:** Niche vắng nhất = dir5 (0 con). Nhưng không có ai từ Front 1 thuộc dir5 → bỏ qua, xét dir3 (1 con) → chọn **s8**.

```
dir3: 1 → 2.  Đã chọn: [s8]
```

**Vòng 2:** Niche vắng nhất = dir2 (1 con) hoặc dir3 (2 con) hoặc dir6 (2 con). dir2 vắng nhất nhưng không ai thuộc dir2 → xét dir6 → chọn **s11**.

```
dir6: 2 → 3.  Đã chọn: [s8, s11]
```

**Vòng 3:** dir1 (3 con) có s6 và s7. Chọn con có **SDE phù hợp** → giả sử **s6** (SDE cao hơn = cô lập hơn).

```
dir1: 3 → 4.  Đã chọn: [s8, s11, s6]
```

**Vòng 4:** dir4 (4 con) có s9 và s10. Chọn **s9**.

```
dir4: 4 → 5.  Đã chọn: [s8, s11, s6, s9]
```

**Vòng 5:** Còn s7 (dir1, count=4) và s10 (dir4, count=5). dir1 vắng hơn → chọn **s7**.

```
Đã chọn: [s8, s11, s6, s9, s7]
```

**s10 bị LOẠI** — ở niche đông nhất (dir4 đã có 5 con).

---

## Kết quả cuối cùng

```
TRƯỚC (16 con):                   SAU (10 con):

  Front 0: s1,s2,s3,s4,s5  ✓ hết   5 con từ Front 0
  Front 1: s6,s7,s8,s9,    ✓       + 5 con từ Front 1
           s10,             ✗ LOẠI   (s10 bị loại vì ở niche đông nhất)
           s11              ✓
  Front 2: s12-s16          ✗ hết   Front 2 toàn bộ bị loại
```

---

## Tóm lại Algorithm 6

```
Phase 1: Chia fronts (NDS)
  → Front 0 tốt nhất, Front 1 kém hơn, ...

Phase 2: Lấy hết front tốt cho đến khi gần đủ
  → Front 0 lấy hết, Front 1 lấy hết, ... cho đến front biên

Phase 3: Front biên có nhiều hơn cần → Niching chọn ai ở ai đi
  a) Gán mỗi con vào reference direction gần nhất
  b) Ưu tiên giữ con ở niche VẮNG (đảm bảo trải đều)
  c) Tie-break bằng SDE (cô lập hơn = giữ)
  → Con ở niche ĐÔNG bị loại trước
```

Logic đơn giản: **Front tốt giữ hết. Front biên thì giữ ai trải đều nhất.**

---

**User**

tôi cần bạn giải thích chi tiết cái phase 1

---

**Cursor**

## Phase 1: Non-dominated Sorting — Giải thích chi tiết

---

### Bước 1: Tính ma trận dominance (ai thắng ai)

```15:35:g:\vrptw-for-pisso\algorithm\nondominated.py
def dominates_vec(objectives):
    a = objectives[:, np.newaxis, :]   # (N, 1, M)
    b = objectives[np.newaxis, :, :]   # (1, N, M)

    leq = a <= b            # a không tệ hơn b ở MỌI mục tiêu?
    lt  = a < b             # a tốt hơn b ở ÍT NHẤT 1 mục tiêu?

    all_leq = leq.all(axis=2)    # AND trên M mục tiêu
    any_lt  = lt.any(axis=2)     # OR trên M mục tiêu

    return all_leq & any_lt      # a dominate b
```

Ví dụ 5 solutions, 2 mục tiêu (minimize cả hai):

```
s1: (3, 900)    s2: (5, 800)    s3: (5, 780)    s4: (8, 650)    s5: (10, 900)
```

Xét từng cặp:

```
s1 vs s2: s1=(3,900), s2=(5,800)
  all_leq: 3≤5? CÓ.  900≤800? KHÔNG → all_leq = KHÔNG → s1 KHÔNG dominate s2

s1 vs s5: s1=(3,900), s5=(10,900)
  all_leq: 3≤10? CÓ.  900≤900? CÓ  → all_leq = CÓ
  any_lt:  3<10? CÓ                  → any_lt = CÓ
  → s1 DOMINATE s5 ✓

s2 vs s3: s2=(5,800), s3=(5,780)
  all_leq: 5≤5? CÓ.  800≤780? KHÔNG → s2 KHÔNG dominate s3

s3 vs s2: s3=(5,780), s2=(5,800)
  all_leq: 5≤5? CÓ.  780≤800? CÓ   → all_leq = CÓ
  any_lt:  780<800? CÓ               → any_lt = CÓ
  → s3 DOMINATE s2 ✓

s4 vs s5: s4=(8,650), s5=(10,900)
  all_leq: 8≤10? CÓ.  650≤900? CÓ  → all_leq = CÓ
  any_lt:  8<10? CÓ                  → any_lt = CÓ
  → s4 DOMINATE s5 ✓
```

Kết quả ma trận 5×5:

```
dom[i,j] = True nếu i dominate j

        s1     s2     s3     s4     s5
s1  [   -    False  False  False   TRUE  ]   s1 dominate s5
s2  [ False    -    False  False  FALSE  ]   s2 không dominate ai
s3  [ False  TRUE     -    False  FALSE  ]   s3 dominate s2
s4  [ False  False  False    -    TRUE   ]   s4 dominate s5
s5  [ False  False  False  False    -    ]   s5 không dominate ai
```

---

### Bước 2: Đếm mỗi solution bị bao nhiêu thằng dominate

```58:59:g:\vrptw-for-pisso\algorithm\nondominated.py
    domination_count = dom.sum(axis=0)   # cộng theo CỘT
```

```
Cộng mỗi CỘT của ma trận:

        s1    s2    s3    s4    s5
s1  [   -     0     0     0     1  ]
s2  [   0     -     0     0     0  ]
s3  [   0     1     -     0     0  ]
s4  [   0     0     0     -     1  ]
s5  [   0     0     0     0     -  ]
      ────  ────  ────  ────  ────
count: 0     1     0     0     2

s1: 0 thằng dominate nó → FRONT 0 ★
s2: 1 thằng dominate nó (s3) → chưa phải front 0
s3: 0 thằng dominate nó → FRONT 0 ★
s4: 0 thằng dominate nó → FRONT 0 ★
s5: 2 thằng dominate nó (s1, s4) → chắc chắn không front 0
```

---

### Bước 3: Tìm ai dominate ai

```61:64:g:\vrptw-for-pisso\algorithm\nondominated.py
    dominated_set = [[] for _ in range(n)]
    for i in range(n):
        dominated_set[i] = np.where(dom[i])[0].tolist()
```

```
dominated_set[s1] = [s5]       s1 dominate s5
dominated_set[s2] = []         s2 không dominate ai
dominated_set[s3] = [s2]       s3 dominate s2
dominated_set[s4] = [s5]       s4 dominate s5
dominated_set[s5] = []         s5 không dominate ai
```

---

### Bước 4: Xây Front 0

```66:72:g:\vrptw-for-pisso\algorithm\nondominated.py
    current_front = np.where(domination_count == 0)[0].tolist()
    fronts.append(current_front)
```

```
domination_count == 0 ở vị trí nào?
  s1: count=0 ✓
  s3: count=0 ✓
  s4: count=0 ✓

Front 0 = [s1, s3, s4]
```

Hình dung:

```
Z₂ ▲
900│  s1●            ○s5   ← s5 bị s1 và s4 dominate
   │
800│      ○s2              ← s2 bị s3 dominate
780│      ●s3
   │
650│            ●s4
   └─────────────────▶ Z₁
   3    5       8    10

● = Front 0 (không ai dominate)
○ = bị dominate (front sau)
```

---

### Bước 5: Xây Front 1, 2, ... (lặp)

```74:84:g:\vrptw-for-pisso\algorithm\nondominated.py
    while fronts[-1]:
        next_front = []
        for p in fronts[-1]:          # với mỗi thằng trong front hiện tại
            for q in dominated_set[p]: # xét những thằng nó dominate
                domination_count[q] -= 1     # giảm count đi 1
                if domination_count[q] == 0: # nếu hết ai dominate → front mới
                    next_front.append(q)
        if next_front:
            fronts.append(next_front)
```

**Vòng 1:** Xử lý Front 0 = [s1, s3, s4]

```
Xét s1: dominated_set = [s5]
  domination_count[s5] = 2 - 1 = 1    (vẫn còn s4 dominate s5)

Xét s3: dominated_set = [s2]
  domination_count[s2] = 1 - 1 = 0    → s2 VÀO FRONT 1 ✓

Xét s4: dominated_set = [s5]
  domination_count[s5] = 1 - 1 = 0    → s5 VÀO FRONT 1 ✓

Front 1 = [s2, s5]
```

**Vòng 2:** Xử lý Front 1 = [s2, s5]

```
Xét s2: dominated_set = []  → không ai
Xét s5: dominated_set = []  → không ai

next_front = rỗng → DỪNG
```

---

### Kết quả cuối cùng

```
Front 0: [s1, s3, s4]   ← tốt nhất, không ai dominate
Front 1: [s2, s5]        ← bị front 0 dominate

Z₂ ▲
900│  s1(F0)          s5(F1)
   │
800│      s2(F1)
780│      s3(F0)
   │
650│            s4(F0)
   └─────────────────▶ Z₁
```

---

### Tóm lại Phase 1

```
Bước 1: So TỪNG CẶP → ai dominate ai (ma trận N×N)
Bước 2: Đếm mỗi solution bị bao nhiêu thằng dominate
Bước 3: Count = 0 → Front 0
Bước 4: "Xóa" Front 0, giảm count → ai count = 0 → Front 1
Bước 5: Lặp lại → Front 2, 3, ...

Đơn giản: bóc lớp vỏ. Lớp ngoài = Front 0. Bóc ra → lớp tiếp = Front 1. Bóc tiếp → Front 2...
```

---

**User**

thế tóm lại SDE có ý nghĩa gì ở trong này

---

**Cursor**

SDE đóng **3 vai trò** trong thuật toán:

### 1. Chọn ai sống ai chết ở Front biên (Algorithm 6 - Phase 3)

```
Cần chọn 5 từ 6 con trong Front 1.
Niching đã chọn niche vắng nhất.
Nhưng cùng 1 niche có 2 con → chọn ai?

  s6: SDE = 0.31 (cô lập)  → GIỮ ✓
  s7: SDE = 0.05 (đông)    → LOẠI ✗
```

### 2. Pruning A_div khi quá 200 (Eq. 56)

```
A_div có 201 con, cần loại 1:

  Tính SDE cho 201 con
  Loại con có SDE THẤP NHẤT (ở chỗ đông nhất)
  → A_div luôn trải đều, không tụ cục bộ
```

### 3. Chọn gbest (khi không có preference)

```
Front 0 có 15 con, cần chọn 1 làm gbest:

  Binary tournament: s12 vs s48
  SDE(s12) = 0.45 > SDE(s48) = 0.22
  → s12 thắng (cô lập hơn = khám phá tốt hơn)
```

---

### Một câu duy nhất

> **SDE = thước đo "solution này có bị thừa không?"**
> Thấp = thừa → loại. Cao = quý → giữ.

Cứ chỗ nào cần quyết định ai ở ai đi mà NDS không phân biệt được (cùng Front), thì SDE là người phán xử.

---

**User**

thế là bản chất vẫn cần phải có NDS đúng không, mà NDS thì thường chọn được ít, nên mới cần SDE để chọn thêm

---

**Cursor**

Đúng chính xác. NDS **chia nhóm**, SDE **chọn trong nhóm**.

```
NDS:  201 con → Front 0 (20 con) | Front 1 (35 con) | Front 2 (146 con)
                     ↑                    ↑                    ↑
                  GIỮ HẾT            GIỮ HẾT           CẦN CHỌN/LOẠI

Cần 100 con:
  Front 0: 20 con → lấy hết (NDS quyết định)
  Front 1: 35 con → lấy hết (NDS quyết định)
  Front 2: cần 45 từ 146 → SDE + Niching quyết định
```

NDS chỉ nói **"nhóm này tốt hơn nhóm kia"**, nhưng **trong cùng 1 nhóm thì tất cả ngang nhau** — NDS không phân biệt được. SDE phá tie.

Và khi M=5, vấn đề càng trầm trọng:

```
M=2:  Front 0 ≈ 10-15% quần thể   → NDS chọn đủ nhiều, SDE ít việc
M=5:  Front 0 ≈ 80-90% quần thể   → GẦN NHƯ TẤT CẢ đều Front 0
                                    → NDS gần như VÔ DỤNG
                                    → SDE phải làm gần như MỌI THỨ
```

Đây chính là lý do SDE quan trọng hơn khi many-objective, và cũng là lý do dùng SDE thay Crowding Distance (CD mất tác dụng khi M >= 4).

---

**User**

dựa vào đâu để chia được thành nhóm 1 2 3 ... nhỉ, nhóm 0 là tốt nhất rồi

---

**Cursor**

Dựa vào **bóc lớp**. Front 0 bóc ra → ai không còn bị ai dominate → Front 1. Lặp lại.

---

### Ví dụ 6 solutions, 2 mục tiêu

```
s1: (3, 900)    s2: (5, 800)    s3: (5, 780)
s4: (8, 650)    s5: (10, 900)   s6: (7, 850)
```

**Bước 1: Tìm Front 0**

Đếm mỗi solution bị bao nhiêu thằng dominate:

```
s1 (3,900): ai dominate s1?
  s2 (5,800): 5>3 → KHÔNG    (s2 tệ hơn s1 ở Z₁)
  s3 (5,780): 5>3 → KHÔNG
  s4 (8,650): 8>3 → KHÔNG
  s5 (10,900): 10>3 → KHÔNG
  s6 (7,850): 7>3 → KHÔNG
  → count = 0 → FRONT 0 ★

s3 (5,780): ai dominate s3?
  s1 (3,900): 900>780 → KHÔNG (s1 tệ hơn s3 ở Z₂)
  → count = 0 → FRONT 0 ★

s4 (8,650): ai dominate s4?
  s1 (3,900): 900>650 → KHÔNG
  s3 (5,780): 780>650 → KHÔNG
  → count = 0 → FRONT 0 ★

s2 (5,800): ai dominate s2?
  s3 (5,780): 5≤5 và 780≤800, có 780<800 → s3 DOMINATE s2 ✓
  → count = 1

s5 (10,900): ai dominate s5?
  s1 (3,900): 3≤10 và 900≤900, có 3<10 → s1 DOMINATE s5 ✓
  s4 (8,650): 8≤10 và 650≤900 → s4 DOMINATE s5 ✓
  s6 (7,850): 7≤10 và 850≤900 → s6 DOMINATE s5 ✓
  → count = 3

s6 (7,850): ai dominate s6?
  s1 (3,900): 900>850 → KHÔNG
  s3 (5,780): 5≤7 và 780≤850 → s3 DOMINATE s6 ✓
  → count = 1
```

```
Front 0 = [s1, s3, s4]     (count = 0, không ai dominate)

Z₂ ▲
900│  s1●                 ○s5
850│              ○s6
800│      ○s2
780│      ●s3
650│              ●s4
   └────────────────────▶ Z₁
   3    5    7    8   10

● = Front 0
○ = chưa phân loại
```

---

**Bước 2: "Bóc" Front 0 ra → Tìm Front 1**

Giả vờ s1, s3, s4 **không tồn tại**. Ai dominate ai trong số còn lại?

```
Còn: s2(5,800), s5(10,900), s6(7,850)

Giảm domination_count (trừ đi ảnh hưởng của Front 0):

s2: count = 1 (bị s3 dominate)
    s3 thuộc Front 0 → trừ 1 → count = 0 → FRONT 1 ★

s6: count = 1 (bị s3 dominate)
    s3 thuộc Front 0 → trừ 1 → count = 0 → FRONT 1 ★

s5: count = 3 (bị s1, s4, s6 dominate)
    s1 thuộc Front 0 → trừ 1 → count = 2
    s4 thuộc Front 0 → trừ 1 → count = 1
    s6 CHƯA bóc → vẫn đếm → count = 1 → CHƯA vào Front 1
```

```
Front 1 = [s2, s6]

Z₂ ▲
900│  s1(F0)              ○s5
850│              ◆s6(F1)
800│      ◆s2(F1)
780│      ●s3(F0)
650│              ●s4(F0)
   └────────────────────▶ Z₁
```

---

**Bước 3: "Bóc" Front 1 ra → Tìm Front 2**

```
Còn: s5(10,900)

s5: count = 1 (còn bị s6 dominate)
    s6 thuộc Front 1 → trừ 1 → count = 0 → FRONT 2 ★
```

```
Front 2 = [s5]
```

---

### Kết quả cuối

```
Front 0: [s1, s3, s4]  ← tốt nhất, lớp ngoài cùng
Front 1: [s2, s6]      ← bị Front 0 dominate, nhưng bóc F0 ra thì nó giỏi nhất
Front 2: [s5]          ← tệ nhất, bị mọi lớp dominate

Z₂ ▲
900│  s1(F0)              s5(F2)
850│              s6(F1)
800│      s2(F1)
780│      s3(F0)
650│              s4(F0)
   └────────────────────▶ Z₁
```

---

### Tóm lại

```
Front 0: Không ai dominate       → "giỏi nhất"
Front 1: Bóc Front 0 ra thì không ai dominate → "giỏi nhì"
Front 2: Bóc Front 0+1 ra thì không ai dominate → "giỏi ba"
...

Giống bóc hành: lớp ngoài = tốt nhất → bóc ra → lớp tiếp → bóc ra → ...
```

---

**User**

có giới hạn gì không

---

**Cursor**

Không có giới hạn. Bóc đến khi hết solutions thì dừng.

```
N solutions → tệ nhất N fronts (mỗi front 1 con)
           → tốt nhất 1 front (tất cả non-dominated)

Ví dụ 201 solutions:
  Trường hợp tốt:   Front 0: 201 con → 1 front duy nhất
  Trường hợp tệ:    Front 0: 1 con, Front 1: 1 con, ..., Front 200: 1 con
  Thực tế M=5:      Front 0: ~160 con, Front 1: ~30 con, Front 2: ~11 con
```

Số fronts phụ thuộc vào **M (số mục tiêu)** và **solutions phân bố thế nào**:

```
M=2:  Ít non-dominated → nhiều fronts (5-10 fronts)
M=5:  Gần như ai cũng non-dominated → ít fronts (2-3 fronts)
```

Đây chính là vấn đề many-objective: M càng lớn → Front 0 càng to → NDS càng ít tác dụng → SDE phải gánh.

---

**User**

SDE gánh như nào khi mà thằng front 0 nó full rồi 

---

**Cursor**

Khi Front 0 chứa gần hết quần thể:

```
201 solutions, cần chọn 100:

Front 0: 180 con    ← vượt quá 100 rồi!
Front 1: 21 con     ← không cần xét

→ Phải chọn 100 từ 180 con CÙNG FRONT 0
→ NDS không giúp gì (tất cả đều rank 0)
→ SDE + Niching quyết định TOÀN BỘ
```

Lúc này Algorithm 6 chạy thẳng vào Phase 3:

```
Phase 2: Lấp đầy fronts
  Front 0 (180 con): 0 + 180 > 100 → VƯỢT NGAY TỪ FRONT ĐẦU TIÊN
  → selected = rỗng, remaining = 100
  → TOÀN BỘ 100 slot do Phase 3 quyết định

Phase 3: Chọn 100 từ 180 con cùng Front 0
  1. Gán 180 con vào 210 reference directions (Niching)
  2. Tính SDE cho 180 con
  3. Lặp 100 lần:
     - Tìm niche vắng nhất → chọn 1 con (SDE phá tie)
     - 80 con bị loại
```

Cụ thể:

```
210 reference directions, 180 con:

dir1:  15 con    ← đông
dir2:  0 con     ← trống
dir3:  8 con
dir4:  12 con    ← đông
dir5:  1 con     ← vắng
...
dir210: 3 con

Vòng 1: dir2 vắng nhất (0 con) → không ai thuộc dir2 → bỏ qua
         dir5 vắng nhất (1 con) → chọn con đó
Vòng 2: tìm niche vắng nhì → chọn
...
Vòng 100: đủ 100 con

Ai bị loại? 80 con ở những niche ĐÃ ĐÔNG
  dir1 có 15 con → chỉ giữ 3-4, loại 11-12
  dir4 có 12 con → chỉ giữ 2-3, loại 9-10
```

Trong cùng 1 niche có nhiều con → SDE quyết định giữ ai:

```
dir1 có 15 con, chỉ giữ 4:

  SDE(s3)  = 0.42  ← cô lập → GIỮ ✓
  SDE(s7)  = 0.38  ← khá vắng → GIỮ ✓
  SDE(s12) = 0.31  → GIỮ ✓
  SDE(s18) = 0.25  → GIỮ ✓
  SDE(s5)  = 0.08  → LOẠI ✗
  SDE(s9)  = 0.05  → LOẠI ✗
  SDE(s11) = 0.02  → LOẠI ✗
  ...11 con bị loại (SDE thấp = đông = thừa)
```

---

### Tóm lại

```
M=2:  NDS làm 80%, SDE làm 20%     (NDS đủ phân biệt)
M=5:  NDS làm ~5%, SDE làm ~95%    (Front 0 quá to, NDS gần như vô dụng)
```

Khi Front 0 full → **SDE + Niching chính là thuật toán chọn lọc thực sự**. NDS chỉ đóng vai trò loại nhanh những con rõ ràng tệ (front cuối), còn lại SDE gánh hết.

---

**User**

giải thích kĩ hơn về phase 3 cho tôi

---

**Cursor**

## Phase 3: Niching Selection — Giải thích từng bước

---

### Bối cảnh

```
Front biên có 12 con, cần chọn 8, loại 4.
5 mục tiêu, 6 reference directions.
Các front trước đã chọn 5 con (đếm vào niche counts).
```

---

### Bước 3a: Reference direction là gì?

Reference direction = **tia** từ gốc tọa độ trong không gian mục tiêu. Mỗi tia đại diện **1 kiểu trade-off**.

```
Ví dụ 2 mục tiêu, 4 directions:

Z₂ ▲
   │╲  dir1 = (0, 1): "ưu tiên Z₂"
   │ ╲
   │  ╲ dir2 = (0.33, 0.67): "Z₂ quan trọng hơn Z₁ một chút"
   │   ╲
   │    ╲ dir3 = (0.67, 0.33): "Z₁ quan trọng hơn"
   │     ╲
   └──────╲──────▶ Z₁
           dir4 = (1, 0): "ưu tiên Z₁"
```

Với M=5 mục tiêu, Das-Dennis tạo 210 directions. Mỗi direction = 1 tổ hợp trọng số (w₁, w₂, w₃, w₄, w₅) sao cho tổng = 1.

---

### Bước 3b: Gán mỗi solution vào direction gần nhất

```python
front_assignments = associate_to_directions(front_norm, ref_dirs)  # dòng 250
```

Với mỗi solution, tính **khoảng cách vuông góc** đến mỗi tia, gán vào tia gần nhất:

```
Solution s6 ở vị trí (0.3, 0.8) trong objective space:

                     ╱ dir2
              s6 ●──┤  ← khoảng cách vuông góc đến dir2 = 0.05 (GẦN NHẤT)
                   ╱
                  ╱ dir1
                 ╱──── khoảng cách vuông góc đến dir1 = 0.20

→ s6 gán vào dir2
```

Code cụ thể:

```python
# Chiếu solution p lên direction d
proj_scalar = np.dot(p, d) / np.dot(d, d)   # hình chiếu lên tia
proj = proj_scalar * d                        # tọa độ điểm chiếu
perp_dist = np.linalg.norm(p - proj)          # khoảng cách vuông góc
```

```
Hình dung:

  dir2 ──────────────────→
                  ↑ perp_dist = 0.05
            ●s6 ──┘
            (khoảng cách từ s6 đến tia dir2)
```

Kết quả gán 12 con vào 6 directions:

```
dir1: s6, s7, s8          → 3 con
dir2: s9                   → 1 con
dir3: (trống)              → 0 con
dir4: s10, s11, s12, s13   → 4 con
dir5: s14, s15             → 2 con
dir6: s16, s17             → 2 con
```

---

### Bước 3c: Đếm niche counts (gồm cả front trước)

```python
niche_counts = existing_niche_counts.copy()   # dòng 253
```

```
Các front trước đã chọn 5 con, phân bổ:
  dir1: 1 con từ front trước
  dir2: 0
  dir3: 2 con từ front trước
  dir4: 1 con từ front trước
  dir5: 0
  dir6: 1 con từ front trước

Niche counts hiện tại (trước khi chọn từ front biên):

  dir1: 1    dir2: 0    dir3: 2    dir4: 1    dir5: 0    dir6: 1
```

---

### Bước 3d: Lặp chọn từng con — ưu tiên niche vắng nhất

```python
for _ in range(n_select):    # lặp 8 lần (cần chọn 8 con)
```

**Vòng 1:**

```python
# Tìm niche vắng nhất trong số remaining
for r in remaining:
    niche = front_assignments[r]
    c = niche_counts[niche]
    if c < min_count: ...
```

```
Duyệt 12 con, xem niche count của mỗi con:

  s6  → dir1 → count=1
  s7  → dir1 → count=1
  s8  → dir1 → count=1
  s9  → dir2 → count=0  ← VẮNG NHẤT
  s10 → dir4 → count=1
  s11 → dir4 → count=1
  s12 → dir4 → count=1
  s13 → dir4 → count=1
  s14 → dir5 → count=0  ← VẮNG NHẤT
  s15 → dir5 → count=0  ← VẮNG NHẤT
  s16 → dir6 → count=1
  s17 → dir6 → count=1

min_count = 0
candidate_niches = {dir2, dir5}  ← 2 niche đều có count=0
```

```python
# Trong candidate niches, chọn con có SDE phù hợp nhất
for r in remaining:
    if niche in candidate_niches:
        if sde_values[idx] < best_sde:
            best_r = r
```

```
Các con thuộc niche vắng nhất (dir2, dir5):
  s9  (dir2): SDE = 0.35
  s14 (dir5): SDE = 0.28  ← thấp nhất
  s15 (dir5): SDE = 0.41

→ Chọn s14 (SDE thấp nhất trong niche vắng nhất)
```

```python
selected.append(front_indices[best_r])        # thêm s14
niche_counts[front_assignments[best_r]] += 1  # dir5: 0 → 1
remaining.remove(best_r)                       # bỏ s14 khỏi danh sách
```

```
Sau vòng 1:
  selected = [s14]
  dir5: 0 → 1
  remaining = 11 con
```

---

**Vòng 2:**

```
Niche counts: dir1=1, dir2=0, dir3=2, dir4=1, dir5=1, dir6=1

min_count = 0 → candidate = {dir2}
Các con trong dir2: s9 (SDE=0.35)

→ Chọn s9
  dir2: 0 → 1
  selected = [s14, s9]
```

---

**Vòng 3:**

```
Niche counts: dir1=1, dir2=1, dir3=2, dir4=1, dir5=1, dir6=1

min_count = 1 → candidate = {dir1, dir2, dir4, dir5, dir6}  (tất cả trừ dir3)

Các con trong candidate niches:
  s6  (dir1): SDE = 0.12
  s7  (dir1): SDE = 0.45
  s8  (dir1): SDE = 0.22
  s10 (dir4): SDE = 0.08  ← thấp nhất
  s11 (dir4): SDE = 0.33
  s12 (dir4): SDE = 0.19
  s13 (dir4): SDE = 0.41
  s15 (dir5): SDE = 0.41
  s16 (dir6): SDE = 0.29
  s17 (dir6): SDE = 0.15

→ Chọn s10 (SDE = 0.08, thấp nhất)
  dir4: 1 → 2
  selected = [s14, s9, s10]
```

---

**Vòng 4-8:** Tiếp tục tương tự...

```
Vòng 4: min_count=1, chọn s6  (dir1) → dir1: 1→2
Vòng 5: min_count=1, chọn s17 (dir6) → dir6: 1→2
Vòng 6: min_count=1, chọn s15 (dir5) → dir5: 1→2
Vòng 7: min_count=2, chọn s12 (dir4) → dir4: 2→3
Vòng 8: min_count=2, chọn s7  (dir1) → dir1: 2→3

selected = [s14, s9, s10, s6, s17, s15, s12, s7]  ← 8 con
```

**4 con bị loại:** s8 (dir1), s11 (dir4), s13 (dir4), s16 (dir6)

→ Toàn bộ bị loại vì ở **niche đã đông** + SDE cao (không cần giữ thêm).

---

### Kết quả trực quan

```
TRƯỚC (12 con):                    SAU (8 con):

dir1: ●●● (3 con)                 dir1: ●● (giữ 2, loại 1)
dir2: ● (1 con)                   dir2: ● (giữ hết)
dir3: (trống)                     dir3: (trống)
dir4: ●●●● (4 con)               dir4: ●● (giữ 2, loại 2)
dir5: ●● (2 con)                  dir5: ●● (giữ hết)
dir6: ●● (2 con)                  dir6: ● (giữ 1, loại 1)

→ TRẢI ĐỀU hơn!
   Trước: [3, 1, 0, 4, 2, 2]  max-min = 4
   Sau:   [2, 1, 0, 2, 2, 1]  max-min = 2
```

---

### Tóm lại Phase 3

```
1. Gán mỗi con vào reference direction gần nhất
   → biết con nào thuộc "góc" nào

2. Lặp từng vòng:
   a) Tìm niche VẮNG NHẤT (count thấp nhất)
   b) Trong niche đó, chọn con SDE phù hợp nhất
   c) Tăng count niche đó lên 1
   
3. Kết quả: solutions TRẢI ĐỀU theo mọi hướng trade-off
   Niche đông bị cắt bớt. Niche vắng được ưu tiên.
```

Logic đơn giản: **chỗ vắng thì thêm người, chỗ đông thì loại bớt**.

---

**User**

6 reference directions con số này được lấy từ đâu ra

---

**Cursor**

Con số reference directions **không cố định** — nó được **tính từ công thức toán học** dựa trên 2 tham số: số mục tiêu **M** và số phân chia **H** (n_partitions).

---

### Công thức Das-Dennis

Số reference directions được tính bằng tổ hợp:

```
N_dirs = C(H + M - 1, M - 1)
```

Trong đó:
- **M** = số mục tiêu (ở đây M = 5)
- **H** = số phân chia trên mỗi trục (n_partitions)

Mỗi direction là 1 vector `(w₁, w₂, w₃, w₄, w₅)` sao cho tổng = 1, với mỗi `wᵢ` là bội số của `1/H`.

---

### Code trong `inssso.py`

```282:296:g:\vrptw-for-pisso\algorithm\inssso.py
        # Generate reference directions for many-objective selection
        n_obj = 5  # Z1..Z5
        if preference is not None:
            self.ref_dirs = preference_biased_dirs(
                n_objectives=n_obj,
                g=preference.g,
                w=preference.w,
                n_total=105,
                pref_ratio=0.7,
            )
        else:
            self.ref_dirs = das_dennis(n_partitions=4, n_objectives=n_obj)
```

Có 2 trường hợp:

---

### Trường hợp 1: Không có preference → `das_dennis(H=4, M=5)`

```
N_dirs = C(4 + 5 - 1, 5 - 1) = C(8, 4) = 70 directions
```

Tính tay:

```
H = 4, M = 5
Mỗi direction = (a/4, b/4, c/4, d/4, e/4) với a+b+c+d+e = 4

Ví dụ một số directions:
  (4/4, 0, 0, 0, 0) = (1.0, 0, 0, 0, 0)   → chỉ ưu tiên Z₁
  (3/4, 1/4, 0, 0, 0) = (0.75, 0.25, 0, 0, 0)
  (1/4, 1/4, 1/4, 1/4, 0) = (0.25, 0.25, 0.25, 0.25, 0)
  (0, 0, 0, 0, 4/4) = (0, 0, 0, 0, 1.0)   → chỉ ưu tiên Z₅

Tổng cộng: 70 directions phủ đều simplex 5 chiều
```

---

### Trường hợp 2: Có preference → `preference_biased_dirs(n_total=105)`

Chia 105 directions thành 2 lớp:

```
70% preference (≈73 dirs): tập trung quanh hướng ưu tiên của DM
30% uniform    (≈32 dirs): trải đều toàn bộ simplex
```

Code cụ thể:

```78:113:g:\vrptw-for-pisso\algorithm\reference_dirs.py
    # --- Uniform layer ---
    n_uniform = max(int(n_total * (1 - pref_ratio)), 10)
    H_uniform = _find_partitions(n_objectives, n_uniform)
    uniform_dirs = das_dennis(H_uniform, n_objectives)

    # --- Preference layer ---
    n_pref = n_total - len(uniform_dirs)
    // ...
    center = w / (w.sum() + 1e-15)
    // ... tạo dense dirs rồi shift về phía center ...
    shifted = (1 - alpha) * dense_dirs + alpha * center
```

```
Hình dung (2D cho dễ):

                     Uniform dirs (30%)
Z₂ ▲                ○ ○ ○ ○ ○ ○ ○ ○
   │               ╱               ╲
   │              ╱  Preference      ╲
   │             ╱   dirs (70%)       ╲
   │            ╱    ●●●●●            ╲
   │           ╱     ●●●●●●            ╲
   │          ╱       ↑ center (w)      ╲
   └──────────────────────────────────────▶ Z₁

○ = uniform direction (trải đều)
● = preference direction (co cụm quanh w)
```

---

### Bảng tham chiếu nhanh

| H (partitions) | M (objectives) | Số directions |
|:-:|:-:|:-:|
| 3 | 5 | C(7,4) = **35** |
| 4 | 5 | C(8,4) = **70** |
| 5 | 5 | C(9,4) = **126** |
| 6 | 5 | C(10,4) = **210** |
| 4 | 3 | C(6,2) = **15** |
| 4 | 10 | C(13,9) = **715** |

H càng lớn → directions càng nhiều → phân giải càng mịn, nhưng tốn chi phí hơn.

---

### Tóm lại

Con số 6 trong ví dụ của tôi là **đơn giản hóa để minh họa**. Trong thực tế, thuật toán của bạn tạo ra **khoảng 70-105 reference directions** tùy có preference hay không, được tính tự động bằng công thức tổ hợp Das-Dennis `C(H+M-1, M-1)`.

---

**User**

dựa vào tập solomon của tôi thì H bằng bao nhiêu nhỉ

---

**Cursor**

Từ code đã đọc ở trên, câu trả lời rất rõ ràng:

### Trong code của bạn, H được **hard-code**, không phụ thuộc vào tập Solomon

```292:293:g:\vrptw-for-pisso\algorithm\inssso.py
        else:
            self.ref_dirs = das_dennis(n_partitions=4, n_objectives=n_obj)
```

- **Không có preference:** `H = 4`, M = 5 → `C(8,4)` = **70 directions**
- **Có preference:** gọi `preference_biased_dirs(n_total=105)`, bên trong `_find_partitions` tự tìm H phù hợp cho từng lớp (uniform + preference)

---

### H có liên quan gì đến tập Solomon không?

**Không trực tiếp.** H quyết định độ mịn của reference directions trong **không gian mục tiêu** (5 chiều: Z₁-Z₅), chứ không liên quan đến số khách hàng hay cấu trúc instance Solomon (C101, R201, RC108...).

Tập Solomon ảnh hưởng đến:
- Số khách hàng (25, 50, 100)
- Kiểu phân bố (C, R, RC)
- Kích thước time window

Còn H ảnh hưởng đến **lưới chia trong objective space**, hoàn toàn độc lập.

---

### Vậy H = 4 có hợp lý không?

Với M = 5 mục tiêu, cộng đồng nghiên cứu thường dùng:

| H | Số directions | Nhận xét |
|:-:|:-:|:--|
| 3 | 35 | Quá thưa cho 5 mục tiêu |
| **4** | **70** | **Phổ biến, cân bằng chi phí và độ phân giải** |
| 5 | 126 | Mịn hơn, nhưng tốn hơn |
| 6 | 210 | Rất mịn, thường dùng cho population lớn (>200) |

**H = 4 → 70 directions** là lựa chọn hợp lý và phổ biến cho population size `n_sol = 100` của bạn. Lý do:

```
Nếu n_sol = 100 và N_dirs = 70:
  Trung bình mỗi direction có 100/70 ≈ 1.4 solution
  → Đủ mịn để phân biệt, không quá thưa cũng không quá dày

Nếu N_dirs = 210 (H=6) mà n_sol = 100:
  Trung bình 100/210 ≈ 0.48 solution/direction
  → Quá nhiều direction trống, niching mất ý nghĩa
```

Tóm lại: **H = 4 là giá trị cố định trong code, không thay đổi theo instance Solomon, và nó phù hợp với population size 100 + 5 mục tiêu.**

---

**User**

vậy tạo cụ thể từng direction như nào

---

**Cursor**

### Das-Dennis tạo direction bằng cách nào

Ý tưởng cực kỳ đơn giản: **chia đều một cái bánh thành H phần, rồi liệt kê tất cả các cách phân phối**.

---

### Quy tắc

Với H = 4, M = 5:

```
Tìm tất cả bộ (a, b, c, d, e) sao cho:
  a + b + c + d + e = 4       (tổng nguyên = H)
  a, b, c, d, e ≥ 0           (không âm)

Rồi chia cho H:
  direction = (a/4, b/4, c/4, d/4, e/4)

→ Mỗi thành phần ∈ {0, 0.25, 0.5, 0.75, 1.0}
→ Tổng luôn = 1.0
```

---

### Minh họa đơn giản: H = 3, M = 3 (3 mục tiêu, 3 phân chia)

Liệt kê tất cả (a, b, c) sao cho a+b+c = 3:

```
 #  | (a, b, c) | direction = (a/3, b/3, c/3)  | Ý nghĩa
----+-----------+-------------------------------+------------------------
 1  | (3, 0, 0) | (1.00, 0.00, 0.00)           | 100% Z₁
 2  | (2, 1, 0) | (0.67, 0.33, 0.00)           | Z₁ chủ đạo, chút Z₂
 3  | (2, 0, 1) | (0.67, 0.00, 0.33)           | Z₁ chủ đạo, chút Z₃
 4  | (1, 2, 0) | (0.33, 0.67, 0.00)           | Z₂ chủ đạo, chút Z₁
 5  | (1, 1, 1) | (0.33, 0.33, 0.33)           | Cân bằng cả 3
 6  | (1, 0, 2) | (0.33, 0.00, 0.67)           | Z₃ chủ đạo, chút Z₁
 7  | (0, 3, 0) | (0.00, 1.00, 0.00)           | 100% Z₂
 8  | (0, 2, 1) | (0.00, 0.67, 0.33)           | Z₂ chủ đạo, chút Z₃
 9  | (0, 1, 2) | (0.00, 0.33, 0.67)           | Z₃ chủ đạo, chút Z₂
10  | (0, 0, 3) | (0.00, 0.00, 1.00)           | 100% Z₃

Tổng: C(3+3-1, 3-1) = C(5,2) = 10 directions ✓
```

Hình dung trên tam giác simplex (nhìn từ trên xuống):

```
          Z₁ = (1,0,0)
           ╱╲
          ╱  ╲
         ●    ●          ← (2/3, 1/3, 0) và (2/3, 0, 1/3)
        ╱      ╲
       ●    ●    ●       ← (1/3, 2/3, 0), (1/3, 1/3, 1/3), (1/3, 0, 2/3)
      ╱              ╲
     ●    ●      ●    ●  ← (0, 1, 0), (0, 2/3, 1/3), (0, 1/3, 2/3), (0, 0, 1)
    Z₂ ──────────────── Z₃

    10 điểm trải đều trên tam giác!
```

---

### Giờ xem code đệ quy chạy thế nào

```37:44:g:\vrptw-for-pisso\algorithm\reference_dirs.py
    def _recursive(M, H, d, result, current):
        if d == M - 1:
            current[d] = H
            result.append(current.copy() / n_partitions)
            return
        for i in range(H + 1):
            current[d] = i
            _recursive(M, H - i, d + 1, result, current)
```

Trace với H=3, M=3:

```
_recursive(M=3, H=3, d=0, current=[_, _, _])
│
├─ i=0: current=[0, _, _]
│  └─ _recursive(M=3, H=3, d=1)
│     ├─ i=0: current=[0, 0, _] → d=2 (cuối) → [0, 0, 3] → (0/3, 0/3, 3/3)
│     ├─ i=1: current=[0, 1, _] → d=2 → [0, 1, 2] → (0, 1/3, 2/3)
│     ├─ i=2: current=[0, 2, _] → d=2 → [0, 2, 1] → (0, 2/3, 1/3)
│     └─ i=3: current=[0, 3, _] → d=2 → [0, 3, 0] → (0, 1, 0)
│
├─ i=1: current=[1, _, _]
│  └─ _recursive(M=3, H=2, d=1)      ← H còn lại = 3-1 = 2
│     ├─ i=0: [1, 0, 2] → (1/3, 0, 2/3)
│     ├─ i=1: [1, 1, 1] → (1/3, 1/3, 1/3)    ← cân bằng!
│     └─ i=2: [1, 2, 0] → (1/3, 2/3, 0)
│
├─ i=2: current=[2, _, _]
│  └─ _recursive(M=3, H=1, d=1)      ← H còn lại = 3-2 = 1
│     ├─ i=0: [2, 0, 1] → (2/3, 0, 1/3)
│     └─ i=1: [2, 1, 0] → (2/3, 1/3, 0)
│
└─ i=3: current=[3, _, _]
   └─ _recursive(M=3, H=0, d=1)      ← H còn lại = 0
      └─ i=0: [3, 0, 0] → (1, 0, 0)

Tổng: 4 + 3 + 2 + 1 = 10 directions ✓
```

---

### Với thuật toán của bạn: H=4, M=5

Tương tự nhưng 5 chiều. Một vài direction cụ thể:

```
(4,0,0,0,0)/4 = (1.00, 0.00, 0.00, 0.00, 0.00) → chỉ tối ưu Z₁ (số xe)
(0,4,0,0,0)/4 = (0.00, 1.00, 0.00, 0.00, 0.00) → chỉ tối ưu Z₂ (tổng quãng đường)
(0,0,0,0,4)/4 = (0.00, 0.00, 0.00, 0.00, 1.00) → chỉ tối ưu Z₅
(1,1,1,1,0)/4 = (0.25, 0.25, 0.25, 0.25, 0.00) → cân bằng 4 mục tiêu, bỏ Z₅
(1,1,1,1,0)/4 = ...
(0,1,1,1,1)/4 = (0.00, 0.25, 0.25, 0.25, 0.25) → cân bằng Z₂-Z₅, bỏ Z₁
...
Tổng: C(8,4) = 70 directions
```

---

### Tóm lại

```
Das-Dennis = liệt kê TẤT CẢ các cách chia H phần cho M mục tiêu

Bước 1: Tìm mọi bộ số nguyên (a₁, a₂, ..., aₘ) sao cho tổng = H
Bước 2: Chia cho H → direction = (a₁/H, a₂/H, ..., aₘ/H)
Bước 3: Mỗi direction tổng = 1.0, nằm trên simplex

Dùng đệ quy: cố định chiều d = aᵢ, rồi chia phần còn lại (H - aᵢ) 
cho các chiều tiếp theo.
```

Bản chất giống bài toán **"chia H viên bi vào M cái hộp"** — liệt kê mọi cách chia rồi mỗi cách = 1 reference direction.

---

**User**

oke, thế giờ có 70 dir, 186 solotion, thì tính khoảng cách từng solution tới từng dir -> solution sẽ biết được ở dir nào, rồi đi xét từng dir theo thứ tự ít -> nhiều solution và dùng SDE để chọn lọc ra đúng không 

---

**Cursor**

Hiểu đúng hướng rồi, nhưng có **1 điểm quan trọng** cần chỉnh lại:

---

### Niching KHÔNG xét toàn bộ 186 solution

Niching chỉ xét **front biên** (front cuối cùng bị cắt), không phải toàn bộ merged population.

```
merged = P ∪ Q = khoảng 200 solution
Cần chọn: n_sol = 100

Phase 1-2: NDS chia front, lấp đầy từ Front 0 trở đi

  Front 0:  45 con  → lấy hết   (tổng: 45)
  Front 1:  30 con  → lấy hết   (tổng: 75)
  Front 2:  40 con  → CẦN 25, CÓ 40 → ĐÂY LÀ FRONT BIÊN
  Front 3+: bỏ hết

Phase 3: Niching chỉ xét 40 con của Front 2, chọn ra 25 con
```

→ Niching xét **40 con** với 70 directions, **không phải 186 con**.

---

### Flow đúng

```
Bước 1: Gán 40 con (front biên) vào 70 directions
         Tính khoảng cách vuông góc từ mỗi con đến mỗi dir
         Mỗi con → dir gần nhất

         dir1:  s₁, s₂, s₃        (3 con)
         dir2:  (trống)            (0 con)
         dir5:  s₇                 (1 con)
         dir12: s₁₅, s₁₆, s₁₇, s₁₈  (4 con)
         ...
         (nhiều dir trống vì 40 con < 70 dirs)

Bước 2: Đếm niche count GỒM CẢ 75 con đã chọn ở front trước
         75 con (Front 0 + Front 1) cũng được gán vào dirs

         dir1:  đã có 2 (từ front trước) + 3 (front biên) → count = 2
         dir2:  đã có 0 + 0                                → count = 0
         dir5:  đã có 1 + 1                                → count = 1
         dir12: đã có 3 + 4                                → count = 3

Bước 3: Lặp 25 lần, mỗi lần:
         a) Tìm dir có count THẤP NHẤT (trong số dir còn solution ở front biên)
         b) Trong dir đó, chọn con SDE thấp nhất (cô lập nhất)
         c) Tăng count dir đó lên 1
```

---

### Vậy hiểu của bạn đúng ở đâu?

| Phần | Đúng/Sai |
|:--|:--|
| Tính khoảng cách solution → dir, gán vào dir gần nhất | Đúng |
| Xét dir theo thứ tự ít → nhiều | Đúng |
| Dùng SDE để chọn trong dir | Đúng |
| Xét toàn bộ 186 solution | **Sai** — chỉ xét front biên |

---

### Tại sao chỉ xét front biên?

```
Front 0, 1: LẤY HẾT, không cần chọn
  → Vì chúng tốt hơn theo Pareto dominance, không cần bàn

Front 2 (biên): QUÁ ĐÔNG, phải cắt bớt
  → Đây mới là nơi cần Niching + SDE

Front 3+: BỎ HẾT, không cần xét
  → Vì bị dominate bởi front trước
```

Niching + SDE chỉ "ra tay" khi NDS không đủ phân biệt — tức là **trong cùng 1 front, ai ở ai đi**.

---

**User**

thì ý tao là pareto[0] nó có 186 thẳng đó, giờ cần 100 thằng thì ưu tiên lấy từ các dir như nào, lấy hết từ dir nhỏ nhất tới dir lớn dần hay sao

---

**Cursor**

Không phải lấy **hết** từ dir nhỏ nhất rồi chuyển sang dir tiếp. Nó lấy **1 con mỗi lần**, rồi xét lại.

---

### Cơ chế chính xác: Round-robin từng con một

Front 0 có 186 con, cần chọn 100. Lặp **100 vòng**, mỗi vòng chỉ chọn **1 con**:

```
Giả sử 186 con phân bổ vào 70 dirs:

  dir1:  5 con    dir2:  0 con    dir3:  3 con    dir4:  0 con
  dir5:  2 con    dir6:  4 con    dir7:  1 con    dir8:  0 con
  dir9:  6 con    dir10: 3 con    ...
  (nhiều dir trống vì 186 con < 70 dirs × 3)
```

**Vòng 1:**

```
Tìm dir count thấp nhất → count = 0 → {dir2, dir4, dir8, ...}
Nhưng dir2, dir4, dir8 TRỐNG (không có solution nào trong front biên)
→ Bỏ qua, tìm count thấp nhất CÓ solution → count = 1 → {dir7}
→ dir7 chỉ có 1 con → chọn luôn con đó
→ dir7: count 0 → 1
```

**Vòng 2:**

```
Count thấp nhất (có solution) → count = 1 → {dir7, dir5, ...}
  dir5 có 2 con: SDE = 0.12, 0.35
  dir7 đã chọn 1 → count = 1, còn 0 con remaining → bỏ qua
→ Chọn con SDE thấp nhất trong dir5: SDE = 0.12
→ dir5: count 0 → 1
```

**Vòng 3:**

```
Count thấp nhất → count = 1 → {dir3, dir10, dir5, ...}
  dir3 có 3 con: SDE = 0.08, 0.21, 0.44
  dir10 có 3 con: SDE = 0.15, 0.29, 0.37
  dir5 còn 1 con: SDE = 0.35
→ Chọn SDE thấp nhất TOÀN CỤC: dir3, SDE = 0.08
→ dir3: count 0 → 1
```

**Vòng 4-10:** Tiếp tục cho đến khi mọi dir (có solution) đều có count ≥ 1

```
Sau ~30 vòng (giả sử 30 dir có solution):
  dir1: 1    dir3: 1    dir5: 1    dir6: 1    dir7: 1    ...
  Tất cả dir có solution đều có count = 1
```

**Vòng 31+:** Bắt đầu "vòng 2" — lúc này count thấp nhất = 1

```
Lại tìm dir count = 1 (tất cả), chọn con SDE thấp nhất
→ Đều đặn phân phối thêm 1 con cho mỗi dir
```

**Vòng 60+:** Mỗi dir ~2 con, bắt đầu "vòng 3"

**Vòng 100:** Dừng. Đủ 100 con.

---

### Hình dung quá trình

```
186 con → 70 dirs → chọn 100 con

Vòng 1-30:   Mỗi dir lấy 1 con (con SDE tốt nhất)    → ~30 con
              ┌─┬─┬─┬─┬─┬─┬─┐
              │1│1│1│1│1│1│1│...  mỗi dir = 1
              └─┴─┴─┴─┴─┴─┴─┘

Vòng 31-60:  Mỗi dir lấy thêm 1 (con SDE tốt thứ 2)  → ~60 con
              ┌─┬─┬─┬─┬─┬─┬─┐
              │2│2│2│2│2│2│2│...  mỗi dir = 2
              └─┴─┴─┴─┴─┴─┴─┘

Vòng 61-90:  Mỗi dir lấy thêm 1                       → ~90 con
              ┌─┬─┬─┬─┬─┬─┬─┐
              │3│3│3│3│3│3│3│...  mỗi dir = 3
              └─┴─┴─┴─┴─┴─┴─┘

Vòng 91-100: Chỉ 10 dir được thêm 1 con nữa (dir nào SDE tốt nhất)
              ┌─┬─┬─┬─┬─┬─┬─┐
              │4│3│4│3│3│4│3│...  không đều nữa, SDE quyết định
              └─┴─┴─┴─┴─┴─┴─┘
```

---

### Tóm lại

```
KHÔNG PHẢI: Lấy hết dir nhỏ → chuyển sang dir lớn
MÀ LÀ:     Lấy 1 con từ dir ít nhất, rồi XÉT LẠI, lấy tiếp 1 con

Giống chia bài:
  - Mỗi lượt chia 1 lá cho người ít bài nhất
  - Nếu nhiều người cùng ít → chia cho người có lá bài "tốt nhất" (SDE thấp)
  - Lặp đến khi đủ 100 lá
```

Kết quả: solutions **trải đều tối đa** qua mọi direction, không có dir nào bị tập trung quá nhiều trong khi dir khác còn trống.

---

**User**

theo tao hiểu như mày nói là, ví dụ vòng 1 lấy từ cái ít nhất rồi thì vòng 2 sẽ bỏ qua cái lấy từ vòng 1 và chỉ xét 69 dir còn lại thôi đúng không? mà 69 thằng đó chọn ra những thằng ít nhất 

---

**Cursor**

Không, **không bỏ qua dir đã chọn**. Tất cả 70 dir đều được xét lại mỗi vòng.

---

### Cơ chế thực tế

Sau khi chọn 1 con từ dir7, **count của dir7 tăng lên 1**. Vòng tiếp theo xét lại **toàn bộ 70 dir**, so sánh count:

```
Vòng 1: Chọn 1 con từ dir7 (count thấp nhất = 0)
         → dir7: count 0 → 1

Vòng 2: Xét LẠI cả 70 dir (gồm cả dir7)
         dir7:  count = 1   ← vẫn xét, nhưng count đã tăng
         dir5:  count = 0   ← thấp hơn dir7
         dir3:  count = 0   ← thấp hơn dir7
         → Chọn từ dir5 hoặc dir3 (count = 0, vẫn ít hơn dir7)

Vòng 3: Xét LẠI cả 70 dir
         dir7:  count = 1
         dir5:  count = 1   ← vừa tăng
         dir3:  count = 0   ← vẫn thấp nhất
         → Chọn từ dir3
```

---

### Điều thực sự bị loại khỏi xét: SOLUTION, không phải DIR

```python
selected.append(front_indices[best_r])      # chọn con này
niche_counts[front_assignments[best_r]] += 1 # tăng count dir
remaining.remove(best_r)                     # ← LOẠI CON NÀY khỏi remaining
```

```
Dir7 ban đầu có 3 con: s₁, s₂, s₃

Vòng 1: Chọn s₁ (SDE tốt nhất) → remaining bỏ s₁, dir7 count = 1
Vòng X: Dir7 lại là thấp nhất → chọn s₂ → remaining bỏ s₂, dir7 count = 2
Vòng Y: Dir7 lại là thấp nhất → chọn s₃ → remaining bỏ s₃, dir7 count = 3
         → Dir7 hết solution trong remaining, nhưng VẪN TỒN TẠI
         → Các vòng sau tìm dir thấp nhất, dir7 count=3 nên ít khi được chọn nữa
         → (mà cũng không còn solution để chọn)
```

---

### Tóm lại

```
Mỗi vòng:
  - Xét TẤT CẢ 70 dir         (không bỏ dir nào)
  - Tìm dir count THẤP NHẤT    (trong số dir CÒN solution chưa chọn)
  - Chọn 1 con từ dir đó
  - Tăng count dir đó
  - Loại CON ĐÃ CHỌN khỏi danh sách remaining

Cái bị loại: solution đã chọn
Cái KHÔNG bị loại: direction
```

Giống việc chia kẹo cho 70 đứa trẻ: mỗi lần nhìn ai **ít kẹo nhất** thì cho thêm 1 cái. Không bao giờ "bỏ qua" đứa nào — chỉ là đứa đã có nhiều thì phải chờ đến lượt sau.

---

**User**

vậy ví dụ có 5 thằng, 2 2 3 3 2, thì lần 1 lấy của SDE của thằng 1 2 5 lấy được từ 1, lần 2 lấy SDE của 2 5 lấy được của 2, lần 3 lấy SDE của  5, lần 3 lấy SDE của 1 2 5 vì đều = 1

---

**Cursor**

Gần đúng hết rồi, chỉ sai **vòng cuối**. Trace lại:

---

### Ban đầu: 5 dir, count = [2, 2, 3, 3, 2]

**Vòng 1:** min count = 2 → candidates = {dir1, dir2, dir5}

```
Xét SDE của tất cả solution trong dir1, dir2, dir5
→ Chọn 1 con (giả sử từ dir1)
→ count: [3, 2, 3, 3, 2]    ✓ đúng
```

**Vòng 2:** min count = 2 → candidates = {dir2, dir5}

```
Xét SDE của solution trong dir2, dir5
→ Chọn 1 con (giả sử từ dir2)
→ count: [3, 3, 3, 3, 2]    ✓ đúng
```

**Vòng 3:** min count = 2 → candidates = {dir5}

```
Xét SDE của solution trong dir5
→ Chọn 1 con từ dir5
→ count: [3, 3, 3, 3, 3]    ✓ đúng
```

**Vòng 4:** min count = 3 → candidates = {dir1, dir2, dir3, dir4, dir5} — **cả 5 thằng**

```
→ count đều = 3, nên xét TẤT CẢ 5 dir, không chỉ 1, 2, 5
→ Dir3, dir4 giờ cũng ngang hàng, được xét
→ SDE quyết định chọn từ dir nào
```

---

### Chỗ bạn nhầm

Bạn nói vòng 4 chỉ xét dir 1, 2, 5 vì "đều = 1". Thực tế **cả 5 dir đều = 3**, nên cả 5 đều là candidate:

```
Vòng 4:
  dir1: 3  ← candidate
  dir2: 3  ← candidate
  dir3: 3  ← candidate    ← THẰNG NÀY CŨNG ĐƯỢC XÉT
  dir4: 3  ← candidate    ← THẰNG NÀY CŨNG ĐƯỢC XÉT
  dir5: 3  ← candidate

→ Xét SDE solution còn lại của cả 5 dir, chọn 1 con tốt nhất
```

Còn lại logic bạn hiểu đúng hết.

---

**User**

vậy khi xét thế có bỏ qua những thằng đã được lấy không, chỉ ra đoạn code thực thi điều này

---

**Cursor**

Có, **solution đã chọn bị loại khỏi `remaining`**, không bao giờ được xét lại.

---

### Code thực thi điều này

```255:291:g:\vrptw-for-pisso\algorithm\reference_dirs.py
    selected = []
    remaining = list(range(len(front_indices)))   # ← danh sách chưa chọn

    for _ in range(n_select):
        if not remaining:
            break

        # Tìm niche count thấp nhất trong số REMAINING
        min_count = np.inf
        candidate_niches = set()
        for r in remaining:                        # ← CHỈ xét remaining
            niche = front_assignments[r]
            c = niche_counts[niche]
            if c < min_count:
                min_count = c
                candidate_niches = {niche}
            elif c == min_count:
                candidate_niches.add(niche)

        # Chọn con SDE tốt nhất trong candidate niches
        best_r = -1
        best_sde = np.inf
        for r in remaining:                        # ← CHỈ xét remaining
            niche = front_assignments[r]
            if niche in candidate_niches:
                idx = front_indices[r]
                if sde_values[idx] < best_sde:
                    best_sde = sde_values[idx]
                    best_r = r

        if best_r < 0:
            best_r = remaining[0]

        selected.append(front_indices[best_r])
        niche_counts[front_assignments[best_r]] += 1
        remaining.remove(best_r)                   # ← LOẠI khỏi remaining
```

---

### 3 dòng then chốt

**Dòng 256** — khởi tạo `remaining` = toàn bộ solution trong front biên:

```python
remaining = list(range(len(front_indices)))   # [0, 1, 2, ..., 185]
```

**Dòng 265 và 277** — vòng lặp chỉ duyệt `remaining`:

```python
for r in remaining:    # KHÔNG phải for r in range(len(front_indices))
```

→ Solution đã chọn không nằm trong `remaining` nên **tự động bị bỏ qua**.

**Dòng 290** — sau khi chọn, loại khỏi `remaining`:

```python
remaining.remove(best_r)   # xóa khỏi danh sách
```

---

### Trace ví dụ

```
Ban đầu:  remaining = [0, 1, 2, 3, 4, 5, 6, 7]   (8 con)

Vòng 1:   chọn con 4 (SDE tốt nhất trong dir vắng nhất)
           remaining.remove(4)
           remaining = [0, 1, 2, 3, 5, 6, 7]       (7 con)

Vòng 2:   for r in [0, 1, 2, 3, 5, 6, 7]  ← con 4 KHÔNG CÒN
           chọn con 1
           remaining = [0, 2, 3, 5, 6, 7]           (6 con)

Vòng 3:   for r in [0, 2, 3, 5, 6, 7]     ← con 4, 1 KHÔNG CÒN
           ...
```

Vậy câu trả lời: **có, solution đã chọn bị loại hoàn toàn**, đảm bảo không chọn trùng.

