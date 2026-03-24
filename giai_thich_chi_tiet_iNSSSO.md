# Giải thích Chi tiết Thuật toán iNSSSO

> **Mục đích:** Tài liệu tổng hợp giải thích trực quan từng thành phần cốt lõi của thuật toán iNSSSO, dành cho việc hiểu sâu trước khi viết bài báo Q1.
>
> **Tham chiếu:** Tài liệu kỹ thuật đầy đủ tại `paper_q1_full.md`

---

## Mục lục

1. [Phân loại thuật toán — Không phải GA](#1-phân-loại-thuật-toán--không-phải-ga)
2. [Điểm nổi bật để apply Q1](#2-điểm-nổi-bật-để-apply-q1)
3. [Bài báo cụ thể chứng minh khoảng trống](#3-bài-báo-cụ-thể-chứng-minh-khoảng-trống)
4. [Fast Non-dominated Sorting (NDS) — §5.1](#4-fast-non-dominated-sorting-nds--51)
5. [Shift-based Density Estimation (SDE) — §5.2](#5-shift-based-density-estimation-sde--52)
6. [DE/rand/1 Perturbation — §7.4](#6-derand1-perturbation--74)
7. [Lévy Flight — §7.3](#7-lévy-flight--73)
8. [Tại sao cần CẢ DE lẫn Lévy](#8-tại-sao-cần-cả-de-lẫn-lévy)
9. [Dual Archive — A_conv và A_div — §9](#9-dual-archive--a_conv-và-a_div--9)
10. [Vòng đời 1 Generation](#10-vòng-đời-1-generation)

---

## 1. Phân loại Thuật toán — Không phải GA

iNSSSO **không phải** Genetic Algorithm. GA dùng crossover (lai ghép 2 parents) + mutation. iNSSSO hoàn toàn khác:

```
GA truyền thống:
  Parent A + Parent B → Crossover → Child → Mutation → Child'

iNSSSO:
  x_i → Enhanced SSO (4 nhánh) hoặc ALNS (destroy/repair)
  Không có crossover. Không chọn 2 parents lai ghép.
```

### Phân loại chính xác từng thành phần

| Thành phần | Thuộc họ | Không phải |
|---|---|---|
| **SSO** (Squirrel Search) | Swarm Intelligence | Evolutionary/GA |
| **Lévy flight** | Random walk theory | Genetic operator |
| **DE/rand/1** | Differential Evolution | Crossover |
| **ALNS** | Local search / Neighbourhood search | Evolutionary |
| **NDS + SDE** | Multi-objective framework | GA-specific |
| **Polynomial mutation** | Mượn từ NSGA-II, chỉ vai trò phụ | GA core |

### Trong bài báo nên mô tả:

> *"...a swarm-based metaheuristic that hybridizes enhanced Squirrel Search Optimization with Adaptive Large Neighbourhood Search..."*

### So sánh với các thuật toán khác

| Thuật toán | Loại |
|---|---|
| NSGA-II, NSGA-III, SPEA2 | **Evolutionary Algorithm (EA)** — crossover + mutation |
| MOEA/D | **Decomposition EA** |
| MOPSO | **Swarm Intelligence** — velocity + position |
| **iNSSSO** | **Swarm Intelligence + Local Search hybrid** |

Cái duy nhất mượn từ EA là polynomial mutation (Eq. 64-65), nhưng chỉ kích hoạt khi stagnation > 3 với xác suất 5-15%.

---

## 2. Điểm nổi bật để apply Q1

### 2.1 Novelty claim mạnh nhất: "Chưa ai làm"

Kết hợp cả 3 thứ chưa ai kết hợp: **many-objective (M=5) + VRPTW + preference-based framework**.

- MO-VRPTW hiện tại chỉ xét 2-3 mục tiêu
- Many-objective VRP có nhưng không time windows, không preference
- Preference-based MaO có nhưng chỉ trên benchmark functions

### 2.2 SSO lần đầu áp dụng cho VRP

SSO (2019) đã có nhiều cải tiến nhưng **chưa bao giờ dùng cho bất kỳ variant VRP nào**. Không chỉ áp dụng mà còn nâng cấp bằng Lévy flight + DE perturbation.

### 2.3 ALNS tích hợp vào framework MaO

ALNS rất phổ biến cho VRP đơn mục tiêu (211 bài báo) nhưng **chưa ai tích hợp ALNS vào framework many-objective evolutionary**. Adaptive switching giữa SSO path và ALNS path tạo hệ thống **global search + local search tự cân bằng**.

### 2.4 Dual Archive giải quyết Convergence-Diversity Dilemma

Ishibuchi (2017) chứng minh 1 archive không thể đồng thời tối ưu convergence và diversity khi M >= 4. Dual archive giải quyết bằng A_conv (hội tụ) + A_div (đa dạng).

### 2.5 R-Dominance khôi phục selection pressure

Với M=5, ~80-90% solutions non-dominated → Pareto dominance gần như vô dụng. R-Dominance giảm non-dominated xuống ~10-20%.

### 2.6 Tóm lại bằng 1 câu cho reviewer

> **"First preference-based many-objective framework for VRPTW that hybridizes an enhanced SSO (Lévy + DE) with ALNS local search, managed by a dual-archive system — each component addresses a specific, identified gap in current literature."**

### 2.7 Checklist Q1

| Tiêu chí Q1 | Đáp ứng |
|---|---|
| **Novelty** | 6 contributions, mỗi cái fill 1 gap cụ thể (G1-G6) |
| **Lý thuyết** | 87 equations, superdiffusion proof, convergence sketch |
| **Thực nghiệm** | 7 thuật toán so sánh, 56 instances, 3 scales, 7 metrics |
| **Ablation** | 9 variants chứng minh từng component đóng góp |
| **Thống kê** | Wilcoxon + Friedman + Bonferroni + effect size |
| **Literature** | 70 refs, 35 từ 2024-2026 (50% rất mới) |
| **Tái tạo** | Pseudocode chi tiết cho tất cả 6 algorithms |

---

## 3. Bài báo Cụ thể Chứng minh Khoảng trống

### 3.1 MO-VRPTW chỉ 2-3 mục tiêu

**[3] Wang et al., 2025:**
> "Multiobjective vehicle routing optimization with time windows: A hybrid approach using deep reinforcement learning and NSGA-II"
> *IEEE Transactions on Intelligent Transportation Systems*, vol. 26, pp. 4032–4045.

**[12] Abdelmaguid, 2024:**
> "An improved multiobjective evolutionary algorithm for time-dependent vehicle routing problem with time windows"
> *Alexandria Engineering Journal*, vol. 92, pp. 1–15.

**[35] Feng et al., 2023:**
> "Solving multi-objective vehicle routing problems with time windows: A decomposition-based multiform optimization approach"
> *Tsinghua Science and Technology*, vol. 28, no. 5, pp. 1–14.

### 3.2 Many-objective VRP — KHÔNG time windows, KHÔNG preference

**[4] Chen et al., 2025:**
> "A local search with chain search path strategy for real-world many-objective vehicle routing problem"
> *Complex & Intelligent Systems*, vol. 11, art. 1825.

**[36] Liu et al., 2025:**
> "Research on multi-objective green vehicle routing problem with time windows based on the improved non-dominated sorting genetic algorithm III"
> *Symmetry*, vol. 17, no. 5, p. 734.
> *(Có time windows nhưng chỉ 3 mục tiêu, chưa many-objective)*

**[37] Ding et al., 2025:**
> "Practice of an improved many-objective route optimization algorithm in a multimodal transportation case under uncertain demand"
> *Complex & Intelligent Systems*, vol. 10, pp. 1–18.
> *(Many-objective nhưng multimodal transportation, không VRPTW)*

### 3.3 Preference-based MaO — CHỈ benchmark functions

**[10] Liu et al., 2025:**
> "Preference-based expensive multi-objective optimization without using an ideal point"
> *Complex & Intelligent Systems*, vol. 11, art. 1905.

**[11] Li, Cheng & Deb, 2023:**
> "Pre-DEMO: Preference-inspired differential evolution for multi/many-objective optimization"
> *IEEE Trans. Systems, Man, and Cybernetics: Systems*, vol. 53, no. 10, pp. 6268–6280.

**[31] Yadav, Ramu & Deb, 2024:**
> "Updated preference-based hypervolume metric for evaluating preference-based evolutionary multi-objective optimization"
> *Technical Report*, Michigan State University.

**[54] Tanabe & Ishibuchi, 2025:**
> "Multi-start via scalarization with target-point-based Tchebycheff distance"
> *Proc. GECCO 2025*.

### 3.4 Bảng tổng hợp khoảng trống

| Bài báo | Many-obj (M≥4) | Time Windows | Preference | Khoảng trống |
|---|---|---|---|---|
| Wang [3] 2025 | M=2 | Có | Không | Thiếu MaO + preference |
| Abdelmaguid [12] 2024 | M=2 | Có | Không | Thiếu MaO + preference |
| Chen [4] 2025 | **M=6** | **Không** | **Không** | Thiếu TW + preference |
| Liu [36] 2025 | M=3 | Có | Không | Chưa MaO |
| Liu [10] 2025 | M≥4 | Không | **Có** | Chỉ benchmark, không routing |
| Pre-DEMO [11] 2023 | M≥4 | Không | **Có** | Chỉ benchmark, không routing |
| **iNSSSO (đề xuất)** | **M=5** | **Có** | **Có** | **Fill tất cả gaps** |

---

## 4. Fast Non-dominated Sorting (NDS) — §5.1

### Khái niệm Pareto Dominance (Eq. 20)

Lời giải **x** thống trị (dominate) lời giải **y** khi:
- Tất cả mục tiêu của x **không tệ hơn** y
- Ít nhất 1 mục tiêu x **tốt hơn hẳn** y

Ví dụ: x = (3, 5, 2) và y = (4, 5, 3) → x dominate y vì mọi giá trị x ≤ y, và ở mục tiêu 1 và 3 thì x tốt hơn hẳn.

### Vectorised Implementation (Eq. 21-23)

Thay vì vòng lặp so sánh từng cặp, dùng NumPy broadcasting tính toàn bộ ma trận N×N cùng lúc:

- **Eq. 21 — all\_leq:** x_i ≤ x_j trên TẤT CẢ M mục tiêu? (phép AND)
- **Eq. 22 — any\_lt:** x_i < x_j trên ÍT NHẤT 1 mục tiêu? (phép OR)
- **Eq. 23 — dominates:** cả hai đều đúng → x_i dominate x_j

Độ phức tạp: $O(M \cdot N^2)$.

---

## 5. Shift-based Density Estimation (SDE) — §5.2

### Tại sao cần SDE thay Crowding Distance?

Crowding Distance (CD) tính mật độ bằng cách xét **từng mục tiêu riêng lẻ** rồi cộng lại. Khi M=5, theo Central Limit Theorem, tổng 5 khoảng cách 1-chiều gần như bằng nhau cho mọi solution → CD **không phân biệt được ai đông ai vắng** → selection thành random.

### SDE hoạt động thế nào — 4 bước

Ví dụ 3 solutions, 2 mục tiêu:

```
Solution A: f = (0.2, 0.8)   ← non-dominated
Solution B: f = (0.3, 0.7)   ← non-dominated
Solution C: f = (0.5, 0.9)   ← bị A dominate
```

**Bước 1 — Chuẩn hóa (Eq. 24):** Đưa mọi mục tiêu về [0, 1].

```
Â = (0.0, 0.5)    B̂ = (0.33, 0.0)    Ĉ = (1.0, 1.0)
```

**Bước 2 — Shift operation (Eq. 25) — BƯỚC THEN CHỐT:**

```
shifted_{i,j,m} = max(f̂_m(j), f̂_m(i))
```

Ý nghĩa: "Nếu j tốt hơn i ở mục tiêu m, giả vờ j ở cùng vị trí với i."

```
Cặp (C, A): shifted = (max(0.0, 1.0), max(0.5, 1.0)) = (1.0, 1.0) = GIỐNG C!
Cặp (A, B): shifted = (max(0.33, 0.0), max(0.0, 0.5)) = (0.33, 0.5) = B bị đẩy xa A
```

**Bước 3 — Distance (Eq. 26):**

```
d_SDE(C, A) = ‖(1.0, 1.0) - (1.0, 1.0)‖ = 0.0   ← A đè lên C!
d_SDE(A, B) = ‖(0.33, 0.5) - (0.0, 0.5)‖ = 0.33  ← A và B có khoảng cách
```

**Bước 4 — SDE value (Eq. 27):**

```
SDE(A) = 0.33   ← vắng
SDE(B) = 0.5    ← rất vắng
SDE(C) = 0.0    ← bị đè → LOẠI ĐẦU TIÊN
```

### Tóm lại SDE bằng 1 câu

> **"Khoảng cách đến hàng xóm gần nhất, nhưng nếu hàng xóm tốt hơn thì giả vờ nó đè lên tôi."**

- SDE cao → cô lập, quý giá → **giữ**
- SDE thấp → bị đè hoặc quá đông → **loại**
- Kết hợp cả convergence (phạt dominated) lẫn diversity (phạt đông) trong 1 con số

---

## 6. DE/rand/1 Perturbation — §7.4

### 6.1 DE là gì? — Nguồn gốc

Differential Evolution (DE) do Storn & Price đề xuất năm 1997 [50]. Đây là một trong những evolutionary algorithm hiệu quả nhất, dựa trên 1 ý tưởng cốt lõi:

> **"Hướng đi tốt = sự khác biệt giữa 2 cá thể trong quần thể"**

Tên gọi "DE/rand/1" phân loại cụ thể variant được dùng:
- **rand**: chọn base vector **ngẫu nhiên** (ở đây là x_i hiện tại)
- **1**: dùng **1** difference vector (r1 - r2)

Các variant khác (DE/best/1, DE/rand/2, ...) không dùng vì:
- DE/best/1 hội tụ quá nhanh → mất diversity trong MaO
- DE/rand/2 dùng 2 difference vectors → quá nhiều randomness

### 6.2 Công thức

```
x_new = x_i + F × (x_r1 - x_r2)       (Eq. 43)
```

Trong đó:
- `x_i = [0.73, 0.12, 0.89, 0.45, 0.31]` — vị trí hiện tại (random-key encoding)
- `x_r1`: cá thể ngẫu nhiên thứ 1 trong quần thể (r1 ≠ i)
- `x_r2`: cá thể ngẫu nhiên thứ 2 trong quần thể (r2 ≠ r1 ≠ i)
- `F = 0.5`: scaling factor (cố định)
- `(x_r1 - x_r2)`: **difference vector** — mã hóa sự khác biệt giữa 2 chiến lược routing

### 6.3 Difference vector chứa thông tin gì?

Mỗi solution trong quần thể là 1 cách giải VRPTW. Difference vector mã hóa **sự khác biệt giữa 2 chiến lược**:

```
Ví dụ: 5 khách hàng, 2 separator keys → dim = 7

r1 = [0.70, 0.30, 0.80, 0.10, 0.50, 0.20, 0.90]
      ↑ routes ngắn, ít xe, tốt về distance

r2 = [0.20, 0.90, 0.40, 0.60, 0.30, 0.80, 0.15]
      ↑ routes đều tải, tốt về balance

Difference vector:
r1 - r2 = [+0.50, -0.60, +0.40, -0.50, +0.20, -0.60, +0.75]
            ↑
            Mã hóa: "chuyển từ chiến lược balance sang chiến lược distance"

x_new = x_i + 0.5 × [+0.50, -0.60, +0.40, -0.50, +0.20, -0.60, +0.75]
      = x_i + [+0.25, -0.30, +0.20, -0.25, +0.10, -0.30, +0.375]
        ↑
        Dịch x_i MỘT CHÚT theo hướng "từ balance sang distance"
```

Khi decode random-key → thứ tự khách hàng thay đổi → routes thay đổi → trade-off objectives thay đổi.

Mỗi lần chọn r1, r2 khác nhau → **hướng đi khác nhau** → khám phá nhiều chiều khác nhau của không gian 5 mục tiêu.

### 6.4 Tại sao F = 0.5?

F kiểm soát **bước nhảy lớn hay nhỏ**:

```
F = 0.1: x_new rất gần x_i    → thay đổi nhẹ (quá bảo thủ)
F = 0.5: x_new ở giữa          → cân bằng tốt ✓
F = 0.9: x_new gần r1-r2 hơn  → thay đổi mạnh (quá mạo hiểm)
```

F = 0.5 là giá trị chuẩn trong literature DE [50, 26], cân bằng giữa exploration và exploitation. Trong bảng tham số (§11.2), range hợp lệ là [0.3, 0.9].

### 6.5 Tính chất 1: Implicit Adaptive Step Size (Eq. 81)

Đây là tính chất mạnh nhất mà random U(0,1) và Lévy đều không có.

Toán học:

```
Var[x_r1 - x_r2] = Var[x_r1] + Var[x_r2] = 2 × Var[population]
```

Step size (‖r1 - r2‖) **tỷ lệ thuận với diversity quần thể**:

| Giai đoạn | Diversity quần thể | ‖r1 - r2‖ | Hành vi |
|---|---|---|---|
| **Đầu** (100 solutions rải rác) | Cao | **Lớn** (~0.3-0.5) | Exploration mạnh |
| **Giữa** (đang hội tụ dần) | Trung bình | **Vừa** (~0.1-0.2) | Cân bằng |
| **Cuối** (tụ lại 1 vùng) | Thấp | **Nhỏ** (~0.01-0.05) | Fine-tune chính xác |

```
ĐẦU: quần thể rải rác

  ○         ○                    ○
       ○          ○        ○
  ○        ○           ○         ○

  r1 ở xa r2 → ‖r1 - r2‖ LỚN → nhảy xa → khám phá rộng


CUỐI: quần thể hội tụ

              ○○○
             ○○○○○
              ○○○

  r1 gần r2 → ‖r1 - r2‖ NHỎ → nhảy ngắn → tinh chỉnh cục bộ
```

**Không cần parameter nào điều khiển.** Step size tự co giãn.

So sánh:

| Cơ chế | Step size | Adaptive? |
|---|---|---|
| Random U(0,1) | Luôn trong [0,1] | **Không** — quá lớn khi cần fine-tune |
| Lévy | Heavy-tailed cố định | **Không** — phân phối không đổi theo thời gian |
| **DE** | = f(diversity quần thể) | **Có — tự động** |

### 6.6 Tính chất 2: Directed Search (Có hướng)

Random và Lévy nhảy theo **mọi hướng** với xác suất gần bằng nhau (isotropic). DE nhảy theo **hướng xác định** bởi 2 donors.

```
Không gian tìm kiếm (đơn giản hóa 2D):

Random/Lévy:            DE:
   ↗ ↑ ↖               
   ← ● →                 ● ───→ (hướng r1-r2)
   ↙ ↓ ↘               
   8 hướng bằng nhau     1 hướng cụ thể, dựa trên quần thể
```

Với quần thể 100 con: C(100, 2) = **4950 cặp (r1, r2)** → 4950 hướng khác nhau có thể được chọn → rất phong phú, nhưng mỗi lần đều có mục đích.

### 6.7 Tính chất 3: Diversity-preserving

Vì r1 và r2 được chọn **ngẫu nhiên** (không phải best), DE/rand/1 không hội tụ quá nhanh về gbest. So sánh:

```
DE/best/1: x_new = x_best + F × (r1 - r2)  → mọi con hướng về best → diversity ↓↓
DE/rand/1: x_new = x_i + F × (r1 - r2)     → mỗi con đi hướng khác → diversity ✓
```

Điều này quan trọng cho MaO (5 mục tiêu): cần duy trì diversity trên 5 chiều đồng thời.

### 6.8 Ví dụ cụ thể với VRPTW

```
Quần thể 100 solutions cho instance Solomon C101 (100 khách hàng):

Solution r1: 8 xe, distance=850, wait=20, balance=15, makespan=300
  → Ít xe nhưng routes dài, ít chờ

Solution r2: 12 xe, distance=620, wait=45, balance=5, makespan=250
  → Nhiều xe nhưng distance ngắn, balance tốt

(r1 - r2) mã hóa: "xu hướng giảm xe + tăng distance + giảm wait"

x_i + 0.5 × (r1 - r2):
  → Dịch x_i theo hướng trade-off "ít xe hơn"
  → Khi decode: có thể gom 2 route thành 1, thay đổi thứ tự phục vụ
  → Tạo solution mới khám phá trade-off Z₁ vs Z₂
```

### 6.9 Điểm yếu của DE

**Chết khi diversity = 0:**

```
Quần thể bị kẹt ở local optimum, tất cả tụ 1 chỗ:

              ○○○○
             ○○○○○○
              ○○○○

  r1 ≈ r2 → ‖r1 - r2‖ ≈ 0 → DE step ≈ 0

  x_new = x_i + 0.5 × (gần 0) ≈ x_i  → KHÔNG DI CHUYỂN

  Vùng tốt hơn ở xa:         ★★★
                              ★★★★

  DE KHÔNG BAO GIỜ tới được vì bước nhảy quá nhỏ
```

Đây chính là lý do cần Lévy flight bổ sung (xem Section 8).

### 6.10 Nếu không có DE — Variant V2 trong Ablation (§16)

Thay DE bằng random U(0,1):

```
Enhanced SSO đầy đủ:                   V2 (không DE):
  ρ ≤ c_g  → gbest (có hướng ✓)        ρ ≤ c_g  → gbest (có hướng ✓)
  ρ ≤ c_w  → giữ nguyên                ρ ≤ c_w  → giữ nguyên
  ρ ≤ c_l  → Lévy (vô hướng ✓)         ρ ≤ c_l  → Lévy (vô hướng ✓)
  ρ > c_l  → DE (CÓ HƯỚNG ✓)           ρ > c_l  → U(0,1) (vô hướng ✗) ← tệ
```

Hậu quả:

| Mất gì | Giải thích |
|---|---|
| Mất adaptive step size | U(0,1) luôn trong [0,1], không scale theo diversity |
| Mất directed search | Không tận dụng vị trí các cá thể khác |
| Convergence chậm hơn | Đặc biệt giai đoạn cuối khi cần fine-tune nhỏ |
| Exploration kém hướng | Chỉ còn Lévy (vô hướng) cho exploration |

Ước tính impact: **-3% đến -7% HV**. Không phải component quan trọng nhất (ALNS quan trọng hơn: -15% đến -25%), nhưng **có ý nghĩa thống kê**.

### 6.11 DE trong bối cảnh Enhanced SSO — 4 nhánh

```
Mỗi gene j của solution i:

  ρ_j = U(0,1)

  ρ ≤ 0.5  → x_new = gbest_j                          EXPLOITATION
             "Copy vị trí tốt nhất"
             Hướng: về gbest. Step: lớn (nhảy thẳng).

  ρ ≤ 0.7  → x_new = x_i,j                            CONSERVATION
             "Giữ nguyên"
             Bảo toàn thông tin tốt đã có.

  ρ ≤ 0.88 → x_new = x_i + L × (gbest - x_i) × 0.01  LÉVY FLIGHT
             "Nhảy vô hướng, heavy-tailed"
             Hướng: hơi về gbest. Step: heavy-tailed.

  ρ > 0.88 → x_new = x_i + 0.5 × (r1 - r2)           DE/RAND/1
             "Nhảy có hướng, adaptive step"
             Hướng: từ population. Step: adaptive.
```

4 nhánh tạo **phổ hành vi** từ exploitation cực (copy gbest) đến exploration có hướng (DE), với Lévy ở giữa để đảm bảo khả năng nhảy xa thoát local optima.

### 6.12 References chính về DE

| Ref | Nội dung | Liên quan |
|---|---|---|
| [50] Storn & Price, 1997 | DE gốc | Công thức DE/rand/1 |
| [26] Sun et al., 2025 | Hybrid DE-PSO dynamic | DE perturbation thoát local optima |
| [27] Emam, 2025 | MADEA — multi-objective DE | DE cho MO, vượt trội 60% test problems |
| [20] Ma et al., 2025 | Two-stage directed DE | DE trong dual-archive framework |

---

## 7. Lévy Flight — §7.3

### Lévy là gì?

Random walk với bước nhảy heavy-tailed: phần lớn bước **rất nhỏ** (fine-tune), đôi khi bước **cực lớn** (nhảy xa).

```
x_new = x_i + L × (gbest - x_i) × 0.01       (Eq. 40)

L = u / |v|^(1/β)    ← Mantegna's algorithm (Eq. 41-42)
u ~ N(0, σ²),  v ~ N(0, 1),  β = 1.5

Khi |v| rất nhỏ (hiếm) → L CỰC LỚN → nhảy xa
Khi |v| bình thường    → L nhỏ      → fine-tune
```

### Tại sao Lévy?

- Thuộc lớp **superdiffusion**: khám phá không gian nhanh gấp đôi Brownian motion
- Được chứng minh là **optimal foraging strategy** trong tự nhiên (Viswanathan 1999)
- Đặc biệt hiệu quả khi targets phân bố thưa thớt — đúng đặc điểm landscape VRPTW 5 mục tiêu

### Điểm yếu

Nhảy **vô hướng** — không biết hướng nào triển vọng, dựa vào may rủi.

### Nếu không có Lévy (Variant V1 trong Ablation):

- Mất khả năng nhảy xa thoát local optima
- Ước tính: **-3% đến -8% HV**

---

## 8. Tại sao cần CẢ DE lẫn Lévy

### Bảng bổ sung cho nhau

```
                 VÔ HƯỚNG              CÓ HƯỚNG
              (isotropic)           (anisotropic)
            ┌────────────────┬────────────────────┐
HEAVY-TAIL  │  LÉVY FLIGHT   │    (không có)      │
(nhảy xa    │  Thoát local   │                    │
 đôi khi)   │  optima ✓      │                    │
            ├────────────────┼────────────────────┤
ADAPTIVE    │  Random U(0,1) │  DE/rand/1         │
(scale theo │  SSO gốc       │  Đúng hướng +      │
 context)   │  (BỊ THAY THẾ) │  tự scale ✓        │
            └────────────────┴────────────────────┘
```

### 3 trường hợp thực tế

**Quần thể còn đa dạng:**
- DE: ‖r1-r2‖ lớn → bước lớn, CÓ HƯỚNG → khám phá hiệu quả ✓
- Lévy: bước nhỏ/lớn, VÔ HƯỚNG → khám phá bổ sung ✓

**Quần thể bị kẹt (diversity thấp):**
- DE: ‖r1-r2‖ ≈ 0 → BẤT LỰC ✗
- Lévy: occasional long jump → THOÁT → **cứu cánh** ✓

**Gần optimal, cần fine-tune:**
- DE: ‖r1-r2‖ nhỏ → bước nhỏ, CÓ HƯỚNG → tinh chỉnh chính xác ✓
- Lévy: phần lớn bước nhỏ → tinh chỉnh bổ sung ✓

### Ví dụ cụ thể VRPTW

```
Gen 50: Quần thể hội tụ, tất cả 9-10 xe, distance 700-720

  CHỈ DE: ‖r1-r2‖ ≈ 0 → kẹt tại 9-10 xe FOREVER ✗
  CHỈ Lévy: nhảy xa nhưng vô hướng → 90% nhảy tệ, 10% tốt → lãng phí ✗
  CẢ HAI: Lévy nhảy xa → tìm vùng 7 xe → DE dẫn đường trong vùng mới ✓
```

### Tóm lại bằng 1 câu

> **DE là GPS — biết đường đi nhưng chỉ trong phạm vi bản đồ.**
> **Lévy là trực thăng — nhảy được mọi nơi nhưng không biết nên đi đâu.**
> **Kết hợp = GPS + trực thăng: đi đúng hướng, và khi bản đồ hết thì bay ra ngoài tìm.**

---

## 9. Dual Archive — A_conv và A_div — §9

### 9.1 Mục đích cốt lõi

> **Giữ lại 2 loại solution tốt nhất mà 1 archive đơn lẻ không thể giữ đồng thời.**

Cả hai đều ngon, nhưng **ngon theo kiểu khác nhau**:

```
A_conv = ngon theo MẮT CỦA BẠN (preference)
A_div  = ngon theo TOÁN HỌC (Pareto optimal, trải đều)
```

```
Objective space:

    Z₂ ▲
       │  ○                          ○  ← A_div giữ (rìa PF)
       │     ○
       │        ●●●●                    ← A_conv giữ (gần preference)
       │           ●●●  ★ ← preference point
       │              ●●
       │                 ○              ← A_div giữ
       │                    ○           ← A_div giữ (rìa PF)
       └──────────────────────────▶ Z₁

    ● = A_conv (tập trung quanh ★)
    ○ = A_div  (trải đều toàn bộ Pareto front)
```

### 9.2 A_conv — Convergence Archive

| Bước | Công thức | Mục đích |
|---|---|---|
| Chia ô lưới | **Eq. 54** — `box(f) = ⌊f_m / (ε + 1e-15)⌋` | Chia objective space thành ε-box |
| Thay thế trong box | **Eq. 55** — `box(x) = box(y) ∧ ASF_aug(x) < ASF_aug(y)` | Giữ con gần preference hơn |
| Tính ASF | **Eq. 33-34** — `ASF(x) = max_m { w_m · (f_m(x) - g_m) }` | Đo khoảng cách đến preference |
| Pruning khi > 200 | Sort theo Eq. 34, giữ top N_A | Loại xa preference nhất |

**Tóm lại:** Eq. 54 (chia box) → Eq. 55 (thay thế) → Eq. 33-34 (ASF ranking)

### 9.3 A_div — Diversity Archive

| Bước | Công thức | Mục đích |
|---|---|---|
| Vào archive | **Eq. 20** — Pareto dominance | Non-dominated thì nhận |
| Chuẩn hóa | **Eq. 24** | Chuẩn hóa trước tính SDE |
| Shift + Distance | **Eq. 25-26** | Tính mật độ quanh mỗi solution |
| Giá trị SDE | **Eq. 27** — `SDE(i) = min_{j≠i} d_SDE(i,j)` | SDE thấp = đông, cao = vắng |
| Pruning khi > 200 | **Eq. 56** — `remove = argmin_i SDE(i)` | Loại chỗ đông nhất |

**Tóm lại:** Eq. 20 (Pareto check) → Eq. 24-27 (tính SDE) → Eq. 56 (prune đông nhất)

### 9.4 Injection — Chọn bơm archive nào (Eq. 57)

```
p_conv = 1 / (1 + e^-(s/5 - 2))    ← s = stagnation count

s = 0  → 88% bơm A_div,  12% bơm A_conv   (khám phá)
s = 10 → 50% bơm A_div,  50% bơm A_conv   (cân bằng)
s = 20 → 12% bơm A_div,  88% bơm A_conv   (tập trung)
```

Logic:
- **Đang chạy tốt** → bơm A_div (vùng xa, mở rộng tầm nhìn)
- **Bị kẹt** → bơm A_conv (quay về vùng preference, đào sâu)

### 9.5 Tại sao cần A_div nếu đã có A_conv?

Nếu chỉ bơm từ A_conv (gần preference) → thuật toán kẹt trong vùng preference mãi → bỏ lỡ vùng tốt hơn ở xa. A_div là **bảo hiểm** chống bỏ lỡ.

### 9.6 Bản đồ công thức nhanh

```
A_conv: Eq.54 → Eq.55 → Eq.33-34         (ε-box + ASF)
A_div:  Eq.20 → Eq.24-27 → Eq.56         (Pareto + SDE)
Injection: Eq.57                           (Sigmoid chọn archive)
Pseudocode tổng hợp: Algorithm 4 (§9.7)
```

---

## 10. Vòng đời 1 Generation

### Bước 1: Ranking quần thể hiện tại

```
P = {s₁, s₂, ..., s₁₀₀}   ← 100 solutions từ gen trước
         │
         ▼
    NDS + SDE ranking → gán rank + SDE score cho mỗi cá thể
    KHÔNG AI BỊ LOẠI. Chỉ đánh giá.
```

### Bước 2: Sinh 100 offspring (Q)

```
Với MỖI cá thể i = 1..100:
│
├─ 20% xác suất → ALNS path (§8)
│   Decode → destroy routes → repair → 2-opt → encode
│
└─ 80% xác suất → Enhanced SSO path (§7)
    4 nhánh: exploit / conserve / Lévy / DE

Kết quả: Q = {y₁, y₂, ..., y₁₀₀}   ← 100 offspring MỚI
P vẫn còn nguyên.
```

### Bước 3: Mutation + Local search

```
Mutation: nếu stagnation > 3, xác suất 5-15% → polynomial mutation
Local search: rank 0 feasible → 10%, còn lại → 3%
Q vẫn 100 con, một số được cải thiện thêm.
```

### Bước 4: Cập nhật Archive

```
Với MỖI y_i trong Q → thử vào A_conv VÀ A_div (song song, độc lập)

A_conv: box mới + non-dominated → THÊM. Cùng box + ASF tốt hơn → THAY THẾ.
A_div: non-dominated → THÊM. Quá 200 → loại SDE thấp nhất.

Archive KHÔNG BAO GIỜ reset. Solutions tốt sống mãi cho đến bị thay thế.
```

### Bước 5: Injection

```
Lấy 1 solution từ archive bơm vào Q → Q = 101 con
Stagnation thấp → A_div. Stagnation cao → A_conv.
```

### Bước 6: Environmental Selection (AI SỐNG AI CHẾT)

```
merged = P ∪ Q = 100 + 101 = 201 solutions
                    │
              NDS + SDE + Niching
                    │
              CHỌN ĐÚNG 100 TỐT NHẤT → P'

101 con BỊ LOẠI VĨNH VIỄN khỏi quần thể
(nhưng có thể vẫn sống trong archive)
```

### Sơ đồ tổng thể

```
P (100) ──ranking──→ sinh Q (100) ──mutation/LS──→ Q (100)
                                                     │
                                          ┌──────────┼──────────┐
                                          ▼          ▼          ▼
                                      A_conv      A_div     Injection
                                      (cập nhật)  (cập nhật) (lấy 1)
                                          │          │          │
                                          └──────────┼──────────┘
                                                     ▼
                                              Q (101 = 100+1)
                                                     │
                                              P ∪ Q = 201
                                                     │
                                             Chọn 100 tốt nhất
                                                     │
                                                     ▼
                                              P' (100) → GEN tiếp
```

### Ai sống, ai chết, ai bất tử

| Đối tượng | Vòng đời | Ghi chú |
|---|---|---|
| **P (quần thể)** | 100 con mỗi gen. 101 con chết mỗi gen | Cạnh tranh khốc liệt |
| **Q (offspring)** | Sinh ra đầu gen, sống hoặc chết cuối gen | Tạm thời |
| **A_conv** | Tích lũy qua mọi gen. Chỉ chết khi bị thay thế | Gần như bất tử |
| **A_div** | Tích lũy qua mọi gen. Chỉ chết khi bị dominated/prune | Gần như bất tử |
| **gbest** | Chọn lại mỗi gen từ Front 0 bằng ASF | Thay đổi liên tục |
| **ideal/nadir** | Cập nhật EMA mỗi gen, không reset | Monotonic (ideal chỉ giảm) |
| **ALNS scores** | Cập nhật mỗi lần dùng, tích lũy | Học dần |
| **stagnation** | Tăng nếu kẹt, reset về 0 khi cải thiện | Dao động |

**Điểm mấu chốt:** Archive là **bộ nhớ dài hạn**. Quần thể là **bộ nhớ ngắn hạn** — 50% bị loại mỗi gen.

---

*Tài liệu này tổng hợp từ các thảo luận chi tiết về iNSSSO, dùng để tham khảo nhanh khi viết bài báo Q1. Mọi công thức và section references trỏ về `paper_q1_full.md`.*
