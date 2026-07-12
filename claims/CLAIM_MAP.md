# Claim map

This map separates analytic proofs, model assumptions, and numerical diagnostics. Section and theorem numbers refer to
`paper/main.tex`.

| Claim | Status in the paper | Reproducible diagnostic |
|---|---|---|
| Theorem 2.1: boundary free-energy expansion with coefficient `k_B T a` | Analytic finite-dimensional proof; the entropy nonanalyticity itself is explicitly attributed to prior perturbation theory | The fitted small-time entropy coefficient agrees with the exact leakage coefficient |
| Corollary 2.3: GKLS leakage is a positive sum of squared support-crossing jump amplitudes | Exact analytic identity | The jump-formula residual is asserted below `1e-12` |
| Theorem 3.1: finite/infinite rapid-power dichotomy according to `a>0` or `a=0` | Analytic proof under the fresh-resource-cell ledger stated in the manuscript | Leaking and Hamiltonian-only branches are both tested |
| Theorem 3.2: periodic threshold-corridor law | Analytic periodic-protocol result; not a theorem over arbitrary autonomous controllers | No standalone optimization claim is made by the script |
| Proposition 4.1: quantitative entropy sandwich | Analytic matrix-inequality proof | Used conceptually in the finite-time leakage diagnostic |
| Proposition 5.1: exact dual-rail SSH logical and leakage sum rules | Exact spectral-completeness proof | Direct diagonalization checks both the zero-mode weight and `w(1-w)` sum rule |
| Corollary 5.2: remote-boundary powers `Theta(zeta^(4 ell))` and `Theta(zeta^(2 ell))` | Analytic consequence of the exact zero-mode profile | Fitted logarithmic slopes are asserted within `2e-3` |
| Theorem 6.1: microscopic Davies rate bounds | Analytic conditional theorem under the explicitly stated frequency separation and two-sided bath-envelope assumptions | SSH geometry is checked; the bath envelope remains an input assumption |
| Lemma 6.2 and Corollary 6.3: uniform crossing norm and corridor coefficient | Analytic results under the same model assumptions | No independent numerical certification is claimed |
| Lemmas 7.1–7.2: uniform fixed-time leakage and free-energy sandwich | Analytic semigroup and entropy estimates with constants and dimension growth stated in the paper | A finite model verifies the first-order leakage interval |
| Theorem 7.3: exponent transmutation `min{4m,2m+q}` | Analytic consequence of the preceding conditional microscopic bounds | The figure and slope tests illustrate the two geometric powers |
| Theorem 8.1: noncommuting rapid and wide-membrane limits | Analytic consequence with the order of quantifiers stated explicitly | The right panel of the figure illustrates the fixed-width rapid singularity |

## Explicit non-claims

- No new perturbation theory for von Neumann entropy.
- No uniform microscopic weak-coupling theorem before the Davies limit.
- No derivation of the two-sided bath spectral envelope from a specific reservoir.
- No optimality theorem over arbitrary autonomous or feedback controllers.
- No work-only implementation of the fresh-target-cell ledger.
- No interacting many-body extension.
- No Lean or other proof-assistant formalization.

The numerical suite is a falsification-oriented companion. Passing it does not elevate a conditional analytic statement
into an unconditional microscopic theorem.
