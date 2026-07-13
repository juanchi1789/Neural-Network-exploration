"""Input current generators for neuron simulations."""

import numpy as np


def constant_input(time, amplitude):
    """Create a constant input current.

    The current is active for every supplied sample.
    """
    return np.full_like(np.asarray(time, dtype=float), amplitude, dtype=float)


def pulse_input(time, amplitude, start_ms, end_ms):
    """Create a pulse input active between ``start_ms`` and ``end_ms``.

    """
    time = np.asarray(time, dtype=float)
    return amplitude * ((time >= start_ms) & (time <= end_ms))


def ramp_input(time, start_amplitude, end_amplitude):
    """Create a linearly increasing or decreasing input current.

    """
    time = np.asarray(time, dtype=float)
    if time.size == 0:
        return np.array([], dtype=float)
    return np.linspace(start_amplitude, end_amplitude, time.size)


def sinusoidal_input(time, amplitude, frequency_hz, offset=0.0):
    """Create a sinusoidal input current.

    """
    time = np.asarray(time, dtype=float)
    return offset + amplitude * np.sin(2 * np.pi * frequency_hz * time / 1000.0)


def noisy_input(time, mean, std, seed=None):
    """Create a noisy input current.

    """
    rng = np.random.default_rng(seed)
    return rng.normal(mean, std, size=np.asarray(time).shape)


def generate_input(
    time,
    input_type="motor_plan",
    amplitude=10.0,
    start_ms=100.0,
    end_ms=None,
    frequency_hz=5.0,
):
    """Generate the input families introduced in notebooks 01 and 02."""
    time = np.asarray(time, dtype=float)
    if time.ndim != 1 or time.size == 0:
        raise ValueError("time must be a non-empty one-dimensional array")
    end_ms = float(time[-1]) if end_ms is None else float(end_ms)
    if end_ms <= start_ms:
        raise ValueError("end_ms must be greater than start_ms")
    active = (time >= start_ms) & (time <= end_ms)
    result = np.zeros_like(time)

    if input_type == "constant":
        result[active] = amplitude
    elif input_type == "pulse":
        result[(time >= start_ms) & (time <= min(start_ms + 100.0, end_ms))] = amplitude
    elif input_type == "ramp":
        result[active] = amplitude * (time[active] - start_ms) / (end_ms - start_ms)
    elif input_type == "sinusoidal":
        phase = 2 * np.pi * frequency_hz * (time[active] - start_ms) / 1000.0
        result[active] = amplitude * (0.5 + 0.5 * np.sin(phase))
    elif input_type == "motor_plan":
        duration = end_ms - start_ms
        transition = min(200.0, duration / 2.0)
        rise_end, fall_start = start_ms + transition, end_ms - transition
        rise = (time >= start_ms) & (time < rise_end)
        hold = (time >= rise_end) & (time < fall_start)
        fall = (time >= fall_start) & (time <= end_ms)
        result[rise] = amplitude * (time[rise] - start_ms) / transition
        result[hold] = amplitude
        result[fall] = amplitude * (end_ms - time[fall]) / transition
    else:
        raise ValueError(f"Unknown input_type: {input_type}")
    return result
