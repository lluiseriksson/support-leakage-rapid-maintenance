"""Create the three-panel figure for the support-leakage paper."""

from __future__ import annotations

import argparse
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm


DEFAULT_OUT = Path(__file__).resolve().parents[1] / "paper" / "support_leakage_phase_diagram.png"


def relative_entropy(p: np.ndarray, pi: np.ndarray) -> float:
    mask = p > 0
    return float(np.sum(p[mask] * np.log(p[mask] / pi[mask])))


def reversible_star_power(ell: int, zeta: float, epsilon: float, tau: float) -> tuple[float, float]:
    nbulk = 2 * ell
    dim = 2 + nbulk
    pi = np.empty(dim)
    pi[0], pi[1] = 0.30, 0.20
    pi[2:] = 0.50 / nbulk
    target = np.zeros(dim)
    target[0], target[1] = 0.63, 0.37

    norm2 = (1 - zeta**2) / (1 - zeta ** (2 * ell + 2))
    w = norm2 * zeta ** (2 * ell)
    logical_scale = w**2
    leak_scale = epsilon * w * (1 - w)

    q = np.zeros((dim, dim))
    # Reversible logical edge through a symmetric conductance.
    conductance = 0.22 * logical_scale
    q[0, 1] = conductance / pi[0]
    q[1, 0] = conductance / pi[1]
    # Reversible support-crossing edges; total outward rate from either code state is leak_scale.
    for i in (0, 1):
        for k in range(2, dim):
            q[i, k] = leak_scale / nbulk
            q[k, i] = pi[i] * q[i, k] / pi[k]
    for i in range(dim):
        q[i, i] = -np.sum(q[i])

    evolved = target @ expm(tau * q)
    power = (relative_entropy(target, pi) - relative_entropy(evolved, pi)) / tau
    leakage = float(np.sum(evolved[2:]))
    return power, leakage


ell = np.arange(2, 31)
zeta = 0.72
norm2 = (1 - zeta**2) / (1 - zeta ** (2 * ell + 2))
w = norm2 * zeta ** (2 * ell)
logical = w**2
leakage_weight = w * (1 - w)

tau_fixed = 0.08
epsilon_soft = 2e-3
exact_power = 0.22 * logical
soft_power = exact_power + epsilon_soft * leakage_weight * np.log(
    1.0 / (tau_fixed * epsilon_soft * leakage_weight)
)

ell_rapid = 8
times = np.logspace(-1, -8, 40)
rapid_power = np.array([reversible_star_power(ell_rapid, zeta, 2e-3, t)[0] for t in times])
_, leakage_at_unit = reversible_star_power(ell_rapid, zeta, 2e-3, 1e-6)
leakage_coefficient = leakage_at_unit / 1e-6
asymptote = leakage_coefficient * np.log(1 / times)
offset = np.mean(rapid_power[-8:] - asymptote[-8:])

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5})
fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.35), constrained_layout=True)

ax = axes[0]
ax.semilogy(ell, logical, "o-", ms=3, lw=1.5, label=r"logical $w_{far}^2$")
ax.semilogy(ell, leakage_weight, "s-", ms=3, lw=1.5, label=r"leakage $w_{far}(1-w_{far})$")
ax.set_xlabel("membrane width ell")
ax.set_ylabel("exact boundary weight")
ax.set_title("(a) Exact SSH sum rules")
ax.grid(True, which="both", alpha=0.25)
ax.legend(frameon=False, fontsize=7.5)

ax = axes[1]
ax.semilogy(ell, exact_power, "o-", ms=3, lw=1.5, label="exact-filter term")
ax.semilogy(ell, soft_power, "s-", ms=3, lw=1.5, label=r"soft-tail asymptotic, $\epsilon=2\times10^{-3}$")
ax.set_xlabel("membrane width ell")
ax.set_ylabel("fixed-period refresh power")
ax.set_title("(b) Exponent transmutation")
ax.grid(True, which="both", alpha=0.25)
ax.legend(frameon=False, fontsize=7.5)

ax = axes[2]
ax.semilogx(times, rapid_power, "o-", ms=3, lw=1.5, label="exact finite model")
ax.semilogx(times, asymptote + offset, "--", lw=1.3, label=r"$a\log(1/\tau)+O(1)$")
ax.invert_xaxis()
ax.set_xlabel("refresh period tau")
ax.set_ylabel("exact refresh power")
ax.set_title(f"(c) Rapid singularity, ell={ell_rapid}")
ax.grid(True, which="both", alpha=0.25)
ax.legend(frameon=False, fontsize=7.5)

fig.suptitle("Soft spectral tails change both the rapid limit and the membrane exponent", fontsize=10.5)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output, dpi=230, bbox_inches="tight", facecolor="white")
print(args.output)
