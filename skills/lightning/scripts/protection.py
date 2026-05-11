"""Lightning protection calculations.

Striking distance, grounding resistance, step voltage,
and incidence formulas from Rakov & Uman (2003) Ch. 2, 18.

All SI units.
"""

import math

EPS_0 = 8.854187817e-12  # F/m


# --- Striking Distance ---


def striking_distance(
    i_peak_ka: float,
    a: float = 10.0,
    b: float = 0.65,
) -> float:
    """Striking distance (attachment distance) as function of peak current.

    r = A * I^b  (meters, I in kA)

    Default A=10, b=0.65: Love (1973) / IEEE standard.
    Other common values:
      Armstrong & Whitehead: A=6.0, b=0.80
      Brown & Whitehead: A=6.4, b=0.75

    Args:
        i_peak_ka: Peak return-stroke current (kA).
        a: Coefficient. Default: 10.0 (Love/IEEE).
        b: Exponent. Default: 0.65.

    Returns:
        r: Striking distance (m).
    """
    return a * math.pow(i_peak_ka, b)


def rolling_sphere_min_current(radius: float) -> float:
    """Minimum peak current intercepted by rolling sphere of given radius.

    Inverts Love (1973) formula: I = (r/10)^(1/0.65)

    IEC 61024-1 protection levels:
      Level I:  R=20m → I_min=2.9 kA (99% interception)
      Level II: R=30m → I_min=5.4 kA (97%)
      Level III: R=45m → I_min=10.1 kA (91%)
      Level IV: R=60m → I_min=15.7 kA (84%)

    Args:
        radius: Rolling sphere radius (m).

    Returns:
        i_min: Minimum peak current (kA).
    """
    return math.pow(radius / 10.0, 1.0 / 0.65)


# --- Grounding Resistance ---


def hemispherical_ground_resistance(
    rho: float,
    a: float,
) -> float:
    """Grounding resistance of hemispherical electrode.

    R_gr = rho / (2*pi*a)

    Args:
        rho: Soil resistivity (ohm*m).
        a: Hemisphere radius (m).

    Returns:
        R_gr: Grounding resistance (ohm).
    """
    return rho / (2.0 * math.pi * a)


def vertical_rod_resistance(
    sigma: float,
    length: float,
    diameter: float,
) -> float:
    """Grounding resistance of vertical ground rod (Dwight 1936).

    R_gr = (1 / (2*pi*sigma*l)) * [ln(8l/d) - 1]

    Note: R is relatively independent of rod diameter.

    Args:
        sigma: Soil conductivity (S/m).
        length: Rod length (m). Typical: 2-3 m.
        diameter: Rod diameter (m). Typical: 0.015-0.025.

    Returns:
        R_gr: Grounding resistance (ohm).
    """
    return (1.0 / (2.0 * math.pi * sigma * length)) * (
        math.log(8.0 * length / diameter) - 1.0
    )


# --- Step and Touch Voltage ---


def step_voltage(
    i_peak: float,
    rho: float,
    r_near: float,
    r_far: float,
) -> float:
    """Step voltage between two points at radii a and b from strike.

    V_step = I*rho/(2*pi) * (1/a - 1/b)

    Assumes hemispherical current spreading in homogeneous soil.

    Args:
        i_peak: Peak current (A).
        rho: Soil resistivity (ohm*m).
        r_near: Distance from strike to nearer foot (m).
        r_far: Distance from strike to farther foot (m).

    Returns:
        V: Step voltage (V).
    """
    return i_peak * rho / (2.0 * math.pi) * (1.0 / r_near - 1.0 / r_far)


def soil_breakdown_radius(
    i_peak: float,
    sigma: float,
    e_b: float = 300e3,
) -> float:
    """Radius of soil breakdown zone around strike point.

    E = I / (2*pi*sigma*r^2) → r_0 = sqrt(I / (2*pi*sigma*E_b))

    Args:
        i_peak: Peak current (A). Typical: 30e3.
        sigma: Soil conductivity (S/m). Typical: 1e-3.
        e_b: Soil breakdown field (V/m). Typical: 100-500 kV/m.

    Returns:
        r_0: Breakdown radius (m).
    """
    return math.sqrt(i_peak / (2.0 * math.pi * sigma * e_b))


def distribution_line_strike_rate(
    n_g: float,
    h: float,
) -> float:
    """Direct lightning strike rate to distribution line.

    N = 0.4 * N_g * h  (per 100 km per year)

    Eq. 18.13 of Rakov & Uman.

    Args:
        n_g: Ground flash density (km^-2 yr^-1).
        h: Effective line height (m).

    Returns:
        N: Strikes per 100 km per year.
    """
    return 0.4 * n_g * h


# --- Wire/conductor melting ---


def conductor_melting_action_integral(
    cross_section_mm2: float,
    material: str = "copper",
) -> float:
    """Approximate action integral to melt a conductor.

    Based on Golde (1968) data. Rough scaling:
    For copper: melts at ~2.4e6 * (A_mm2)^2 A^2s
    (e.g., No. 4 AWG ~21 mm^2 melts at ~2e7 A^2s)

    Args:
        cross_section_mm2: Conductor cross-section (mm^2).
        material: "copper" or "aluminum".

    Returns:
        action_integral: Approximate melting threshold (A^2s).
    """
    # Empirical scaling from Golde (1968) data
    if material == "copper":
        k = 2.4e6  # A^2s per mm^4
    elif material == "aluminum":
        k = 0.7e6  # Aluminum melts at ~30% of copper's threshold
    else:
        raise ValueError(f"Unknown material: {material}")
    return k * cross_section_mm2 * cross_section_mm2


if __name__ == "__main__":
    from .incidence import flash_incidence_to_structure, upward_flash_percentage

    print("Striking Distance vs Peak Current (Love/IEEE):")
    print(f"{'I (kA)':>8} {'r (m)':>8}")
    for i in [3, 5, 10, 20, 30, 50, 80, 100, 200]:
        print(f"{i:8d} {striking_distance(i):8.1f}")

    print("\nRolling Sphere Protection Levels (IEC 61024-1):")
    for r, level in [(20, "I"), (30, "II"), (45, "III"), (60, "IV")]:
        print(f"  Level {level}: R={r}m → I_min={rolling_sphere_min_current(r):.1f} kA")

    print("\nGround Rod Resistance (3m rod, 25mm dia):")
    for rho, soil in [(25, "clay"), (100, "loam"), (1000, "sand")]:
        r_gr = vertical_rod_resistance(1.0 / rho, 3.0, 0.025)
        print(f"  {soil:>6} (rho={rho:4d} ohm*m): R={r_gr:.0f} ohm")

    print(
        "\nStep voltage: 20 kA, rho=100, feet at 9.5-10.0 m: "
        + f"{step_voltage(20e3, 100, 9.5, 10.0):.0f} V"
    )

    print(
        f"\nSoil breakdown radius: 30 kA, sigma=1e-3: {soil_breakdown_radius(30e3, 1e-3):.1f} m"
    )

    print(
        "\nFlash incidence to 100 m tower, Ng=10: "
        + f"{flash_incidence_to_structure(100, 10):.1f} flashes/yr"
    )

    print(f"Upward flash % for 200 m: {upward_flash_percentage(200):.0f}%")
    print(f"Upward flash % for 500 m: {upward_flash_percentage(500):.0f}%")
