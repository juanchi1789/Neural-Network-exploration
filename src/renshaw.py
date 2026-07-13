"""Motor-neuron/Renshaw recurrent inhibition circuit."""

from __future__ import annotations

import numpy as np

from .connectivity import create_weight_matrix, synaptic_current
from .inputs import generate_input
from .izhikevich import izhikevich_step, population_parameters


def create_renshaw_connectivity(
    n_motor=20,
    n_renshaw=5,
    p_mn_to_r=0.5,
    w_mn_to_r=1.5,
    p_r_to_mn=0.6,
    w_r_to_mn=1.0,
    seed=42,
):
    """Create positive-magnitude MN->R and R->MN matrices."""
    rng = np.random.default_rng(seed)
    return (
        create_weight_matrix(n_motor, n_renshaw, p_mn_to_r, w_mn_to_r, rng),
        create_weight_matrix(n_renshaw, n_motor, p_r_to_mn, w_r_to_mn, rng),
    )


def simulate_renshaw_circuit(
    n_motor=20,
    n_renshaw=5,
    amplitude=12.0,
    input_type="motor_plan",
    parameter_noise=0.03,
    input_noise=0.5,
    p_mn_to_r=0.5,
    w_mn_to_r=1.5,
    p_r_to_mn=0.6,
    w_r_to_mn=1.0,
    synaptic_tau=10.0,
    total_time=1000.0,
    dt=0.5,
    seed=42,
    recurrent_inhibition=True,
    input_start=100.0,
    input_end=None,
    frequency_hz=5.0,
):
    """Simulate the two-population recurrent circuit with Euler integration.

    Both matrices contain positive magnitudes. Excitation is added to Renshaw
    cells, while the R->MN current is explicitly subtracted from motor input.
    """
    if not 2 <= n_motor <= 30 or not 1 <= n_renshaw <= 10:
        raise ValueError("n_motor must be 2..30 and n_renshaw 1..10")
    if dt <= 0 or total_time <= dt or synaptic_tau <= 0:
        raise ValueError("Use positive dt/tau and total_time greater than dt")
    rng = np.random.default_rng(seed)
    time = np.arange(0.0, total_time, dt)
    end = total_time - max(dt, 100.0) if input_end is None else input_end
    motor_command = generate_input(time, input_type, amplitude, input_start, end, frequency_hz)

    motor_params = population_parameters(n_motor, "Regular Spiking", parameter_noise, rng)
    renshaw_params = population_parameters(n_renshaw, "Fast Spiking", parameter_noise, rng)
    w_mr = create_weight_matrix(n_motor, n_renshaw, p_mn_to_r, w_mn_to_r, rng)
    w_rm = create_weight_matrix(n_renshaw, n_motor, p_r_to_mn, w_r_to_mn, rng)

    n_steps = time.size
    v_motor = np.empty((n_motor, n_steps)); u_motor = np.empty_like(v_motor)
    v_renshaw = np.empty((n_renshaw, n_steps)); u_renshaw = np.empty_like(v_renshaw)
    spikes_motor = np.zeros((n_motor, n_steps), dtype=bool)
    spikes_renshaw = np.zeros((n_renshaw, n_steps), dtype=bool)
    i_exc = np.zeros((n_renshaw, n_steps)); i_inh = np.zeros((n_motor, n_steps))
    i_motor_total = np.zeros((n_motor, n_steps)); i_renshaw_total = np.zeros((n_renshaw, n_steps))
    v_motor[:, 0] = -65.0; u_motor[:, 0] = motor_params["b"] * v_motor[:, 0]
    v_renshaw[:, 0] = -65.0; u_renshaw[:, 0] = renshaw_params["b"] * v_renshaw[:, 0]
    noise_motor = input_noise * rng.normal(size=(n_motor, n_steps))
    noise_renshaw = input_noise * rng.normal(size=(n_renshaw, n_steps))
    state_motor = np.zeros(n_motor); state_renshaw = np.zeros(n_renshaw)
    decay = np.exp(-dt / synaptic_tau)

    for step in range(1, n_steps):
        state_motor *= decay; state_renshaw *= decay
        i_exc[:, step] = synaptic_current(w_mr, state_motor)
        if recurrent_inhibition:
            i_inh[:, step] = synaptic_current(w_rm, state_renshaw)
        i_motor_total[:, step] = motor_command[step] + noise_motor[:, step] - i_inh[:, step]
        i_renshaw_total[:, step] = i_exc[:, step] + noise_renshaw[:, step]

        vm, um, fired_m = izhikevich_step(
            v_motor[:, step - 1], u_motor[:, step - 1], i_motor_total[:, step], motor_params, dt
        )
        vr, ur, fired_r = izhikevich_step(
            v_renshaw[:, step - 1], u_renshaw[:, step - 1], i_renshaw_total[:, step], renshaw_params, dt
        )
        v_motor[:, step] = vm; u_motor[:, step] = um; spikes_motor[:, step] = fired_m
        v_renshaw[:, step] = vr; u_renshaw[:, step] = ur; spikes_renshaw[:, step] = fired_r
        v_motor[fired_m, step - 1] = 30.0; v_renshaw[fired_r, step - 1] = 30.0
        state_motor[fired_m] += 1.0; state_renshaw[fired_r] += 1.0

    return {
        "time": time, "motor_command": motor_command,
        "V_MN": v_motor, "U_MN": u_motor, "spikes_MN": spikes_motor,
        "V_R": v_renshaw, "U_R": u_renshaw, "spikes_R": spikes_renshaw,
        "I_MN": i_motor_total, "I_R": i_renshaw_total,
        "I_MN_to_R": i_exc, "I_R_to_MN": i_inh,
        "W_MN_to_R": w_mr, "W_R_to_MN": w_rm,
        "params_MN": motor_params, "params_R": renshaw_params,
        "dt": dt, "recurrent_inhibition": recurrent_inhibition,
    }
