"""Connectivity and exponential synapse helpers."""

import numpy as np


def create_weight_matrix(n_sources, n_targets, probability, weight, rng=None):
    """Create a non-negative source-by-target random weight matrix."""
    if n_sources < 1 or n_targets < 1:
        raise ValueError("Both populations must contain at least one neuron")
    if not 0 <= probability <= 1 or weight < 0:
        raise ValueError("probability must be in [0, 1] and weight non-negative")
    rng = np.random.default_rng() if rng is None else rng
    return (rng.random((n_sources, n_targets)) < probability).astype(float) * weight


def synaptic_decay(dt, tau_ms):
    """Return the exact exponential decay factor for one time step."""
    if dt <= 0 or tau_ms <= 0:
        raise ValueError("dt and tau_ms must be positive")
    return np.exp(-dt / tau_ms)


def synaptic_current(weight_matrix, source_state):
    """Map source synaptic states to currents at target neurons."""
    return np.asarray(weight_matrix, dtype=float).T @ np.asarray(source_state, dtype=float)
