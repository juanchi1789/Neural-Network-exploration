"""Simplified muscle force models driven by neural spikes."""


def twitch_response(time, amplitude, contraction_time_ms, relaxation_time_ms):
    """Create a simplified twitch response kernel.

    TODO:
        Build a twitch curve suitable for convolution with spike trains.
    """
    raise NotImplementedError("Implement muscle twitch response.")


def spikes_to_force(spike_times, time, muscle_params):
    """Convert spike events into a simplified muscle force signal.

    TODO:
        Convert spikes to impulses and convolve them with a twitch response.
    """
    raise NotImplementedError("Implement spike-to-force conversion.")


def compute_net_force(agonist_force, antagonist_force):
    """Compute a movement proxy from agonist and antagonist forces.

    TODO:
        Subtract antagonist force from agonist force and normalize if needed.
    """
    raise NotImplementedError("Implement net force computation.")

