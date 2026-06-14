"""Metrics for neural activity and muscle output."""


def firing_rate(spike_times, duration_ms):
    """Estimate firing rate from spike times.

    TODO:
        Return spikes per second for a single neuron or neuron pool.
    """
    raise NotImplementedError("Implement firing rate metric.")


def interspike_intervals(spike_times):
    """Compute interspike intervals from spike times.

    TODO:
        Return differences between consecutive spike times.
    """
    raise NotImplementedError("Implement interspike interval metric.")


def force_summary(force, time):
    """Summarize a muscle force signal.

    TODO:
        Return peak, mean, time-to-peak, and optional fatigue-related values.
    """
    raise NotImplementedError("Implement force summary metrics.")


def co_contraction_index(agonist_force, antagonist_force):
    """Estimate co-contraction between agonist and antagonist muscles.

    TODO:
        Define and compute a simple overlap-based co-contraction index.
    """
    raise NotImplementedError("Implement co-contraction index.")

