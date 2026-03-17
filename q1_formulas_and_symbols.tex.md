# Q1 Formulas and Symbols

This file provides a LaTeX-ready symbol list and equation bank for the paper.

Reference policy:

- use recent support from `q1_evidence_matrix_2024_2026.md` where possible,
- use foundational keys only when the original concept needs its first source.

## Symbol Table

| Symbol | Meaning | Code anchor |
|---|---|---|
| $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ | VRPTW graph | `core/problem.py` |
| $0$ | Depot node | `core/problem.py` |
| $i, j$ | Customer indices | `core/problem.py` |
| $q_i$ | Demand of customer $i$ | `core/problem.py` |
| $[e_i, l_i]$ | Time window of customer $i$ | `core/problem.py` |
| $s_i$ | Service time at customer $i$ | `core/problem.py` |
| $Q$ | Vehicle capacity | `core/problem.py` |
| $d_{ij}$ | Euclidean distance from $i$ to $j$ | `core/problem.py` |
| $t_{ij}$ | Travel time from $i$ to $j$ | `core/problem.py` |
| $X = (x_1,\dots,x_{n_{\mathrm{var}}})$ | Random-key vector | `core/solution.py` |
| $n_{\mathrm{var}}$ | Number of decision variables | `core/solution.py` |
| $R_k$ | Route $k$ | `core/solution.py` |
| $K$ | Number of used routes | `core/objectives.py` |
| $T_k$ | Completion time of route $k$ | `core/solution.py` |
| $L_k$ | Load of route $k$ | `core/objectives.py` |
| $\mathbf{f}(x)$ | Objective vector of solution $x$ | `core/objectives.py` |
| $\mathbf{g}$ | Preference reference point | `core/preference.py` |
| $\mathbf{w}$ | Preference weight vector | `core/preference.py` |
| $\delta$ | ROI radius factor | `core/preference.py` |
| $\epsilon$ | Epsilon-box archive tolerance | `algorithm/inssso.py`, `config/params.yaml` |
| $\mathrm{ASF}$ | Achievement scalarizing function | `core/preference.py` |
| $\mathrm{SDE}$ | Shift-based density estimation | `algorithm/crowding.py` |
| $\mathcal{A}_{\mathrm{conv}}$ | Convergence archive | `algorithm/inssso.py` |
| $\mathcal{A}_{\mathrm{div}}$ | Diversity archive | `algorithm/inssso.py` |

## Problem and Encoding

### Decision-vector size

```latex
n_{\mathrm{var}} = |\mathcal{C}| + |\mathcal{V}_{\mathrm{veh}}| - 1
```

Mapping: `core/solution.py:8-15`, `core/solution.py:52-63`

### Random-key decoding

Let

```latex
\mathbf{z} = \mathrm{argsort}(X) + 1.
```

Every entry $z_r > |\mathcal{C}|$ is treated as a route separator; all remaining entries are customer IDs.

```latex
R_1 \mid R_2 \mid \cdots \mid R_K
\Longleftarrow
\mathbf{z}
```

Mapping: `core/solution.py:116-134`

### Reverse encoding from routes

The reverse construction enforces:

```latex
\mathrm{argsort}(X) + 1 = \mathbf{z}_{\mathrm{seq}},
```

where $\mathbf{z}_{\mathrm{seq}}$ is the customer-and-separator sequence built from the route set.

Mapping: `core/solution.py:66-113`

## Feasibility Model

### Capacity feasibility

For each route $R_k$,

```latex
\sum_{i \in R_k} q_i \le Q.
```

Mapping: `core/constraints.py:12-15`, `core/solution.py:210-214`

### Time-window service start

Let vehicle arrival at customer $i$ be $a_i$. Service begins at:

```latex
b_i = \max(a_i, e_i).
```

Feasibility requires:

```latex
b_i \le l_i.
```

Mapping: `core/constraints.py:28-36`, `core/solution.py:216-224`

### Depot return feasibility

After servicing customer $i$, the route must still be able to return to the depot:

```latex
b_i + s_i + t_{i0} \le l_0.
```

Mapping: `core/constraints.py:38-42`, `core/solution.py:226-231`

### Waiting time at customer

```latex
w_i = \max(0, e_i - a_i).
```

Mapping: `core/solution.py:268-273`

### Route completion time

For route $R_k$ ending at customer $j_k$,

```latex
T_k = b_{j_k} + s_{j_k} + t_{j_k 0}.
```

Mapping: `core/solution.py:278-280`

## Five Objective Functions

Let $U(x)$ be the number of unserved customers and $P = 10^4$ the per-customer penalty.

```latex
\mathrm{pen}(x) = P \cdot U(x).
```

Mapping: `core/objectives.py:24`, `core/objectives.py:141`

### Objective 1: number of used vehicles

```latex
Z_1(x) = K(x) + \mathrm{pen}(x).
```

Mapping: `core/objectives.py:144`

### Objective 2: total travel distance

```latex
Z_2(x) = \sum_{k=1}^{K} \sum_{(i,j) \in R_k} d_{ij} + \mathrm{pen}(x).
```

Implementation detail: the route cost includes depot departure and depot return.

Mapping: `core/solution.py:262-279`, `core/objectives.py:147-160`

### Objective 3: total waiting time

```latex
Z_3(x) = \sum_{k=1}^{K} \sum_{i \in R_k} w_i + \mathrm{pen}(x).
```

Mapping: `core/objectives.py:148-160`

### Objective 4: load balance

Let

```latex
L_k = \sum_{i \in R_k} q_i.
```

Then

```latex
Z_4(x) = \max_k L_k - \min_k L_k + \mathrm{pen}(x).
```

Mapping: `core/objectives.py:152-165`

### Objective 5: makespan

```latex
Z_5(x) = \max_k T_k + \mathrm{pen}(x).
```

Mapping: `core/objectives.py:167-170`

## Preference Layer

### Weight normalization

```latex
\mathbf{w} \leftarrow \frac{\mathbf{w}}{\sum_{m=1}^{M} w_m}.
```

Mapping: `core/preference.py:37-41`

### Achievement scalarizing function

```latex
\mathrm{ASF}(\mathbf{f}(x); \mathbf{g}, \mathbf{w}) =
\max_{m=1,\dots,M} \left\{ w_m \left(f_m(x) - g_m\right) \right\}.
```

Mapping: `core/preference.py:47-56`

### Augmented ASF

```latex
\mathrm{ASF}_{\mathrm{aug}}(\mathbf{f}(x)) =
\max_m \left\{ w_m (f_m(x)-g_m) \right\}
 + \rho \sum_{m=1}^{M} w_m (f_m(x)-g_m),
\quad \rho = 10^{-3}.
```

Mapping: `core/preference.py:58-68`

### Weighted distance from the reference point

```latex
D_w(\mathbf{f}(x), \mathbf{g}) =
\sqrt{\sum_{m=1}^{M} \left[w_m\left(f_m(x)-g_m\right)\right]^2 }.
```

Mapping: `core/preference.py:70-75`

### Region of interest (ROI)

Let $\mathbf{z}^{\ast}$ and $\mathbf{z}^{\mathrm{nad}}$ be ideal and nadir estimates. Then:

```latex
\sum_{m=1}^{M}
\left(
\frac{w_m \left(f_m(x)-g_m\right)}
{\delta \left(z_m^{\mathrm{nad}} - z_m^{\ast}\right)}
\right)^2 \le 1.
```

Mapping: `core/preference.py:77-99`

### Auto-calibration of the reference point

With ideal vector $\mathbf{z}^{\ast}$ and per-objective 10th percentile $\mathbf{p}_{10}$,

```latex
\mathbf{g}_{\mathrm{new}}
=
\mathbf{z}^{\ast}
 + \eta \cdot \max(\mathbf{p}_{10} - \mathbf{z}^{\ast}, \mathbf{0}),
\quad \eta = 0.1.
```

The implementation also forces a minimum shift:

```latex
\mathbf{g}_{\mathrm{new}}
\leftarrow
\max\left(
\mathbf{g}_{\mathrm{new}},
\mathbf{z}^{\ast} + 0.01 \cdot (\mathbf{z}^{\max} - \mathbf{z}^{\ast})
\right).
```

Mapping: `algorithm/inssso.py:299-347`

## Many-Objective Density and Direction Model

### Objective normalization

```latex
\hat{f}_m(x) =
\frac{f_m(x) - z_m^{\ast}}
{z_m^{\mathrm{nad}} - z_m^{\ast} + \varepsilon}.
```

Mapping: `core/objectives.py:28-68`, `algorithm/reference_dirs.py:124-138`

### Shift-based density estimation

For solutions $i$ and $j$, define the shifted point component-wise:

```latex
\tilde{f}_{m}^{(i,j)} = \max\left(\hat{f}_{m}^{(j)}, \hat{f}_{m}^{(i)}\right).
```

The shifted distance is:

```latex
d_{\mathrm{SDE}}(i,j)
=
\left\|
\tilde{\mathbf{f}}^{(i,j)} - \hat{\mathbf{f}}^{(i)}
\right\|_2.
```

Then

```latex
\mathrm{SDE}(i) = \min_{j \ne i} d_{\mathrm{SDE}}(i,j).
```

Mapping: `algorithm/crowding.py:20-58`

### Preference-biased reference directions

Uniform directions are generated on the simplex and then blended toward the normalized preference center:

```latex
\mathbf{c} = \frac{\mathbf{w}}{\sum_{m=1}^{M} w_m},
\qquad
\mathbf{r}' = (1-\alpha)\mathbf{r} + \alpha \mathbf{c},
\quad \alpha = 0.5.
```

The shifted directions are renormalized by:

```latex
\mathbf{r}' \leftarrow \frac{\mathbf{r}'}{\sum_{m=1}^{M} r'_m}.
```

Mapping: `algorithm/reference_dirs.py:42-98`

### Perpendicular-distance association to reference directions

For normalized objective vector $\hat{\mathbf{f}}(x)$ and reference direction $\mathbf{r}$:

```latex
\mathrm{proj}(\hat{\mathbf{f}}, \mathbf{r})
=
\frac{\hat{\mathbf{f}}^\top \mathbf{r}}{\mathbf{r}^\top \mathbf{r}} \mathbf{r},
```

```latex
d_{\perp}(\hat{\mathbf{f}}, \mathbf{r})
=
\left\|
\hat{\mathbf{f}} - \mathrm{proj}(\hat{\mathbf{f}}, \mathbf{r})
\right\|_2.
```

Mapping: `algorithm/reference_dirs.py:141-173`

## Enhanced SSO Update

The implemented update partitions the decision dimensions into exploitation, conservation, Levy exploration, and DE-style perturbation:

```latex
x_{i,j}^{\mathrm{new}} =
\begin{cases}
x_{g,j}, & \rho_j \le c_g, \\
x_{i,j}, & c_g < \rho_j \le c_w, \\
x_{i,j} + 0.01 \, L_j \, (x_{g,j} - x_{i,j}), & c_w < \rho_j \le c_{\ell}, \\
x_{i,j} + F(x_{r_1,j} - x_{r_2,j}), & \rho_j > c_{\ell}.
\end{cases}
```

with

```latex
c_{\ell} = c_w + 0.6(1-c_w), \qquad F = 0.5.
```

Mapping: `algorithm/inssso.py:416-463`

### Levy step via Mantegna's algorithm

```latex
\sigma_u =
\left(
\frac{
\Gamma(1+\beta)\sin(\pi \beta / 2)
}{
\Gamma((1+\beta)/2)\beta 2^{(\beta-1)/2}
}
\right)^{1/\beta},
\qquad \beta = 1.5,
```

```latex
u \sim \mathcal{N}(0, \sigma_u^2),
\quad
v \sim \mathcal{N}(0, 1),
\quad
L = \frac{u}{|v|^{1/\beta}}.
```

Mapping: `algorithm/inssso.py:466-490`

## Mutation and Adaptive Control

### Polynomial mutation

The implementation follows the standard bounded polynomial-mutation pattern on random keys:

```latex
x_j' = \mathrm{clip}(x_j + \Delta_q, 0, 0.999),
```

with distribution index

```latex
\eta_m = 20.
```

Mapping: `algorithm/inssso.py:492-531`

### Adaptive ALNS probability

The effective ALNS trigger probability is:

```latex
n_{\mathrm{abs}} =
\begin{cases}
\min(0.5, n_{\mathrm{abs}}^0 + 0.05 s), & s > 5, \\
n_{\mathrm{abs}}^0, & s \le 5,
\end{cases}
```

where $s$ is the stagnation counter.

Mapping: `algorithm/inssso.py:592-601`

### Adaptive mutation rate

Let $p \in [0,1]$ be normalized elapsed-time progress:

```latex
\mu(p) = 0.05 + 0.10 p.
```

Mapping: `algorithm/inssso.py:603-605`

## ALNS Core

### Adaptive operator-selection probability

For operator score $\pi_k$:

```latex
\Pr(k) = \frac{\pi_k}{\sum_j \pi_j}.
```

Mapping: `algorithm/abs_search.py:54-57`

### Segment-end weight update

```latex
\pi_k^{(s+1)} = (1-r)\pi_k^{(s)} + r \bar{\sigma}_k^{(s)},
```

where $r$ is the reaction factor and $\bar{\sigma}_k^{(s)}$ is the average reward collected in the segment.

Mapping: `algorithm/abs_search.py:59-70`

### Shaw-relatedness score

```latex
\mathrm{Rel}(i,j)
=
\alpha \frac{d_{ij}}{d_{\max}}
 + \beta \frac{|e_i - e_j|}{\mathrm{TW}_{\max}}
 + \gamma \frac{|q_i - q_j|}{q_{\max}},
```

with $(\alpha,\beta,\gamma) = (0.4, 0.3, 0.3)$ in the current implementation.

Mapping: `algorithm/abs_search.py:148-177`

### Regret-$k$ insertion

For customer $c$ with sorted feasible insertion costs $c_1(c) \le c_2(c) \le \cdots$:

```latex
\mathrm{regret}_k(c) = \sum_{j=2}^{k} \left(c_j(c) - c_1(c)\right).
```

Mapping: `algorithm/abs_search.py:260-303`

## Dual Archive

### Epsilon-box identifier

```latex
\mathrm{box}_{\epsilon}(\mathbf{f}(x))
=
\left\lfloor \frac{\mathbf{f}(x)}{\epsilon + 10^{-15}} \right\rfloor.
```

Mapping: `algorithm/inssso.py:87-89`

### Archive preference replacement in the same epsilon box

If two solutions fall into the same box, keep the one with smaller augmented ASF:

```latex
x \prec_{\mathrm{box}} y
\Longleftrightarrow
\mathrm{ASF}_{\mathrm{aug}}(x) < \mathrm{ASF}_{\mathrm{aug}}(y).
```

Mapping: `algorithm/inssso.py:110-130`

### Diversity-archive pruning

When the diversity archive exceeds its limit, preserve solutions with larger SDE:

```latex
\mathcal{A}_{\mathrm{div}}
\leftarrow
\mathrm{TopK}_{\max\_size}\left(\mathrm{SDE}\right).
```

Mapping: `algorithm/inssso.py:170-177`

### Adaptive archive injection

The convergence-archive injection probability is logistic in the stagnation count $s$:

```latex
p_{\mathrm{conv}}(s)
=
\frac{1}{1 + \exp(-s/5 + 2)}.
```

Mapping: `algorithm/inssso.py:197-212`

## Performance Indicators

### Coverage

```latex
\mathrm{Cov}(P_{\mathrm{approx}}, P_{\mathrm{true}})
=
\frac{
\left|
\left\{
\mathbf{v} \in P_{\mathrm{true}}
:
\exists \mathbf{u} \in P_{\mathrm{approx}},\ \mathbf{u} \preceq \mathbf{v}
\right\}
\right|
}
{|P_{\mathrm{true}}|}.
```

Mapping: `benchmark/metrics.py:21-37`

### IGD

```latex
\mathrm{IGD}(P_{\mathrm{approx}}, P_{\mathrm{true}})
=
\frac{1}{|P_{\mathrm{true}}|}
\sum_{\mathbf{v} \in P_{\mathrm{true}}}
\min_{\mathbf{u} \in P_{\mathrm{approx}}}
\| \mathbf{u} - \mathbf{v} \|_2.
```

Mapping: `benchmark/metrics.py:40-60`

### Hypervolume

```latex
\mathrm{HV}(P)
=
\lambda \left(
\bigcup_{\mathbf{u} \in P}
[\mathbf{u}, \mathbf{r}]
\right),
```

where $\mathbf{r}$ is the reference point and $\lambda$ is the Lebesgue measure.

Mapping: `benchmark/metrics.py:63-81`

### Reference-restricted hypervolume

```latex
\mathrm{RHV}(P)
=
\mathrm{HV}\left(\{\mathbf{u} \in P \mid \mathbf{u} \in \mathrm{ROI}\}\right).
```

Mapping: `benchmark/metrics.py:84-120`

### Best ASF in the approximation set

```latex
\mathrm{BestASF}(P) = \min_{\mathbf{u} \in P} \mathrm{ASF}(\mathbf{u}).
```

Mapping: `benchmark/metrics.py:123-130`

## Equation Policy for the Paper

1. Treat the equations above as the canonical LaTeX bank for the first full manuscript draft.
2. When a formula is an exact implementation mirror, keep the notation close to the code.
3. When a formula is a paper-friendly abstraction of the code, state that it follows the implementation logic.
4. Do not include any R-dominance survival equation in the main algorithm pseudocode unless the implementation is updated to use it in the main loop.
