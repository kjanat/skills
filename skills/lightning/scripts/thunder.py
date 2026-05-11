"""Thunder generation and propagation equations.

Few's thunder theory from Rakov & Uman (2003) Chapter 11.

All SI units.
"""

import math

P_0 = 1.01325e5  # Pa, standard atmospheric pressure
C_0 = 343.0  # m/s, speed of sound at 20C


def relaxation_radius(
    w: float,
    p_0: float = P_0,
) -> float:
    """Few's relaxation radius R_0.

    R_0 = sqrt(W / (pi * P_0))

    The radial distance at which the shock-wave energy equals the
    energy required to compress the ambient air.

    Args:
        w: Energy input per unit channel length (J/m).
           Typical range: 10^3 to 10^6 J/m.
        p_0: Ambient pressure (Pa). Default: 1 atm.

    Returns:
        R_0: Relaxation radius (m).
    """
    return math.sqrt(w / (math.pi * p_0))


def peak_thunder_frequency(
    w: float,
    c_0: float = C_0,
    p_0: float = P_0,
) -> float:
    """Peak frequency of thunder from Few's theory.

    f_m = 0.63 * c_0 * sqrt(P_0 / W)

    Args:
        w: Energy input per unit length (J/m).
        c_0: Speed of sound (m/s). Default: 343.
        p_0: Ambient pressure (Pa). Default: 1 atm.

    Returns:
        f_m: Peak frequency (Hz).
    """
    return 0.63 * c_0 * math.sqrt(p_0 / w)


def n_wave_length(r_0: float) -> float:
    """Characteristic N-wave length.

    L = 2.6 * R_0

    The N-wave is the characteristic pressure signature: initial
    overpressure (compression) followed by rarefaction.

    Args:
        r_0: Relaxation radius (m).

    Returns:
        L: N-wave length (m).
    """
    return 2.6 * r_0


def flash_to_bang_distance(
    t_delay: float,
    c_0: float = C_0,
) -> float:
    """Distance from flash-to-bang time delay.

    d = c_0 * t_delay

    Rule of thumb: ~3 seconds per kilometer.

    Args:
        t_delay: Time between seeing flash and hearing thunder (s).
        c_0: Speed of sound (m/s). Default: 343.

    Returns:
        d: Distance to lightning channel (m).
    """
    return c_0 * t_delay


def thunder_duration_estimate(
    d_near: float,
    d_far: float,
    c_0: float = C_0,
) -> float:
    """Estimated thunder duration from channel geometry.

    Duration = (d_far - d_near) / c_0

    Thunder duration depends on the difference in distances between
    the closest and farthest audible channel points.

    Args:
        d_near: Distance to nearest audible channel point (m).
        d_far: Distance to farthest audible channel point (m).
        c_0: Speed of sound (m/s).

    Returns:
        Duration (s).
    """
    return abs(d_far - d_near) / c_0


def acoustic_efficiency(
    e_acoustic: float,
    e_total: float,
) -> float:
    """Acoustic efficiency of lightning.

    eta = E_acoustic / E_total

    Holmes et al. (1971a): ~0.18% if total flash energy 1.8x10^9 J.
    Could be 2-20% if actual input energy is 10^3-10^4 J/m.

    Args:
        e_acoustic: Acoustic energy output (J).
        e_total: Total flash energy input (J).

    Returns:
        eta: Acoustic efficiency (dimensionless).
    """
    return e_acoustic / e_total


def overpressure_at_distance(
    w: float,
    r: float,
    p_0: float = P_0,
) -> float:
    """Approximate overpressure from cylindrical shock-wave model.

    For r >> R_0 (far field, weak shock):
    Delta_P ≈ P_0 * (R_0 / r)^(3/4)

    This is a simplified scaling; actual overpressure depends on
    channel geometry and propagation effects.

    Args:
        w: Energy per unit length (J/m).
        r: Distance from channel (m).
        p_0: Ambient pressure (Pa).

    Returns:
        delta_p: Overpressure (Pa).
    """
    r_0 = relaxation_radius(w, p_0)
    if r <= r_0:
        return p_0  # Near-field: pressure ~ ambient (strong shock regime)
    return p_0 * math.pow(r_0 / r, 0.75)


def shock_to_acoustic_transition(
    r_0: float,
    factor: float = 3.5,
) -> float:
    """Distance at which shock wave transitions to acoustic wave.

    Transition occurs at approximately 2*R_0 to 5*R_0.
    Default factor: 3.5 (midpoint estimate).

    Args:
        r_0: Relaxation radius (m).
        factor: Multiplier (2-5). Default: 3.5.

    Returns:
        r_transition: Transition distance (m).
    """
    return factor * r_0


if __name__ == "__main__":
    print("Few's Thunder Theory - Energy vs Parameters:")
    print(f"{'W (J/m)':>12} {'R_0 (cm)':>10} {'N-wave (m)':>12} {'f_m (Hz)':>10}")
    for w in [1e3, 1e4, 1e5, 1e6]:
        r0 = relaxation_radius(w)
        nw = n_wave_length(r0)
        fm = peak_thunder_frequency(w)
        print(f"{w:12.0e} {r0 * 100:10.1f} {nw:12.2f} {fm:10.0f}")

    print("\nFlash-to-bang examples:")
    for secs in [3, 6, 9, 15, 30]:
        d = flash_to_bang_distance(secs)
        print(f"  {secs:2d} s → {d / 1e3:.1f} km")

    print(
        "\nOverpressure at 1 km for W=10^4 J/m: "
        + f"{overpressure_at_distance(1e4, 1e3):.2f} Pa "
        + f"({overpressure_at_distance(1e4, 1e3) / P_0 * 1e4:.2f} x10^-4 atm)"
    )
