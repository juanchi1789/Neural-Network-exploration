"""Input current generators for neuron simulations."""


def constant_input(time, amplitude):
    """Create a constant input current.

    TODO:
        Return a time-aligned array filled with ``amplitude``.
    """
    raise NotImplementedError("Implement constant input generation.")


def pulse_input(time, amplitude, start_ms, end_ms):
    """Create a pulse input active between ``start_ms`` and ``end_ms``.

    TODO:
        Return zero outside the pulse window and ``amplitude`` inside it.
    """
    raise NotImplementedError("Implement pulse input generation.")


def ramp_input(time, start_amplitude, end_amplitude):
    """Create a linearly increasing or decreasing input current.

    TODO:
        Interpolate from ``start_amplitude`` to ``end_amplitude`` over time.
    """
    raise NotImplementedError("Implement ramp input generation.")


def sinusoidal_input(time, amplitude, frequency_hz, offset=0.0):
    """Create a sinusoidal input current.

    TODO:
        Generate a sinusoid using frequency in Hz and time in milliseconds.
    """
    raise NotImplementedError("Implement sinusoidal input generation.")


def noisy_input(time, mean, std, seed=None):
    """Create a noisy input current.

    TODO:
        Use a random number generator with optional seeding for reproducibility.
    """
    raise NotImplementedError("Implement noisy input generation.")

