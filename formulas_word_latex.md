# Công thức LaTeX — Tương thích Microsoft Word Equation Editor

> **Hướng dẫn sử dụng:**
> 1. Trong Word → Insert → Equation (hoặc Alt + =)
> 2. Nhấn vào ô Equation, chọn chế độ **LaTeX** (góc trên trái)
> 3. Copy từng công thức bên dưới và paste vào
> 4. Nhấn Enter hoặc click ra ngoài để convert
>
> **Lưu ý quan trọng:**
> - Các công thức có `\cases` (ngoặc nhọn chia trường hợp): Word không hỗ trợ `\begin{cases}`. Thay vào đó dùng **Insert → Equation → Bracket → Cases** từ ribbon, hoặc dùng cú pháp `\left\lbrace \matrix{...} \right.` như bên dưới.
> - Số thứ tự (1), (2)... **không paste** vào equation — tự đánh số bên ngoài.
> - Mỗi công thức nằm trong block ` ``` ` riêng để dễ copy.

---

## §3.2 — Hàm mục tiêu (5 objectives)

### Ký hiệu cơ bản

```
d_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}
```

```
t_{ij}=\frac{d_{ij}}{v},\quad v=1
```

```
L_k=\sum_{i\in\tau_k} q_i
```

### (1) Số phương tiện

```
Z_1=\sum_{k=1}^{K_{\max}} y_k
```

Phần điều kiện y_k dùng Cases bracket trong Word:

```
y_k=\left\lbrace\matrix{1 & |\tau_k|>0 \\ 0 & otherwise}\right.
```

### (2) Tổng khoảng cách

```
Z_2=\sum_{k=1}^{K}\left(d_{0,\tau_k^1}+\sum_{j=1}^{|\tau_k|-1} d_{\tau_k^j,\tau_k^{j+1}}+d_{\tau_k^{|\tau_k|},0}\right)
```

### (3) Tổng thời gian chờ

```
Z_3=\sum_{k=1}^{K}\sum_{i\in\tau_k}\max(0, e_i-a_i^k)
```

### (4) Cân bằng tải trọng

```
Z_4=L_{\max}-L_{\min},\quad L_k=\sum_{i\in\tau_k} q_i
```

### (5) Makespan

```
Z_5=\max_{k\in K} C_k
```

### (6) Vector mục tiêu

```
\mathbf{f}(\mathbf{x})=(Z_1(\mathbf{x}), Z_2(\mathbf{x}), Z_3(\mathbf{x}), Z_4(\mathbf{x}), Z_5(\mathbf{x}))\in\mathbb{R}^5
```

---

## §3.3 — Ràng buộc

### (7) Capacity

```
\sum_{i\in\tau_k} q_i\leq Q,\quad\forall k\in K
```

### (8) Thời điểm đến

```
a_i^k=\left\lbrace\matrix{t_{0,i} & i\;la\;KH\;dau\;tien \\ b_{prev}^k+s_{prev}+t_{prev,i} & otherwise}\right.
```

### (9) Bắt đầu phục vụ

```
b_i^k=\max(a_i^k, e_i)
```

### (10) Time window

```
b_i^k\leq l_i,\quad\forall i\in\tau_k,\;\forall k\in K
```

### (11) Thời điểm hoàn thành route

```
C_k=b_{last}^k+s_{last}+t_{last,0}
```

### (12) Depot deadline

```
C_k\leq l_0,\quad\forall k\in K
```

---

## §3.4 — Penalty

### (13) Penalty function

```
\tilde{Z}_m=Z_m+P\cdot|unserved|,\quad P=10^4,\quad\forall m=1,\ldots,5
```

---

## §3.5 — Conflict Analysis

### (14) Spearman rank correlation

```
r_s(f_i,f_j)=1-\frac{6\sum_{k=1}^{n} d_k^2}{n(n^2-1)}
```

### (15) Conflict metric

```
\mathcal{C}(i,j)=1-r_s(f_i,f_j)
```

---

## §4 — Mã hoá & Khởi tạo

### (16) Random-key decoding

```
\pi=argsort(\mathbf{x})+1
```

### (17) Route partitioning

```
\tau_k=\lbrace\pi_j:j_{k-1}<j<j_k,\;\pi_j\leq n\rbrace
```

### (18) Clarke-Wright Savings

```
savings(i,j)=d_{0,i}+d_{0,j}-d_{i,j}
```

### (19) Solomon I1 Insertion cost

```
c_1(i,u,j)=\alpha_1(d_{iu}+d_{uj}-\mu d_{ij})+\alpha_2(b_u^{new}-b_j^{old})
```

---

## §5 — NDS, SDE, Reference Directions

### (20) Pareto dominance

```
\mathbf{x}\prec\mathbf{y}\Leftrightarrow\forall m:f_m(\mathbf{x})\leq f_m(\mathbf{y})\wedge\exists m:f_m(\mathbf{x})<f_m(\mathbf{y})
```

### (21) Vectorised all-leq

```
all\_leq=\bigwedge_{m=1}^{M}(f_m(\mathbf{x}_i)\leq f_m(\mathbf{x}_j))
```

### (22) Vectorised any-lt

```
any\_lt=\bigvee_{m=1}^{M}(f_m(\mathbf{x}_i)<f_m(\mathbf{x}_j))
```

### (23) Dominance matrix

```
dominates=all\_leq\wedge any\_lt
```

### (24) Chuẩn hoá objectives (SDE)

```
\hat{f}_m(i)=\frac{f_m(i)-f_m^{\min}}{f_m^{\max}-f_m^{\min}+\varepsilon}
```

### (25) Shift operation

```
shifted_{i,j,m}=\max(\hat{f}_m(j),\hat{f}_m(i)),\quad\forall m
```

### (26) SDE distance

```
d_{SDE}(i,j)=\left\|shifted_{i,j}-\hat{f}(i)\right\|_2
```

### (27) SDE value

```
SDE(i)=\min_{j\neq i} d_{SDE}(i,j)
```

### (28) Das-Dennis Reference Directions

```
W=\left\lbrace\mathbf{w}\in\mathbb{R}^M:w_m=\frac{j_m}{p},\;\sum_{m=1}^M j_m=p,\;j_m\geq 0\right\rbrace
```

### (29) Number of directions

```
|W|=\binom{p+M-1}{M-1}
```

### (30) Preference-biased directions

```
\mathbf{w}_{bias}=(1-\alpha)\mathbf{w}_{DD}+\alpha\cdot\frac{\mathbf{w}_{pref}}{\|\mathbf{w}_{pref}\|_1}
```

### (31) Normalisation

```
\mathbf{w}_{bias}=\frac{\mathbf{w}_{bias}}{\|\mathbf{w}_{bias}\|_1}
```

### (32) Perpendicular distance

```
d_\perp(\mathbf{p},\mathbf{w})=\left\|\mathbf{p}-\frac{\mathbf{p}\cdot\mathbf{w}}{\mathbf{w}\cdot\mathbf{w}}\mathbf{w}\right\|_2
```

---

## §6 — Preference: ASF, ROI, R-Dominance

### (33) ASF

```
ASF(\mathbf{x})=\max_{m=1}^{M}\lbrace w_m\cdot(f_m(\mathbf{x})-g_m)\rbrace
```

### (34) Augmented ASF

```
ASF_{aug}(\mathbf{x})=\max_{m}\lbrace w_m(f_m-g_m)\rbrace+\rho\sum_{m=1}^{M} w_m(f_m-g_m)
```

### (35) ROI Ellipsoid

```
ROI(\mathbf{x})=\left\lbrace\mathbf{x}:\sum_{m=1}^{M}\left(\frac{w_m(f_m(\mathbf{x})-g_m)}{\delta\cdot(f_m^{nadir}-f_m^{ideal})}\right)^2\leq 1\right\rbrace
```

### (36) ROI count

```
ROI\_count(t)=|\lbrace x\in PF(t):x\in ROI\rbrace|
```

### (37) R-Dominance — 3 điều kiện (paste từng dòng riêng hoặc dùng Cases bracket)

Điều kiện (i):
```
\mathbf{x}\prec_R\mathbf{y}\;\;if\;\;\mathbf{x}\prec\mathbf{y}
```

Điều kiện (ii):
```
\mathbf{x}\prec_R\mathbf{y}\;\;if\;\;\mathbf{x}\in ROI\wedge\mathbf{y}\notin ROI
```

Điều kiện (iii):
```
\mathbf{x}\prec_R\mathbf{y}\;\;if\;\;same\_ROI(\mathbf{x},\mathbf{y})\wedge ASF(\mathbf{x})<ASF(\mathbf{y})
```

Hoặc dùng matrix (cases bracket):
```
\mathbf{x}\prec_R\mathbf{y}\Leftrightarrow\left\lbrace\matrix{\mathbf{x}\prec\mathbf{y} \\ \mathbf{x}\in ROI\wedge\mathbf{y}\notin ROI \\ same\_ROI\wedge ASF(\mathbf{x})<ASF(\mathbf{y})}\right.
```

### (38) Auto-Calibration

```
g_m=ideal_m+0.1\cdot\max(p_{10,m}-ideal_m, 0)
```

---

## §7 — Enhanced SSO: Lévy Flight & DE

### (39) Original SSO

```
x_{i,j}^{new}=\left\lbrace\matrix{gbest_j & \rho_j\leq c_g \\ x_{i,j} & c_g<\rho_j\leq c_w \\ U(0,1) & otherwise}\right.
```

### (40) Enhanced SSO — CORE NOVELTY

```
x_{i,j}^{new}=\left\lbrace\matrix{gbest_j & \rho_j\leq c_g \\ x_{i,j} & c_g<\rho_j\leq c_w \\ x_{i,j}+L_j\cdot(gbest_j-x_{i,j})\cdot 0.01 & c_w<\rho_j\leq c_l \\ x_{i,j}+F\cdot(x_{r1,j}-x_{r2,j}) & otherwise}\right.
```

### (41) Lévy flight step

```
L=\frac{u}{|v|^{1/\beta}},\quad\beta=1.5
```

```
u\sim\mathcal{N}(0,\sigma_u^2),\quad v\sim\mathcal{N}(0,1)
```

### (42) Mantegna sigma

```
\sigma_u=\left[\frac{\Gamma(1+\beta)\sin(\pi\beta/2)}{\Gamma\left(\frac{1+\beta}{2}\right)\beta\cdot 2^{(\beta-1)/2}}\right]^{1/\beta}
```

### (43) DE/rand/1

```
x_{i,j}^{new}=x_{i,j}+F\cdot(x_{r1,j}-x_{r2,j}),\quad F=0.5
```

---

## §8 — ALNS

### (44) Score update

```
\pi_k(s+1)=(1-r)\cdot\pi_k(s)+r\cdot\Delta_k(s)
```

### (45) Selection probability

```
P(k)=\frac{\pi_k}{\sum_{j}\pi_j}
```

### (46) Worst Removal saving

```
saving(c)=d_{prev(c),c}+d_{c,next(c)}-d_{prev(c),next(c)}
```

### (47) Shaw Removal relatedness

```
R(i,j)=\alpha\frac{d_{ij}}{d_{\max}}+\beta\frac{|e_i-e_j|}{tw_{\max}}+\gamma\frac{|q_i-q_j|}{q_{\max}}
```

### (48) Route Removal probability

```
P(k)\propto\exp\left(-10\cdot\frac{|\tau_k|}{\max_j|\tau_j|}\right)
```

### (49) Regret-2

```
regret(c)=cost_2(c)-cost_1(c)
```

### (50) Regret-3

```
regret_3(c)=\sum_{j=2}^{3}(cost_j(c)-cost_1(c))
```

### (51) A*-based Build

```
f(c)=w_1\cdot g_{sc}(c)+w_2\cdot tw_{sc}(c)+(1-w_1-w_2)\cdot h_{sc}(c)
```

### (52) SA acceptance

```
accept(\Delta f)\Leftrightarrow\Delta f<0\;\vee\;U(0,1)<\exp\left(-\frac{\Delta f}{T}\right)
```

### (53) SA cooling

```
T_{t+1}=c_T\cdot T_t,\quad c_T=0.995
```

---

## §9 — Dual Archive

### (54) ε-box index

```
box(\mathbf{f})=\left\lfloor\frac{f_m}{\varepsilon+10^{-15}}\right\rfloor,\quad\forall m=1,\ldots,M
```

### (55) ε-Box replacement

```
\mathbf{x}\;replaces\;\mathbf{y}\Leftrightarrow box(\mathbf{x})=box(\mathbf{y})\wedge ASF_{aug}(\mathbf{x})<ASF_{aug}(\mathbf{y})
```

### (56) Diversity pruning

```
remove=\arg\min_{i\in A_{div}} SDE(i)
```

### (57) Sigmoid injection

```
p_{conv}=\sigma\left(\frac{s}{5}-2\right)=\frac{1}{1+e^{-(s/5-2)}}
```

---

## §10 — Adaptive Mechanisms

### (58) Ideal point update

```
ideal_m(t)=\min(ideal_m(t-1),\min_{\mathbf{x}\in P(t)} f_m(\mathbf{x}))
```

### (59) Nadir point update (EMA)

```
nadir_m(t)=(1-\alpha)\cdot nadir_m(t-1)+\alpha\cdot\max_{\mathbf{x}\in P(t)} f_m(\mathbf{x})
```

### (60) Normalised objectives

```
\hat{f}_m(\mathbf{x})=\frac{f_m(\mathbf{x})-ideal_m}{nadir_m-ideal_m+\varepsilon}
```

### (61) Stagnation detection

```
stagnation(t)=\left\lbrace\matrix{s(t-1)+1 & |BestASF(t)-BestASF(t-1)|<10^{-6} \\ 0 & otherwise}\right.
```

### (62) ALNS probability adaptation

```
n_{abs}(t)=\left\lbrace\matrix{\min(0.5, n_{abs}^0+0.05\cdot s(t)) & s(t)>5 \\ n_{abs}^0 & otherwise}\right.
```

### (63) Mutation rate adaptation

```
\mu(t)=0.05+0.10\cdot\frac{t}{T_{\max}}
```

### (64) Polynomial mutation

```
\delta_q=\left\lbrace\matrix{(2r+(1-2r)(1-y)^{\eta_m+1})^{1/(\eta_m+1)}-1 & r<0.5 \\ 1-(2(1-r)+2(r-0.5)(1-y')^{\eta_m+1})^{1/(\eta_m+1)} & otherwise}\right.
```

### (65) Mutation application

```
x_j^{new}=clip(x_j+\delta_q, 0, 0.999)
```

---

## §13 — Thuật toán So sánh

### (66) MOEA/D Tchebycheff

```
g^{te}(\mathbf{x}|\boldsymbol{\lambda},\mathbf{z}^*)=\max_{m=1}^{M}\lbrace\lambda_m|f_m(\mathbf{x})-z_m^*|\rbrace
```

### (67) MOPSO velocity

```
v_i=w\cdot v_i+c_1 r_1(pbest_i-x_i)+c_2 r_2(gbest-x_i)
```

### (68) MOPSO position

```
x_i^{new}=clip(x_i+v_i, 0, 1)
```

### (69) SPEA2 fitness

```
F(i)=\sum_{j:j\prec i} strength(j)+\frac{1}{\sigma_k(i)+2}
```

---

## §14 — Performance Metrics

### (70) Hypervolume

```
HV(A)=\Lambda\left(\bigcup_{\mathbf{x}\in A}[\mathbf{x},\mathbf{r}]\right)
```

### (71) R-HV

```
R\text{-}HV(A)=HV(\lbrace x\in A:x\in ROI\rbrace)
```

### (72) Best ASF

```
BestASF(A)=\min_{\mathbf{x}\in A} ASF(\mathbf{x})
```

### (73) ROI Count

```
ROI\_count(A)=|\lbrace\mathbf{x}\in A:\mathbf{x}\in ROI\rbrace|
```

### (74) IGD

```
IGD(A,P^*)=\frac{1}{|P^*|}\sum_{\mathbf{p}\in P^*}\min_{\mathbf{a}\in A}\|\hat{\mathbf{p}}-\hat{\mathbf{a}}\|_2
```

### (75) Coverage (C-metric)

```
C(A,B)=\frac{|\lbrace\mathbf{b}\in B:\exists\mathbf{a}\in A,\mathbf{a}\preceq\mathbf{b}\rbrace|}{|B|}
```

### (76) Number of Non-dominated Solutions

```
N_{nds}(A)=|\lbrace\mathbf{a}\in A:\nexists\mathbf{b}\in A,\mathbf{b}\prec\mathbf{a}\rbrace|
```

---

## §15 — Thống kê

### (77) Friedman critical difference

```
CD=q_\alpha\sqrt{\frac{k(k+1)}{6N}}
```

### (78) Vargha-Delaney A-measure

```
\hat{A}_{12}=\frac{\sum_{i=1}^{n_1}\sum_{j=1}^{n_2}\mathbb{1}[x_i>y_j]+0.5\cdot\mathbb{1}[x_i=y_j]}{n_1\cdot n_2}
```

---

## §16 — Ablation

### (79) Delta percentage

```
\Delta\%_k=\frac{metric_{V_0}-metric_{V_k}}{|metric_{V_0}|}\times 100
```

---

## §17 — Phân tích Lý thuyết

### (80) Superdiffusion

```
\langle r^2(t)\rangle\sim t^\gamma,\quad\gamma>1
```

### (81) DE variance

```
Var[\mathbf{d}]=2\cdot Var[\mathbf{x}]
```

### (82) Crowding Distance

```
CD(i)=\sum_{m=1}^{M} CD_m(i)
```

### (83) CD limit

```
CD(i)\rightarrow constant\quad\forall i\quad(M\rightarrow\infty)
```

### (84) Non-dominated ratio

```
P(non\text{-}dominated)\approx\frac{(\ln N)^{M-1}}{(M-1)!\cdot N}
```

---

## §18 — Độ phức tạp

### (85) Per-generation

```
O(N^2 M+n_{abs} NR+N|W|M+|A|N)
```

### (86) Total

```
O(G\cdot(N^2 M+n_{abs} NR+N|W|M))
```

### (87) Space

```
O(N^2 M+2N_A\cdot M+|W|\cdot M)
```
