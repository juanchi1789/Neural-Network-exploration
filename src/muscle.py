"""Simplified muscle force models driven by neural spikes."""

import numpy as np


def twitch_response(time, amplitude=1.0, contraction_time_ms=10.0, relaxation_time_ms=50.0):
    """Create a simplified twitch response kernel.

    Uses a difference of exponentials and scales its peak to ``amplitude``.
    """
    time = np.asarray(time, dtype=float)
    if contraction_time_ms <= 0 or relaxation_time_ms <= contraction_time_ms:
        raise ValueError("Require 0 < contraction_time_ms < relaxation_time_ms")
    response = np.where(
        time >= 0,
        np.exp(-time / relaxation_time_ms) - np.exp(-time / contraction_time_ms),
        0.0,
    )
    peak = response.max(initial=0.0)
    return amplitude * response / peak if peak > 0 else response


def spikes_to_force(
    spikes,
    time,
    muscle_params=None,
    amplitude=1.0,
    tau_rise_ms=10.0,
    tau_decay_ms=50.0,
):
    """Convert spike events into a simplified muscle force signal.

    ``spikes`` may be a binary (neurons, time) array or spike-time values.
    """
    time = np.asarray(time, dtype=float)
    if time.ndim != 1 or time.size < 2:
        raise ValueError("time must contain at least two samples")
    if muscle_params:
        amplitude = muscle_params.get("twitch_amplitude", amplitude)
        tau_rise_ms = muscle_params.get("contraction_time_ms", tau_rise_ms)
        tau_decay_ms = muscle_params.get("relaxation_time_ms", tau_decay_ms)
    spike_data = np.asarray(spikes)
    impulses = np.zeros(time.size, dtype=float)
    if spike_data.ndim == 2:
        if spike_data.shape[1] != time.size:
            raise ValueError("Spike matrix and time must have matching samples")
        impulses = spike_data.sum(axis=0).astype(float)
    else:
        indices = np.searchsorted(time, spike_data.astype(float))
        indices = indices[(indices >= 0) & (indices < time.size)]
        np.add.at(impulses, indices, 1.0)
    kernel_time = np.arange(time.size) * (time[1] - time[0])
    kernel = twitch_response(kernel_time, amplitude, tau_rise_ms, tau_decay_ms)
    return np.convolve(impulses, kernel, mode="full")[: time.size]


def normalize_force(force):
    """Normalize a force trace to [0, 1], preserving an all-zero trace."""
    force = np.asarray(force, dtype=float)
    peak = force.max(initial=0.0)
    return force / peak if peak > 0 else np.zeros_like(force)


def compute_net_force(agonist_force, antagonist_force):
    """Compute a movement proxy from agonist and antagonist forces.

    """
    return np.asarray(agonist_force) - np.asarray(antagonist_force)
