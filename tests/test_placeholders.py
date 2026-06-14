"""Basic scaffold tests.

These tests only verify that the placeholder API exists. They are not intended
to validate simulation behavior yet.
"""

from src import config
from src import inhibition
from src import inputs
from src import metrics
from src import muscle
from src import network
from src import neuron_models
from src import visualization


def test_default_configuration_exists():
    assert config.SIMULATION_TIME_MS > 0
    assert config.TIME_STEP_MS > 0
    assert "a" in config.DEFAULT_IZHIKEVICH_PARAMS
    assert "twitch_amplitude" in config.DEFAULT_MUSCLE_PARAMS


def test_placeholder_functions_are_available():
    functions = [
        neuron_models.izhikevich_step,
        neuron_models.simulate_single_neuron,
        neuron_models.reset_neuron,
        inputs.constant_input,
        inputs.pulse_input,
        inputs.ramp_input,
        inputs.sinusoidal_input,
        inputs.noisy_input,
        network.create_motor_neuron_pool,
        network.simulate_motor_pool,
        network.compute_population_activity,
        muscle.twitch_response,
        muscle.spikes_to_force,
        muscle.compute_net_force,
        inhibition.renshaw_feedback,
        inhibition.reciprocal_inhibition,
        inhibition.apply_inhibitory_current,
        metrics.firing_rate,
        metrics.interspike_intervals,
        metrics.force_summary,
        metrics.co_contraction_index,
        visualization.plot_voltage_trace,
        visualization.plot_raster,
        visualization.plot_muscle_force,
        visualization.animate_muscle_contraction,
    ]

    assert all(callable(function) for function in functions)
