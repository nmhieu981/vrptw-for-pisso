# Tổng hợp Công thức Toán học — iNSSSO cho MaO-VRPTW

> Trích xuất và chuẩn hoá LaTeX từ tài liệu kỹ thuật `paper_q1_full.md`
>
> **Tổng cộng: 87 công thức đánh số + các công thức phụ trợ**

---

## Phần I — Mô hình Toán học MO-VRPTW (§3)

### Ký hiệu cơ bản

$$d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$$

$$t_{ij} = \frac{d_{ij}}{v}, \quad v = 1$$

$$L_k = \sum_{i \in \tau_k} q_i$$

### Hàm mục tiêu (5 objectives — minimize)

**Eq. 1 — Số phương tiện sử dụng:**

$$Z_1 = \sum_{k=1}^{K_{\max}} y_k, \quad y_k = \begin{cases} 1 & \text{if } |\tau_k| > 0 \\ 0 & \text{otherwise} \end{cases} \tag{1}$$

**Eq. 2 — Tổng khoảng cách:**

$$Z_2 = \sum_{k=1}^{K} \left( d_{0, \tau_k^1} + \sum_{j=1}^{|\tau_k|-1} d_{\tau_k^j, \tau_k^{j+1}} + d_{\tau_k^{|\tau_k|}, 0} \right) \tag{2}$$

**Eq. 3 — Tổng thời gian chờ:**

$$Z_3 = \sum_{k=1}^{K} \sum_{i \in \tau_k} \max(0,\; e_i - a_i^k) \tag{3}$$

**Eq. 4 — Cân bằng tải trọng:**

$$Z_4 = L_{\text{max}} - L_{\text{min}}, \quad L_k = \sum_{i \in \tau_k} q_i \tag{4}$$

**Eq. 5 — Makespan:**

$$Z_5 = \displaystyle\max_{k \in K}  C_k \tag{5}$$

**Eq. 6 — Vector mục tiêu:**

$$\mathbf{f}(\mathbf{x}) = \bigl(Z_1(\mathbf{x}),\; Z_2(\mathbf{x}),\; Z_3(\mathbf{x}),\; Z_4(\mathbf{x}),\; Z_5(\mathbf{x})\bigr) \in \mathbb{R}^5 \tag{6}$$

### Ràng buộc

**Eq. 7 — Capacity:**

$$\sum_{i \in \tau_k} q_i \le Q, \quad \forall\, k \in K \tag{7}$$

**Eq. 8 — Thời điểm đến:**

$$a_i^k = \begin{cases} t_{0,i} & \text{if } i \text{ là KH đầu tiên trên route } k \\ b_{\text{prev}}^k + s_{\text{prev}} + t_{\text{prev},i} & \text{otherwise} \end{cases} \tag{8}$$

**Eq. 9 — Bắt đầu phục vụ:**

$$b_i^k = \max(a_i^k,\; e_i) \tag{9}$$

**Eq. 10 — Time window:**

$$b_i^k \le l_i, \quad \forall\, i \in \tau_k,\; \forall\, k \in K \tag{10}$$

**Eq. 11 — Thời điểm hoàn thành route:**

$$C_k = b_{\text{last}}^k + s_{\text{last}} + t_{\text{last}, 0} \tag{11}$$

**Eq. 12 — Depot deadline:**

$$C_k \le l_0, \quad \forall\, k \in K \tag{12}$$

### Penalty & Conflict

**Eq. 13 — Penalty function:**

$$\tilde{Z}_m = Z_m + P \cdot |\text{unserved}|, \quad P = 10^4, \quad \forall m = 1, \ldots, 5 \tag{13}$$

**Eq. 14 — Spearman rank correlation:**

$$r_s(f_i, f_j) = 1 - \frac{6 \sum_{k=1}^{n} d_k^2}{n(n^2 - 1)} \tag{14}$$

**Eq. 15 — Conflict metric:**

$$\mathcal{C}(i,j) = 1 - r_s(f_i, f_j) \tag{15}$$

---

## Phần II — Mã hoá & Khởi tạo (§4)

**Eq. 16 — Random-key decoding (argsort):**

$$\pi = \operatorname{argsort}(\mathbf{x}) + 1 \tag{16}$$

**Eq. 17 — Route partitioning:**

$$\tau_k = \bigl\{\pi_{j} : j_{k-1} < j < j_k,\; \pi_j \leq n\bigr\} \tag{17}$$

**Eq. 18 — Clarke-Wright Savings:**

$$\text{savings}(i,j) = d_{0,i} + d_{0,j} - d_{i,j} \tag{18}$$

**Eq. 19 — Solomon I1 Insertion cost:**

$$c_1(i, u, j) = \alpha_1 \bigl(d_{iu} + d_{uj} - \mu\, d_{ij}\bigr) + \alpha_2 \bigl(b_u^{\text{new}} - b_j^{\text{old}}\bigr) \tag{19}$$

---

## Phần III — NDS, SDE, Reference Directions (§5)

### Non-dominated Sorting

**Eq. 20 — Pareto dominance:**

$$\mathbf{x} \prec \mathbf{y} \iff \forall m: f_m(\mathbf{x}) \leq f_m(\mathbf{y}) \;\land\; \exists m: f_m(\mathbf{x}) < f_m(\mathbf{y}) \tag{20}$$

**Eq. 21 — Vectorised all-leq:**

$$\text{all\_leq} = \bigwedge_{m=1}^{M} \bigl(f_m(\mathbf{x}_i) \leq f_m(\mathbf{x}_j)\bigr) \tag{21}$$

**Eq. 22 — Vectorised any-lt:**

$$\text{any\_lt} = \bigvee_{m=1}^{M} \bigl(f_m(\mathbf{x}_i) < f_m(\mathbf{x}_j)\bigr) \tag{22}$$

**Eq. 23 — Dominance matrix:**

$$\mathit{dominates} = \mathit{all{\text{-}}leq} \;\land\; \mathit{any{\text{-}}lt} \tag{23}$$

### Shift-based Density Estimation (SDE)

**Eq. 24 — Chuẩn hoá objectives:**

$$\hat{f}_m(i) = \frac{f_m(i) - f_m^{\min}}{f_m^{\max} - f_m^{\min} + \varepsilon} \tag{24}$$

**Eq. 25 — Shift operation:**

$$\mathit{shifted}_{i,j,m} = \max\left(\hat{f}_m(j),\; \hat{f}_m(i)\right), \quad \forall\, m \tag{25}$$

**Eq. 26 — SDE distance:**

$$d_{\text{SDE}}(i, j) = \left\| \text{shifted}_{i,j} - \hat{f}(i) \right\|_2 \tag{26}$$

**Eq. 27 — SDE value:**

$$\text{SDE}(i) = \min_{j \neq i}\; d_{\text{SDE}}(i, j) \tag{27}$$

**Vectorised broadcasting shapes:**

$$\text{norm}_i \in \mathbb{R}^{N \times 1 \times M}, \quad \text{norm}_j \in \mathbb{R}^{1 \times N \times M}$$

$$\text{shifted} = \max(\text{norm}_j,\; \text{norm}_i) \in \mathbb{R}^{N \times N \times M}$$

### Reference Direction Niching

**Eq. 28 — Das-Dennis Reference Directions:**

$$W = \left\{ \mathbf{w} \in \mathbb{R}^M : w_m = \frac{j_m}{p},\; \sum_{m=1}^M j_m = p,\; j_m \geq 0 \right\} \tag{28}$$

**Eq. 29 — Number of directions:**

$$|W| = \binom{p + M - 1}{M - 1} \tag{29}$$

**Eq. 30 — Preference-biased directions:**

$$\mathbf{w}_{\text{bias}} = (1-\alpha)\, \mathbf{w}_{\text{DD}} + \alpha \cdot \frac{\mathbf{w}_{\text{pref}}}{\|\mathbf{w}_{\text{pref}}\|_1} \tag{30}$$

**Eq. 31 — Normalisation of biased directions:**

$$\mathbf{w}_{\text{bias}} = \frac{\mathbf{w}_{\text{bias}}}{\|\mathbf{w}_{\text{bias}}\|_1} \tag{31}$$

**Eq. 32 — Perpendicular distance (association):**

$$d_\perp(\mathbf{p}, \mathbf{w}) = \left\| \mathbf{p} - \frac{\mathbf{p} \cdot \mathbf{w}}{\mathbf{w} \cdot \mathbf{w}}\, \mathbf{w} \right\|_2 \tag{32}$$

---

## Phần IV — Preference: ASF, ROI, R-Dominance (§6)

**Eq. 33 — Achievement Scalarizing Function (ASF):**

$$\text{ASF}(\mathbf{x}) = \max_{m=1}^{M} \left\{ w_m \cdot \bigl(f_m(\mathbf{x}) - g_m\bigr) \right\} \tag{33}$$

**Eq. 34 — Augmented ASF:**

$$\text{ASF}_{\text{aug}}(\mathbf{x}) = \max_{m} \left\{ w_m \bigl(f_m - g_m\bigr) \right\} + \rho \sum_{m=1}^{M} w_m \bigl(f_m - g_m\bigr) \tag{34}$$

**Eq. 35 — ROI Ellipsoid:**

$$\text{ROI}(\mathbf{x}) = \left\{ \mathbf{x} : \sum_{m=1}^{M} \left( \frac{w_m \bigl(f_m(\mathbf{x}) - g_m\bigr)}{\delta \cdot \bigl(f_m^{\text{nadir}} - f_m^{\text{ideal}}\bigr)} \right)^2 \leq 1 \right\} \tag{35}$$

**Eq. 36 — ROI count metric:**

$$\text{ROI\_count}(t) = \bigl|\{x \in PF(t) : x \in \text{ROI}\}\bigr| \tag{36}$$

**Eq. 37 — R-Dominance (3 conditions):**

$$\mathbf{x} \prec_R \mathbf{y} \iff \begin{cases} (i)   & \mathbf{x} \prec \mathbf{y} & \text{(Pareto dominance)} \\ (ii)  & \mathbf{x} \in \text{ROI} \;\land\; \mathbf{y} \notin \text{ROI} & \text{(ROI membership)} \\ (iii) & \text{same\_ROI}(\mathbf{x}, \mathbf{y}) \;\land\; \text{ASF}(\mathbf{x}) < \text{ASF}(\mathbf{y}) & \text{(ASF comparison)} \end{cases} \tag{37}$$

**Eq. 38 — Auto-Calibration of Reference Point:**

$$g_m = \text{ideal}_m + 0.1 \cdot \max\bigl(p_{10,m} - \text{ideal}_m,\; 0\bigr) \tag{38}$$

---

## Phần V — Enhanced SSO: Lévy Flight & DE (§7)

**Eq. 39 — Original SSO update rule:**

$$x_{i,j}^{\text{new}} = \begin{cases} \text{gbest}_j & \text{if } \rho_j \leq c_g \\ x_{i,j}         & \text{if } c_g < \rho_j \leq c_w \\ U(0,1)          & \text{otherwise} \end{cases} \tag{39}$$

**Eq. 40 — Enhanced SSO (Lévy + DE) — CORE NOVELTY:**

$$x_{i,j}^{\text{new}} = \begin{cases} \text{gbest}_j & \text{if } \rho_j \leq c_g & \text{(exploitation)} \\ x_{i,j} & \text{if } c_g < \rho_j \leq c_w & \text{(conservation)} \\ x_{i,j} + L_j \cdot (\text{gbest}_j - x_{i,j}) \cdot 0.01 & \text{if } c_w < \rho_j \leq c_l & \text{(Lévy flight)} \\ x_{i,j} + F \cdot (x_{r1,j} - x_{r2,j}) & \text{otherwise} & \text{(DE perturbation)} \end{cases} \tag{40}$$

**Eq. 41 — Lévy flight step (Mantegna):**

$$L = \frac{u}{|v|^{1/\beta}}, \quad \beta = 1.5 \tag{41}$$

$$u \sim \mathcal{N}(0, \sigma_u^2), \quad v \sim \mathcal{N}(0, 1)$$

**Eq. 42 — Mantegna sigma:**

$$\sigma_u = \left[ \frac{\Gamma(1+\beta) \sin(\pi\beta/2)}{\Gamma\!\left(\frac{1+\beta}{2}\right) \beta \cdot 2^{(\beta-1)/2}} \right]^{1/\beta} \tag{42}$$

**Eq. 43 — DE/rand/1 perturbation:**

$$x_{i,j}^{\text{new}} = x_{i,j} + F \cdot (x_{r1,j} - x_{r2,j}), \quad F = 0.5 \tag{43}$$

---

## Phần VI — ALNS: Adaptive Large Neighbourhood Search (§8)

**Eq. 44 — Adaptive score update (exponential smoothing):**

$$\pi_k(s+1) = (1 - r) \cdot \pi_k(s) + r \cdot \Delta_k(s) \tag{44}$$

**Eq. 45 — Roulette-wheel selection probability:**

$$P(k) = \frac{\pi_k}{\sum_{j} \pi_j} \tag{45}$$

**Eq. 46 — Worst Removal saving:**

$$\text{saving}(c) = d_{\text{prev}(c),\, c} + d_{c,\, \text{next}(c)} - d_{\text{prev}(c),\, \text{next}(c)} \tag{46}$$

**Eq. 47 — Shaw Removal relatedness:**

$$R(i,j) = \alpha \frac{d_{ij}}{d_{\max}} + \beta \frac{|e_i - e_j|}{tw_{\max}} + \gamma \frac{|q_i - q_j|}{q_{\max}} \tag{47}$$

**Eq. 48 — Route Removal probability:**

$$P(k) \propto \exp\!\left(-10 \cdot \frac{|\tau_k|}{\max_j |\tau_j|}\right) \tag{48}$$

**Eq. 49 — Regret-2 Insertion:**

$$\text{regret}(c) = \text{cost}_2(c) - \text{cost}_1(c) \tag{49}$$

**Eq. 50 — Regret-3 Insertion:**

$$\text{regret}_3(c) = \sum_{j=2}^{3} \bigl(\text{cost}_j(c) - \text{cost}_1(c)\bigr) \tag{50}$$

**Eq. 51 — A\*-based Build score:**

$$f(c) = w_1 \cdot g_{\text{sc}}(c) + w_2 \cdot tw_{\text{sc}}(c) + (1 - w_1 - w_2) \cdot h_{\text{sc}}(c) \tag{51}$$

**Eq. 52 — Simulated Annealing acceptance:**

$$\text{accept}(\Delta f) \iff \Delta f < 0 \;\lor\; U(0,1) < \exp\!\left(-\frac{\Delta f}{T}\right) \tag{52}$$

**Eq. 53 — SA cooling schedule:**

$$T_{t+1} = c_T \cdot T_t, \quad c_T = 0.995 \tag{53}$$

---

## Phần VII — Dual Archive System (§9)

**Eq. 54 — ε-Dominance box index:**

$$\mathit{box}(\mathbf{f}) = \left\lfloor \frac{f_m}{\varepsilon + 10^{-15}} \right\rfloor, \quad \forall\, m = 1, \ldots, M \tag{54}$$

**Eq. 55 — ε-Box replacement rule:**

$$\mathbf{x} \text{ replaces } \mathbf{y} \iff \text{box}(\mathbf{x}) = \text{box}(\mathbf{y}) \;\land\; \text{ASF}_{\text{aug}}(\mathbf{x}) < \text{ASF}_{\text{aug}}(\mathbf{y}) \tag{55}$$

**Eq. 56 — Diversity archive pruning (SDE-based):**

$$\text{remove} = \arg\min_{i \in A_{\text{div}}} \text{SDE}(i) \tag{56}$$

**Eq. 57 — Sigmoid injection probability:**

$$p_{\text{conv}} = \sigma\!\left(\frac{s}{5} - 2\right) = \frac{1}{1 + e^{-(s/5 - 2)}} \tag{57}$$

---

## Phần VIII — Adaptive Mechanisms (§10)

**Eq. 58 — Adaptive ideal point update:**

$$\text{ideal}_m(t) = \min\!\bigl(\text{ideal}_m(t-1),\; \min_{\mathbf{x} \in P(t)} f_m(\mathbf{x})\bigr) \tag{58}$$

**Eq. 59 — Adaptive nadir point update (EMA):**

$$\text{nadir}_m(t) = (1-\alpha) \cdot \text{nadir}_m(t-1) + \alpha \cdot \max_{\mathbf{x} \in P(t)} f_m(\mathbf{x}) \tag{59}$$

**Eq. 60 — Normalised objectives:**

$$\hat{f}_m(\mathbf{x}) = \frac{f_m(\mathbf{x}) - \text{ideal}_m}{\text{nadir}_m - \text{ideal}_m + \varepsilon} \tag{60}$$

**Eq. 61 — Stagnation detection:**

$$\text{stagnation}(t) = \begin{cases} s(t-1) + 1 & \text{if } |\text{BestASF}(t) - \text{BestASF}(t-1)| < 10^{-6} \\ 0 & \text{otherwise} \end{cases} \tag{61}$$

**Eq. 62 — ALNS probability adaptation:**

$$n_{\text{abs}}(t) = \begin{cases} \min\!\bigl(0.5,\; n_{\text{abs}}^0 + 0.05 \cdot s(t)\bigr) & \text{if } s(t) > 5 \\ n_{\text{abs}}^0 & \text{otherwise} \end{cases} \tag{62}$$

**Eq. 63 — Mutation rate adaptation:**

$$\mu(t) = 0.05 + 0.10 \cdot \frac{t}{T_{\max}} \tag{63}$$

**Eq. 64 — Polynomial mutation:**

$$\delta_q = \begin{cases} \bigl(2r + (1-2r)(1-y)^{\eta_m+1}\bigr)^{1/(\eta_m+1)} - 1 & \text{if } r < 0.5 \\ 1 - \bigl(2(1-r) + 2(r-0.5)(1-y')^{\eta_m+1}\bigr)^{1/(\eta_m+1)} & \text{otherwise} \end{cases} \tag{64}$$

**Eq. 65 — Mutation application:**

$$x_j^{\text{new}} = \operatorname{clip}(x_j + \delta_q,\; 0,\; 0.999) \tag{65}$$

---

## Phần IX — Thuật toán So sánh (§13)

**Eq. 66 — MOEA/D Tchebycheff aggregation:**

$$g^{te}(\mathbf{x} \mid \boldsymbol{\lambda}, \mathbf{z}^*) = \max_{m=1}^{M} \left\{ \lambda_m \,|f_m(\mathbf{x}) - z_m^*| \right\} \tag{66}$$

**Eq. 67 — MOPSO velocity update:**

$$v_i = w \cdot v_i + c_1 r_1 (pbest_i - x_i) + c_2 r_2 (gbest - x_i) \tag{67}$$

**Eq. 68 — MOPSO position update:**

$$x_i^{\text{new}} = \operatorname{clip}(x_i + v_i,\; 0,\; 1) \tag{68}$$

**Eq. 69 — SPEA2 fitness:**

$$F(i) = \sum_{j \in \{j:\, j \prec i\}} \text{strength}(j) + \frac{1}{\sigma_k(i) + 2} \tag{69}$$

---

## Phần X — Chỉ số Đánh giá Hiệu năng (§14)

**Eq. 70 — Hypervolume (HV):**

$$\text{HV}(A) = \Lambda\!\left(\bigcup_{\mathbf{x} \in A} [\mathbf{x}, \mathbf{r}]\right) \tag{70}$$

**Eq. 71 — Reference-based Hypervolume (R-HV):**

$$\text{R-HV}(A) = \text{HV}\!\bigl(\{x \in A : x \in \text{ROI}\}\bigr) \tag{71}$$

**Eq. 72 — Best ASF:**

$$\text{Best ASF}(A) = \min_{\mathbf{x} \in A} \text{ASF}(\mathbf{x}) \tag{72}$$

**Eq. 73 — ROI Count:**

$$\text{ROI\_count}(A) = \bigl|\{\mathbf{x} \in A : \mathbf{x} \in \text{ROI}\}\bigr| \tag{73}$$

**Eq. 74 — Inverted Generational Distance (IGD):**

$$\text{IGD}(A, P^*) = \frac{1}{|P^*|} \sum_{\mathbf{p} \in P^*} \min_{\mathbf{a} \in A} \|\hat{\mathbf{p}} - \hat{\mathbf{a}}\|_2 \tag{74}$$

**Eq. 75 — Coverage (C-metric):**

$$C(A, B) = \frac{\bigl|\{\mathbf{b} \in B : \exists\, \mathbf{a} \in A,\; \mathbf{a} \preceq \mathbf{b}\}\bigr|}{|B|} \tag{75}$$

**Eq. 76 — Number of Non-dominated Solutions:**

$$N_{\text{nds}}(A) = \bigl|\{\mathbf{a} \in A : \nexists\, \mathbf{b} \in A,\; \mathbf{b} \prec \mathbf{a}\}\bigr| \tag{76}$$

---

## Phần XI — Phương pháp Thống kê (§15)

**Eq. 77 — Friedman critical difference:**

$$CD = q_\alpha \sqrt{\frac{k(k+1)}{6N}} \tag{77}$$

**Eq. 78 — Vargha-Delaney A-measure (effect size):**

$$\hat{A}_{12} = \frac{\sum_{i=1}^{n_1} \sum_{j=1}^{n_2} \mathbb{1}[x_i > y_j] + 0.5 \cdot \mathbb{1}[x_i = y_j]}{n_1 \cdot n_2} \tag{78}$$

---

## Phần XII — Ablation Study (§16)

**Eq. 79 — Ablation delta percentage:**

$$\Delta\%_k = \frac{\text{metric}_{V_0} - \text{metric}_{V_k}}{|\text{metric}_{V_0}|} \times 100 \tag{79}$$

---

## Phần XIII — Phân tích Lý thuyết (§17)

**Eq. 80 — Superdiffusion (Mean Squared Displacement):**

$$\left\langle r^2(t) \right\rangle \sim t^{\gamma}, \quad \gamma \gt 1 \;\text{(superdiffusion)} \tag{80}$$

**DE variance (unnumbered):**

$$E[\mathbf{d}] = E[\mathbf{x}_{r1}] - E[\mathbf{x}_{r2}] = \mathbf{0}$$

**Eq. 81 — DE perturbation variance:**

$$\operatorname{Var}[\mathbf{d}] = 2 \cdot \operatorname{Var}[\mathbf{x}] \tag{81}$$

### SDE vs Crowding Distance

**Crowding Distance per objective (unnumbered):**

$$CD_m(i) = \frac{f_m(\text{sorted}[i+1]) - f_m(\text{sorted}[i-1])}{f_m^{\max} - f_m^{\min}}$$

**Eq. 82 — Total Crowding Distance:**

$$CD(i) = \sum_{m=1}^{M} CD_m(i) \tag{82}$$

**Eq. 83 — CD limit for large M:**

$$CD(i) \to \text{constant} \quad \forall i \quad \text{as } M \to \infty \tag{83}$$

### R-Dominance Analysis

**Eq. 84 — Non-dominated ratio:**

$$P(\text{non-dominated}) \approx \frac{(\ln N)^{M-1}}{(M-1)! \cdot N} \to 1 \;\text{khi } M \to \infty \tag{84}$$

---

## Phần XIV — Phân tích Độ phức tạp (§18)

**Eq. 85 — Per-generation complexity:**

$$O\!\bigl(N^2 M + n_{\text{abs}}\, N R + N |W| M + |A| N\bigr) \tag{85}$$

**Eq. 86 — Total complexity:**

$$O\!\bigl(G \cdot (N^2 M + n_{\text{abs}}\, N R + N |W| M)\bigr) \tag{86}$$

**Eq. 87 — Space complexity:**

$$O\!\bigl(N^2 M + 2 N_A \cdot M + |W| \cdot M\bigr) \tag{87}$$

---

## Phụ lục — Dominance matrix (unnumbered)

$$\text{dom\_matrix}[i,j] = \text{True} \iff \mathbf{x}_i \prec \mathbf{x}_j$$

## Phụ lục — Lévy distribution

$$P(l) \sim l^{-\beta}, \quad 1 < \beta < 3$$

## Phụ lục — Lévy boundary parameter

$$c_l = c_w + 0.6\,(1 - c_w)$$

---

> **Ghi chú:** Công thức in **đậm** (Eq. 37, 40–43, 44–57) là các công thức mới/nâng cấp thuộc core novelty của thuật toán iNSSSO.
