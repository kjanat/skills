"""Stepped-leader electric and magnetic field calculations.

Equations from Thottappillil et al. (1997), as presented in
Rakov & Uman (2003) Chapter 4, Eqs. 4.1-4.7.

All SI units unless noted.
"""

import math

EPS_0 = 8.854187817e-12  # F/m, vacuum permittivity
MU_0 = 4e-7 * math.pi  # H/m, vacuum permeability
C = 2.998e8  # m/s, speed of light


def leader_tip_height(
    h_m: float,
    v: float,
    t: float,
) -> float:
    """Height of descending leader tip at time t.

    Args:
        h_m: Height of cloud charge source (m).
        v: Leader speed, assumed constant (m/s). Typical: 2e5.
        t: Time since leader initiation (s).

    Returns:
        z_t: Height of leader tip (m). Clamped to >= 0.
    """
    return max(h_m - v * t, 0.0)


def leader_e_field_uniform(
    r: float,
    z_t: float,
    h_m: float,
    rho_l: float,
) -> float:
    """Electrostatic vertical E-field from uniformly-charged leader.

    Eq. 4.4 of Rakov & Uman (2003). Assumes uniform line charge density
    rho_L, perfect-conductor ground (image method), and quasi-static
    approximation (retardation negligible).

    Args:
        r: Horizontal distance from channel to observer (m).
        z_t: Current height of leader tip (m). 0 = touching ground.
        h_m: Height of cloud charge source (m).
        rho_l: Line charge density (C/m). Typical: 0.001 (1 mC/m).

    Returns:
        E_z: Vertical electric field at ground surface (V/m).
             Positive = upward (away from negative charge on leader).
    """
    if r <= 0:
        raise ValueError("Distance r must be positive")

    r2 = r * r

    term1 = 1.0 / math.sqrt(1.0 + z_t * z_t / r2)
    term2 = 1.0 / math.sqrt(1.0 + h_m * h_m / r2)
    term3 = (h_m - z_t) * h_m / (r2 * math.pow(1.0 + h_m * h_m / r2, 1.5))

    return rho_l / (2.0 * math.pi * EPS_0 * r) * (term1 - term2 - term3)


def leader_e_field_close(
    r: float,
    rho_l: float,
) -> float:
    """Close-range E-field approximation when leader tip near ground.

    Valid when H_m >> 2r and z_t ≈ 0. Eq. 4.5 simplified.

    Args:
        r: Horizontal distance (m).
        rho_l: Line charge density (C/m).

    Returns:
        E_z: Approximate vertical E-field (V/m).
    """
    return rho_l / (2.0 * math.pi * EPS_0 * r)


def leader_b_field(
    r: float,
    i_leader: float,
) -> float:
    """Magnetostatic azimuthal B-field from leader current.

    Eq. 4.7: same form as infinitely-long current-carrying wire.
    Valid for close range where quasi-static approximation holds.

    Args:
        r: Horizontal distance (m).
        i_leader: Leader current (A). Typical: 50-5000.

    Returns:
        B_phi: Azimuthal magnetic field (T).
    """
    return MU_0 * i_leader / (2.0 * math.pi * r)


def leader_retarded_height(
    h_m: float,
    v: float,
    t: float,
    r: float,
) -> float:
    """Retarded leader tip height h(t) seen by observer.

    Solves Eq. 4.2: t = (H_m - h)/v + sqrt(h^2 + r^2)/c

    Uses Newton's method since equation is implicit.

    Args:
        h_m: Charge source height (m).
        v: Leader speed (m/s).
        r: Horizontal distance to observer (m).
        t: Observation time (s).

    Returns:
        h: Retarded height of leader tip as "seen" by observer (m).
    """
    # Initial guess: non-retarded position
    h = max(h_m - v * t, 0.01)
    f = float("inf")

    for _ in range(50):
        f = (h_m - h) / v + math.sqrt(h * h + r * r) / C - t
        df = -1.0 / v + h / (C * math.sqrt(h * h + r * r))
        if abs(df) < 1e-30:
            break
        h_new = h - f / df
        if abs(h_new - h) < 1e-6:
            h = h_new
            break
        h = max(h_new, 0.0)
    else:
        import warnings

        warnings.warn(
            "leader_retarded_height: Newton's method did not converge "
            + f"after 50 iterations (residual |f|={abs(f):.2e})",
            stacklevel=2,
        )

    return h


def stepped_leader_field_vs_time(
    r: float,
    h_m: float,
    v: float,
    rho_l: float,
    n_points: int = 200,
) -> tuple[list[float], list[float]]:
    """Compute leader E-field as function of normalized time.

    Args:
        r: Horizontal distance (m).
        h_m: Cloud charge source height (m). Typical: 5000.
        v: Leader speed (m/s). Typical: 2e5.
        rho_l: Line charge density (C/m). Typical: 0.001.
        n_points: Number of time steps.

    Returns:
        Tuple of (times_normalized, e_fields) where times are t/T
        with T = h_m/v.
    """
    t_total = h_m / v
    times_norm: list[float] = []
    fields: list[float] = []

    for i in range(n_points + 1):
        t_norm = i / n_points
        t = t_norm * t_total
        z_t = leader_tip_height(h_m, v, t)
        e_z = leader_e_field_uniform(r, z_t, h_m, rho_l)
        times_norm.append(t_norm)
        fields.append(e_z)

    return times_norm, fields


if __name__ == "__main__":
    # Example: leader from 5 km, uniform charge 1 mC/m, observed at 1 km
    H_M = 5000.0  # m
    V = 2e5  # m/s
    RHO_L = 1e-3  # C/m

    print("Stepped Leader E-Field vs Distance (tip at ground, z_t=0):")
    print(f"{'r (m)':>10} {'E_z (V/m)':>12} {'E_z (kV/m)':>12}")
    for dist in [30, 50, 100, 200, 500, 1000, 2000, 5000]:
        e = leader_e_field_uniform(float(dist), 0.0, H_M, RHO_L)
        print(f"{dist:10d} {e:12.1f} {e / 1e3:12.3f}")

    print(f"\nClose approx at 30 m: {leader_e_field_close(30.0, RHO_L):.1f} V/m")
    print(
        f"Full calc at 30 m:    {leader_e_field_uniform(30.0, 0.0, H_M, RHO_L):.1f} V/m"
    )

    print(
        f"\nB-field at 100 m for 1 kA leader: {leader_b_field(100.0, 1e3) * 1e6:.3f} uT"
    )
