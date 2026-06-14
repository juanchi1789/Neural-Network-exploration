"""Project-level configuration constants.

These defaults are intentionally simple and will be refined as each project
phase is implemented.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Simulation defaults
SIMULATION_TIME_MS = 1000.0
TIME_STEP_MS = 0.1

# Default Izhikevich parameters for a regular-spiking neuron.
DEFAULT_IZHIKEVICH_PARAMS = {
    "a": 0.02,
    "b": 0.2,
    "c": -65.0,
    "d": 8.0,
    "v_peak": 30.0,
    "v_initial": -65.0,
    "u_initial": -13.0,
}

# Default muscle twitch parameters for a simplified force model.
DEFAULT_MUSCLE_PARAMS = {
    "twitch_amplitude": 1.0,
    "contraction_time_ms": 30.0,
    "relaxation_time_ms": 80.0,
    "max_force": 1.0,
}

# Output paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SIMULATION_DATA_DIR = DATA_DIR / "simulations"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
ANIMATIONS_DIR = OUTPUTS_DIR / "animations"
TABLES_DIR = OUTPUTS_DIR / "tables"

