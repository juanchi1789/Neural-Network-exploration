"""Inhibitory mechanisms for motor circuit experiments."""


def renshaw_feedback(motor_activity, feedback_gain, delay_ms=None):
    """Compute Renshaw-like recurrent inhibitory feedback.

    TODO:
        Transform motor neuron activity into delayed inhibitory feedback.
    """
    raise NotImplementedError("Implement Renshaw-like feedback.")


def reciprocal_inhibition(agonist_activity, antagonist_activity, inhibition_gain):
    """Compute reciprocal inhibition between agonist and antagonist pools.

    TODO:
        Estimate how each pool suppresses the opposing pool.
    """
    raise NotImplementedError("Implement reciprocal inhibition.")


def apply_inhibitory_current(excitatory_current, inhibitory_current):
    """Apply inhibitory current to an excitatory motor command.

    TODO:
        Combine excitation and inhibition with clipping or normalization rules.
    """
    raise NotImplementedError("Implement inhibitory current application.")

