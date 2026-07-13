"""Metrics for neural activity and muscle output."""

import numpy as np


def firing_rate(spike_times, duration_ms):
    """Estimate firing rate from spike times.

    """
    if duration_ms <= 0:
        raise ValueError("duration_ms must be positive")
    return np.asarray(spike_times).size / (duration_ms / 1000.0)


def interspike_intervals(spike_times):
    """Compute interspike intervals from spike times.

    """
    return np.diff(np.sort(np.asarray(spike_times, dtype=float)))


def force_summary(force, time):
    """Summarize a muscle force signal.

    """
    force = np.asarray(force, dtype=float)
    time = np.asarray(time, dtype=float)
    if force.shape != time.shape or force.size == 0:
        raise ValueError("force and time must be non-empty matching arrays")
    peak_index = int(np.argmax(force))
    return {
        "max_force": float(force[peak_index]),
        "mean_force": float(force.mean()),
        "time_to_peak_ms": float(time[peak_index]),
    }


def co_contraction_index(agonist_force, antagonist_force):
    """Estimate co-contraction between agonist and antagonist muscles.

    """
    agonist = np.asarray(agonist_force, dtype=float)
    antagonist = np.asarray(antagonist_force, dtype=float)
    denominator = np.maximum(agonist, antagonist).sum()
    return float(np.minimum(agonist, antagonist).sum() / denominator) if denominator else 0.0


def population_activity(spikes, dt=0.5, bin_size_ms=20.0):
    """Count population spikes in fixed-width bins."""
    spikes = np.asarray(spikes)
    steps_per_bin = max(int(round(bin_size_ms / dt)), 1)
    usable = (spikes.shape[1] // steps_per_bin) * steps_per_bin
    activity = spikes[:, :usable].reshape(spikes.shape[0], -1, steps_per_bin).sum(axis=(0, 2))
    times = np.arange(activity.size) * steps_per_bin * dt
    return times, activity


def neural_summary(spikes, time, inhibitory_current=None, bin_size_ms=20.0):
    """Return the comparison metrics used in notebook 04."""
    spikes = np.asarray(spikes, dtype=bool)
    time = np.asarray(time, dtype=float)
    duration_s = (time[-1] - time[0] + (time[1] - time[0])) / 1000.0
    _, activity = population_activity(spikes, time[1] - time[0], bin_size_ms)
    intervals = []
    for row in spikes:
        isi = np.diff(time[row])
        if isi.size:
            intervals.extend(isi.tolist())
    inhibitory_mean = 0.0 if inhibitory_current is None else float(np.mean(inhibitory_current))
    return {
        "spikes_totales": int(spikes.sum()),
        "firing_rate_medio_Hz": float(spikes.sum() / spikes.shape[0] / duration_s),
        "motoneuronas_activas": int(np.count_nonzero(spikes.sum(axis=1))),
        "pico_actividad": int(activity.max(initial=0)),
        "corriente_inhibitoria_media": inhibitory_mean,
        "ISI_medio_ms": float(np.mean(intervals)) if intervals else np.nan,
        "variabilidad_ISI_ms": float(np.std(intervals)) if intervals else np.nan,
    }
