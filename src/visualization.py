"""Plotting and animation helpers for the project."""


def plot_voltage_trace(time, voltage, spike_times=None, ax=None):
    """Plot membrane voltage over time.

    TODO:
        Add spike markers and return the Matplotlib axis.
    """
    raise NotImplementedError("Implement voltage trace plotting.")


def plot_raster(spike_times_by_neuron, ax=None):
    """Plot a spike raster for a neuron pool.

    TODO:
        Draw one row per neuron and mark each spike time.
    """
    raise NotImplementedError("Implement raster plotting.")


def plot_muscle_force(time, force, ax=None):
    """Plot muscle force over time.

    TODO:
        Add labels, units, and optional summary annotations.
    """
    raise NotImplementedError("Implement muscle force plotting.")


def animate_muscle_contraction(time, force, output_path=None):
    """Create a simple animation of muscle contraction.

    TODO:
        Use simulated force to drive a 2D muscle or limb visualization.
    """
    raise NotImplementedError("Implement muscle contraction animation.")

