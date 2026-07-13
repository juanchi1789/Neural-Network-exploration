"""Plotting and animation helpers for the project."""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import animation
from matplotlib.patches import Ellipse


def plot_voltage_trace(time, voltage, spike_times=None, ax=None):
    """Plot membrane voltage over time.

    """
    ax = plt.gca() if ax is None else ax
    ax.plot(time, voltage)
    if spike_times is not None:
        ax.vlines(spike_times, 25, 30, color="tab:red", linewidth=0.8)
    ax.set(xlabel="Tiempo (ms)", ylabel="v (mV)")
    ax.grid(alpha=0.25)
    return ax


def plot_raster(spike_times_by_neuron, ax=None):
    """Plot a spike raster for a neuron pool.

    """
    ax = plt.gca() if ax is None else ax
    for index, times in enumerate(spike_times_by_neuron):
        ax.vlines(times, index + 0.6, index + 1.4, linewidth=0.7)
    ax.set(xlabel="Tiempo (ms)", ylabel="Neurona", ylim=(0.5, len(spike_times_by_neuron) + 0.5))
    return ax


def plot_muscle_force(time, force, ax=None):
    """Plot muscle force over time.

    """
    ax = plt.gca() if ax is None else ax
    ax.plot(time, force, color="tab:red")
    ax.set(xlabel="Tiempo (ms)", ylabel="Fuerza (u.a.)")
    ax.grid(alpha=0.25)
    return ax


def animate_muscle_contraction(time, force, output_path=None):
    """Create a simple animation of muscle contraction.

    """
    time = np.asarray(time)
    force = np.asarray(force, dtype=float)
    peak = force.max(initial=0.0)
    normalized = force / peak if peak else np.zeros_like(force)
    frame_indices = np.linspace(0, len(time) - 1, min(120, len(time)), dtype=int)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.set(xlim=(-2.2, 2.2), ylim=(-1.3, 1.3), aspect="equal")
    ax.axis("off")
    muscle = Ellipse((0, 0), width=3.6, height=0.55, color="salmon", ec="firebrick")
    ax.add_patch(muscle)
    label = ax.text(0, -1.0, "", ha="center")

    def update(frame):
        activation = normalized[frame]
        muscle.width = 3.6 - 1.4 * activation
        muscle.height = 0.55 + 0.75 * activation
        label.set_text(f"t = {time[frame]:.0f} ms | activación = {activation:.2f}")
        return muscle, label

    result = animation.FuncAnimation(fig, update, frames=frame_indices, interval=50, blit=True)
    if output_path:
        result.save(output_path)
    return result


def spike_times_from_matrix(spikes, time):
    """Convert a binary spike matrix to one time array per neuron."""
    spikes = np.asarray(spikes, dtype=bool)
    time = np.asarray(time)
    return [time[row] for row in spikes]


def plot_renshaw_circuit(weight_mn_to_r, weight_r_to_mn, ax=None, show_labels=True):
    """Plot the two-population MN/Renshaw architecture."""
    ax = plt.gca() if ax is None else ax
    w_mr, w_rm = np.asarray(weight_mn_to_r), np.asarray(weight_r_to_mn)
    motor = [f"MN{i+1}" for i in range(w_mr.shape[0])]
    renshaw = [f"R{i+1}" for i in range(w_mr.shape[1])]
    graph = nx.DiGraph()
    positions = {node: (i, 1) for i, node in enumerate(motor)}
    positions.update({node: (i * max(len(motor)-1, 1) / max(len(renshaw)-1, 1), 0) for i, node in enumerate(renshaw)})
    graph.add_nodes_from(motor + renshaw)
    excitatory = [(motor[i], renshaw[j]) for i, j in zip(*np.nonzero(w_mr))]
    inhibitory = [(renshaw[i], motor[j]) for i, j in zip(*np.nonzero(w_rm))]
    graph.add_edges_from(excitatory + inhibitory)
    nx.draw_networkx_nodes(graph, positions, nodelist=motor, node_color="#9ecae1", node_size=360, ax=ax)
    nx.draw_networkx_nodes(graph, positions, nodelist=renshaw, node_color="#fdae6b", node_size=430, ax=ax)
    nx.draw_networkx_edges(graph, positions, edgelist=excitatory, edge_color="tab:blue", alpha=.25, arrowsize=8, ax=ax)
    nx.draw_networkx_edges(graph, positions, edgelist=inhibitory, edge_color="tab:red", style="dashed", alpha=.25, arrowsize=8, ax=ax)
    if show_labels:
        nx.draw_networkx_labels(graph, positions, font_size=7, ax=ax)
    ax.set_title("Circuito MN–Renshaw")
    ax.axis("off")
    return ax


def _flow_box(ax, center, text, color, width=2.0, height=0.72):
    """Draw one rounded box used by the explanatory flow diagrams."""
    from matplotlib.patches import FancyBboxPatch

    x, y = center
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor=color, edgecolor="0.2", linewidth=1.2,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=10, color="white", weight="bold")
    return patch


def _flow_arrow(ax, start, end, color="0.25", label=None, curve=0.0):
    """Draw a labelled arrow between two flow-diagram boxes."""
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(arrowstyle="-|>", color=color, lw=2, connectionstyle=f"arc3,rad={curve}"),
    )
    if label:
        x = (start[0] + end[0]) / 2
        horizontal = abs(start[1] - end[1]) < 1e-9 and curve == 0
        offset = 0.5 if horizontal else (0.28 if curve >= 0 else -0.28)
        y = (start[1] + end[1]) / 2 + offset
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5, color=color, weight="bold")


def plot_renshaw_signal_flow(ax=None):
    """Explain how a motor spike becomes recurrent Renshaw inhibition."""
    if ax is None:
        _, ax = plt.subplots(figsize=(13, 4.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")

    _flow_box(ax, (1.3, 3.5), "Comando\nmotor", "#4c78a8", 1.7)
    _flow_box(ax, (4.0, 3.5), "Pool de\nmotoneuronas", "#1f77b4", 2.2)
    _flow_box(ax, (7.1, 3.5), "Spikes MN +\nestado sináptico", "#17becf", 2.35)
    _flow_box(ax, (10.3, 3.5), "Pool de\nRenshaw", "#f2a65a", 2.0)
    _flow_box(ax, (7.1, 1.2), "Corriente inhibitoria\nI_R→MN", "#d9534f", 2.6)
    _flow_box(ax, (4.0, 1.2), "Se resta del input\nde cada MN", "#a94442", 2.35)

    _flow_arrow(ax, (2.18, 3.5), (2.88, 3.5), "#4c78a8", "I_motor")
    _flow_arrow(ax, (5.12, 3.5), (5.9, 3.5), "#17becf", "spike")
    _flow_arrow(ax, (8.3, 3.5), (9.25, 3.5), "#17becf", "W_MN_to_R")
    _flow_arrow(ax, (10.3, 3.1), (8.1, 1.58), "#d9534f", "W_R_to_MN", curve=-0.12)
    _flow_arrow(ax, (5.78, 1.2), (5.2, 1.2), "#d9534f", "− I_Renshaw")
    _flow_arrow(ax, (3.55, 1.58), (3.55, 3.08), "#d9534f", "feedback", curve=-0.2)

    ax.set_title(
        "Flujo causal simplificado: la motoneurona activa a Renshaw y Renshaw devuelve inhibición",
        fontsize=13, weight="bold", pad=12,
    )
    ax.text(
        6, 0.25,
        "Las matrices solo indican qué neurona origen se conecta con qué destino y con qué magnitud.",
        ha="center", fontsize=10, color="0.3",
    )
    return ax


def plot_spikes_to_force_flow(ax=None):
    """Explain the spike-train to twitch-convolution to force pipeline."""
    if ax is None:
        _, ax = plt.subplots(figsize=(13, 4.2))
    ax.set_xlim(0, 13); ax.set_ylim(0, 4.2); ax.axis("off")

    centers = [(1.25, 2.4), (4.0, 2.4), (7.0, 2.4), (10.0, 2.4), (12.1, 2.4)]
    labels = [
        "Matriz de\nspikes", "Tren poblacional\nde impulsos", "Kernel twitch\nh(t)",
        "Convolución\nimpulsos * h(t)", "Fuerza\ntotal",
    ]
    colors = ["#4c78a8", "#1f77b4", "#f2a65a", "#8b6bb1", "#d9534f"]
    widths = [1.9, 2.25, 1.75, 2.3, 1.55]
    for center, label, color, width in zip(centers, labels, colors, widths):
        _flow_box(ax, center, label, color, width)
    arrow_labels = ["sumar MN", "cada spike", "sumar en tiempo", "resultado"]
    for index, (left, right, label) in enumerate(zip(centers[:-1], centers[1:], arrow_labels)):
        start = (left[0] + widths[index] / 2 + 0.04, left[1])
        end = (right[0] - widths[index + 1] / 2 - 0.04, right[1])
        _flow_arrow(ax, start, end, "0.25", label)

    ax.text(7.0, 1.25, "subida rápida + relajación lenta", ha="center", fontsize=10, color="#a65f21")
    ax.text(10.0, 1.25, "superposición temporal de twitches", ha="center", fontsize=10, color="#68498a")
    ax.set_title("Cómo se convierten los spikes en una señal muscular simplificada", fontsize=13, weight="bold")
    ax.text(
        6.5, 0.35,
        "No se calcula movimiento ni fuerza física real: se obtiene un proxy de activación en unidades arbitrarias.",
        ha="center", fontsize=10, color="0.3",
    )
    return ax
