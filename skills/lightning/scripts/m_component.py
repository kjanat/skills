"""M-component guided-wave model.

Two-wave model from Rakov et al. (1995), as presented in
Rakov & Uman (2003) Chapter 12, Eqs. 12.7-12.8.

All SI units.
"""

import math
from collections.abc import Callable


def m_component_current_before_ground(
    z_prime: float,
    t: float,
    h: float,
    v: float,
    source_current_fn: Callable[[float], float],
) -> float:
    """M-component current before wave reaches ground (t < H/v).

    Eq. 12.7: I(z', t) = I(H, t - (H - z')/v)

    Single downward-propagating wave from channel top.

    Args:
        z_prime: Height along channel (m). z'=0 is ground.
        t: Time (s).
        h: Channel height (m).
        v: M-wave propagation speed (m/s). Typical: 2.5e7 to 3.0e7.
        source_current_fn: Callable(t) -> float. Current injected at
                           channel top = 1/2 of total ground-level current.

    Returns:
        I: Current at (z', t) in amperes.
    """
    t_retarded = t - (h - z_prime) / v
    if t_retarded < 0:
        return 0.0
    return source_current_fn(t_retarded)


def m_component_current_after_ground(
    z_prime: float,
    t: float,
    h: float,
    v: float,
    source_current_fn: Callable[[float], float],
) -> float:
    """M-component current after wave reflects at ground (t >= H/v).

    Eq. 12.8: I(z', t) = I(H, t-(H-z')/v) + I(H, t-(H+z')/v)

    Two counter-propagating waves: original downward wave plus
    upward-reflected wave. Ground reflection coefficient = 1.

    Args:
        z_prime: Height along channel (m).
        t: Time (s).
        h: Channel height (m).
        v: M-wave propagation speed (m/s).
        source_current_fn: Callable(t) -> float.

    Returns:
        I: Current at (z', t) in amperes.
    """
    t1 = t - (h - z_prime) / v
    t2 = t - (h + z_prime) / v

    i1 = source_current_fn(t1) if t1 >= 0 else 0.0
    i2 = source_current_fn(t2) if t2 >= 0 else 0.0

    return i1 + i2


def m_component_current(
    z_prime: float,
    t: float,
    h: float,
    v: float,
    source_current_fn: Callable[[float], float],
) -> float:
    """M-component current at height z' and time t.

    Automatically selects pre-ground or post-ground equation.

    Ground-level current is 2x the source current (due to reflection).

    Args:
        z_prime: Height along channel (m). z'=0 is ground.
        t: Time (s).
        h: Channel height (m).
        v: M-wave propagation speed (m/s). Typical: 2.5e7 to 3.0e7.
        source_current_fn: Callable(t) returning current at channel top (A).

    Returns:
        I: Current at (z', t) in amperes.
    """
    t_ground = h / v
    if t < t_ground:
        return m_component_current_before_ground(z_prime, t, h, v, source_current_fn)
    return m_component_current_after_ground(z_prime, t, h, v, source_current_fn)


def m_component_source_pulse(
    t: float,
    i_peak: float = 150.0,
    tau_rise: float = 500e-6,
    tau_decay: float = 2e-3,
) -> float:
    """Typical M-component source current pulse.

    Simple model: I(t) = I_peak * (t/tau_rise) * exp(1 - t/tau_rise)
    for t > 0, times a slow decay.

    Typical M-component parameters (Rakov et al. 2001):
    - Peak current: tens-hundreds of A (at ground, 2x source)
    - Risetime (10-90%): ~500 us
    - Charge: 0.1-0.5 C

    Args:
        t: Time (s).
        i_peak: Peak source current (A). Ground peak = 2*i_peak.
        tau_rise: Rise time constant (s). Default: 500 us.
        tau_decay: Decay time constant (s). Default: 2 ms.

    Returns:
        I: Source current (A).
    """
    if t <= 0:
        return 0.0
    x = t / tau_rise
    return i_peak * x * math.exp(1.0 - x) * math.exp(-t / tau_decay)


if __name__ == "__main__":
    H = 5000.0  # 5 km channel
    V = 2.5e7  # m/s

    t_ground = H / V
    print(f"M-component wave: H={H:.0f} m, v={V:.1e} m/s")
    print(f"Time to reach ground: {t_ground * 1e3:.2f} ms")
    print(f"Ground-level peak current: {2 * 150:.0f} A (2x source)")

    print(f"\nSource pulse shape (I_peak=150 A):")
    print(f"{'t (us)':>10} {'I_source (A)':>14} {'I_ground (A)':>14}")
    for t_us in [0, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]:
        t_s = t_us * 1e-6
        i_src = m_component_source_pulse(t_s)
        # Ground current at z'=0, at time when wave has reflected
        t_obs = t_s + t_ground
        i_gnd = m_component_current(0.0, t_obs, H, V, m_component_source_pulse)
        print(f"{t_us:10d} {i_src:14.1f} {i_gnd:14.1f}")
