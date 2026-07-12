"""Numerical checks for support leakage, entropy singularity, and SSH sum rules."""

from __future__ import annotations

import math
import numpy as np
from scipy.linalg import expm


def entropy(rho: np.ndarray) -> float:
    vals = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    vals = vals[vals > 1e-14]
    return float(-np.sum(vals * np.log(vals)))


def dissipator_superop(l: np.ndarray) -> np.ndarray:
    d = l.shape[0]
    ident = np.eye(d)
    ld = l.conj().T @ l
    return np.kron(l.conj(), l) - 0.5 * np.kron(ident, ld) - 0.5 * np.kron(ld.T, ident)


def commutator_superop(h: np.ndarray) -> np.ndarray:
    d = h.shape[0]
    ident = np.eye(d)
    return -1j * (np.kron(ident, h) - np.kron(h.T, ident))


def evolve(rho: np.ndarray, generator: np.ndarray, time: float) -> np.ndarray:
    vec = rho.reshape(-1, order="F")
    out = expm(time * generator) @ vec
    result = out.reshape(rho.shape, order="F")
    return (result + result.conj().T) / 2


def ssh_matrix(ell: int, t1: float, t2: float) -> np.ndarray:
    na = ell + 1
    h = np.zeros((2 * ell + 1, 2 * ell + 1))
    for j in range(ell):
        b = na + j
        h[j, b] = h[b, j] = t1
        h[j + 1, b] = h[b, j + 1] = t2
    return h


if __name__ == "__main__":
    # Rank-two target in dimension four. The jump 0 -> 2 leaks out of support.
    rho = np.diag([0.63, 0.37, 0.0, 0.0]).astype(complex)
    jump = np.zeros((4, 4), dtype=complex)
    jump[2, 0] = math.sqrt(0.41)
    internal = np.zeros((4, 4), dtype=complex)
    internal[1, 0] = math.sqrt(0.23)
    generator = dissipator_superop(jump) + dissipator_superop(internal)
    projector = np.diag([1.0, 1.0, 0.0, 0.0])
    qprojector = np.eye(4) - projector

    x = (generator @ rho.reshape(-1, order="F")).reshape((4, 4), order="F")
    leakage = float(np.real(np.trace(qprojector @ x)))
    jump_formula = float(np.real(np.trace(qprojector @ jump @ rho @ jump.conj().T)))
    coefficient_errors = []
    powers = []
    logs = []
    for time in np.logspace(-3, -9, 13):
        evolved = evolve(rho, generator, time)
        power = (entropy(evolved) - entropy(rho)) / time  # H=0, kBT=1.
        coefficient = power / math.log(1.0 / time)
        coefficient_errors.append(abs(coefficient - leakage))
        powers.append(power)
        logs.append(math.log(1.0 / time))
    fit = np.polyfit(logs[-7:], powers[-7:], 1)

    # The a=0 branch: a Hamiltonian rotates the fixed support but preserves rank.
    rotation = np.zeros((4, 4), dtype=complex)
    rotation[2, 0] = rotation[0, 2] = 0.7
    unitary_generator = commutator_superop(rotation)
    rotation_leakage = []
    rotation_entropy_error = []
    for time in np.logspace(-2, -7, 6):
        rotated = evolve(rho, unitary_generator, time)
        rotation_leakage.append(float(np.real(np.trace(qprojector @ rotated))))
        rotation_entropy_error.append(abs(entropy(rotated) - entropy(rho)))

    # A direct finite-time check of the uniform first-order leakage estimate.
    leakage_ratios = []
    for time in np.logspace(-4, -1, 7):
        evolved = evolve(rho, generator, time)
        qtime = float(np.real(np.trace(qprojector @ evolved)))
        leakage_ratios.append(qtime / (leakage * time))

    # Exact SSH completeness identity on each far boundary.
    t1, t2 = 0.37, 1.0
    zeta = t1 / t2
    worst_sum_rule = 0.0
    worst_weight = 0.0
    logical_rates = []
    leakage_rates = []
    ells = np.arange(2, 41)
    for ell in ells:
        h = ssh_matrix(ell, t1, t2)
        vals, vecs = np.linalg.eigh(h)
        zero_index = int(np.argmin(np.abs(vals)))
        psi = vecs[:, zero_index]
        xsite = ell
        w = float(abs(psi[xsite]) ** 2)
        bulk_weight = float(np.sum(np.abs(np.delete(vecs[xsite, :], zero_index)) ** 2))
        exact_w = (1 - zeta**2) * zeta ** (2 * ell) / (1 - zeta ** (2 * ell + 2))
        worst_weight = max(worst_weight, abs(w - exact_w))
        worst_sum_rule = max(worst_sum_rule, abs(w * bulk_weight - w * (1 - w)))
        logical_rates.append(w**2)
        leakage_rates.append(w * (1 - w))

    logical_slope = np.polyfit(ells, np.log(logical_rates), 1)[0]
    leakage_slope = np.polyfit(ells, np.log(leakage_rates), 1)[0]
    expected_logical = 4 * math.log(zeta)
    expected_leakage = 2 * math.log(zeta)

    print(f"leakage coefficient                 = {leakage:.12f}")
    print(f"jump-formula residual               = {abs(leakage-jump_formula):.3e}")
    print(f"asymptotic fitted coefficient       = {fit[0]:.12f}")
    print(f"coefficient fit error               = {abs(fit[0]-leakage):.3e}")
    print(f"smallest direct coefficient error   = {min(coefficient_errors):.3e}")
    print(f"Hamiltonian max entropy drift       = {max(rotation_entropy_error):.3e}")
    print(f"Hamiltonian q(t)/t at smallest t    = {rotation_leakage[-1]/1e-7:.3e}")
    print(f"finite-time leakage ratio range     = [{min(leakage_ratios):.6f}, {max(leakage_ratios):.6f}]")
    print(f"worst SSH weight error              = {worst_weight:.3e}")
    print(f"worst SSH leakage sum-rule residual = {worst_sum_rule:.3e}")
    print(f"logical log-slope residual          = {abs(logical_slope-expected_logical):.3e}")
    print(f"leakage log-slope residual          = {abs(leakage_slope-expected_leakage):.3e}")

    assert abs(leakage - jump_formula) < 1e-12
    assert abs(fit[0] - leakage) < 2e-5
    assert max(rotation_entropy_error) < 1e-12
    assert rotation_leakage[-1] / 1e-7 < 1e-6
    assert min(leakage_ratios) > 0.5 and max(leakage_ratios) < 1.5
    assert worst_weight < 1e-12
    assert worst_sum_rule < 1e-12
    assert abs(logical_slope - expected_logical) < 2e-3
    assert abs(leakage_slope - expected_leakage) < 2e-3
