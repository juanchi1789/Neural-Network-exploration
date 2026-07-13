"""Vectorized Izhikevich neuron utilities shared by the notebooks."""

from __future__ import annotations

import numpy as np


NEURON_PRESETS = {
    "Regular Spiking": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},
    "Intrinsically Bursting": {"a": 0.02, "b": 0.2, "c": -55.0, "d": 4.0},
    "Chattering": {"a": 0.02, "b": 0.2, "c": -50.0, "d": 2.0},
    "Fast Spiking": {"a": 0.1, "b": 0.2, "c": -65.0, "d": 2.0},
    "Low Threshold Spiking": {"a": 0.02, "b": 0.25, "c": -65.0, "d": 2.0},
}


def population_parameters(n_neurons, preset="Regular Spiking", variability=0.0, rng=None):
    """Return heterogeneous parameter arrays derived from a named preset."""
    if n_neurons < 1:
        raise ValueError("n_neurons must be at least 1")
    if variability < 0:
        raise ValueError("variability must be non-negative")
    if preset not in NEURON_PRESETS:
        raise KeyError(f"Unknown preset: {preset}")
    rng = np.random.default_rng() if rng is None else rng
    base = NEURON_PRESETS[preset]
    params = {
        "a": np.clip(base["a"] * (1 + variability * rng.normal(size=n_neurons)), 0.001, 0.2),
        "b": np.clip(base["b"] * (1 + variability * rng.normal(size=n_neurons)), 0.01, 0.4),
        "c": np.clip(base["c"] + abs(base["c"]) * variability * rng.normal(size=n_neurons), -90, -40),
        "d": np.clip(base["d"] * (1 + variability * rng.normal(size=n_neurons)), 0.1, 20),
    }
    return params


def izhikevich_step(v, u, current, params, dt):
    """Advance one neuron or a vectorized population by one Euler step."""
    v_next = v + dt * (0.04 * v**2 + 5 * v + 140 - u + current)
    u_next = u + dt * params["a"] * (params["b"] * v - u)
    fired = v_next >= 30.0
    v_next = np.where(fired, params["c"], v_next)
    u_next = np.where(fired, u_next + params["d"], u_next)
    return v_next, u_next, fired


def simulate_population(input_current, params, dt=0.5, v_initial=-65.0):
    """Simulate a population receiving a shared or neuron-specific current."""
    current = np.asarray(input_current, dtype=float)
    n_neurons = np.asarray(params["a"]).size
    if current.ndim == 1:
        current = np.broadcast_to(current, (n_neurons, current.size))
    if current.ndim != 2 or current.shape[0] != n_neurons:
        raise ValueError("input_current must have shape (time,) or (neurons, time)")

    n_steps = current.shape[1]
    voltage = np.empty((n_neurons, n_steps), dtype=float)
    recovery = np.empty_like(voltage)
    spikes = np.zeros((n_neurons, n_steps), dtype=bool)
    voltage[:, 0] = v_initial
    recovery[:, 0] = params["b"] * v_initial

    for step in range(1, n_steps):
        v_next, u_next, fired = izhikevich_step(
            voltage[:, step - 1], recovery[:, step - 1], current[:, step - 1], params, dt
        )
        voltage[:, step] = v_next
        recovery[:, step] = u_next
        spikes[:, step] = fired
        voltage[fired, step - 1] = 30.0
    return voltage, recovery, spikes
