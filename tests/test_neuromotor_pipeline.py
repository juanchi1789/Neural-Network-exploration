"""Fast regression tests for the reusable neuromotor pipeline."""

import numpy as np

from src.inputs import generate_input
from src.metrics import neural_summary
from src.muscle import normalize_force, spikes_to_force, twitch_response
from src.renshaw import simulate_renshaw_circuit


def test_motor_plan_and_twitch_are_well_formed():
    time = np.arange(0, 500, 0.5)
    command = generate_input(time, "motor_plan", 12, 50, 450)
    twitch = twitch_response(time, amplitude=2, contraction_time_ms=10, relaxation_time_ms=50)
    assert command.shape == time.shape
    assert np.isclose(command.max(), 12)
    assert np.isclose(twitch.max(), 2)
    assert np.all(twitch >= 0)


def test_renshaw_shapes_sign_convention_and_reproducibility():
    kwargs = dict(n_motor=8, n_renshaw=2, total_time=300, dt=0.5, seed=7)
    first = simulate_renshaw_circuit(**kwargs)
    second = simulate_renshaw_circuit(**kwargs)
    assert first["spikes_MN"].shape == (8, 600)
    assert first["spikes_R"].shape == (2, 600)
    assert first["W_MN_to_R"].shape == (8, 2)
    assert first["W_R_to_MN"].shape == (2, 8)
    assert np.all(first["W_MN_to_R"] >= 0)
    assert np.all(first["W_R_to_MN"] >= 0)
    assert np.array_equal(first["spikes_MN"], second["spikes_MN"])


def test_disabled_inhibition_is_zero_and_force_is_finite():
    result = simulate_renshaw_circuit(
        n_motor=8, n_renshaw=2, total_time=300, dt=0.5, seed=9,
        recurrent_inhibition=False,
    )
    assert np.count_nonzero(result["I_R_to_MN"]) == 0
    summary = neural_summary(result["spikes_MN"], result["time"], result["I_R_to_MN"])
    force = spikes_to_force(result["spikes_MN"], result["time"])
    assert summary["spikes_totales"] >= 0
    assert np.all(np.isfinite(force))
    assert normalize_force(force).max(initial=0) <= 1
