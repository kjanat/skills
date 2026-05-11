"""Lightning incidence and statistics formulas.

Equations from Rakov & Uman (2003) Chapter 2.

All SI units unless noted.
"""

import math


def ground_flash_density_from_td(t_d: float) -> float:
    """Ground flash density from thunderstorm days.

    N_g = 0.04 * T_D^1.25  (Anderson et al. 1984a)

    IEEE/CIGRE standard. Based on 62 South African sites.

    Args:
        t_d: Annual thunderstorm days (days/yr).

    Returns:
        N_g: Ground flash density (km^-2 yr^-1).
    """
    return 0.04 * math.pow(t_d, 1.25)


def ground_flash_density_from_th(t_h: float) -> float:
    """Ground flash density from thunderstorm hours.

    N_g = 0.054 * T_H^1.1  (MacGorman et al. 1984)

    Args:
        t_h: Annual thunderstorm hours (hr/yr).

    Returns:
        N_g: Ground flash density (km^-2 yr^-1).
    """
    return 0.054 * math.pow(t_h, 1.1)


def cloud_to_ground_ratio(latitude_deg: float) -> float:
    """Cloud-to-ground flash ratio z = Nc/Ng.

    z = 4.16 + 2.16 * cos(3*lambda)  (Prentice & Mackerras 1977)

    Args:
        latitude_deg: Latitude (degrees, absolute value).

    Returns:
        z: Ratio of cloud to ground flashes (dimensionless).
    """
    return 4.16 + 2.16 * math.cos(3.0 * math.radians(abs(latitude_deg)))


def flash_rate_from_cloud_height(h_km: float) -> float:
    """Flash rate from cloud-top height.

    F = 3.44e-5 * H^4.9  (Williams 1985)

    Fifth-power relation predicted by Vonnegut (1963).

    Args:
        h_km: Cloud-top height (km).

    Returns:
        F: Flash rate (flashes/min).
    """
    return 3.44e-5 * math.pow(h_km, 4.9)


def flash_incidence_to_structure(
    h_s: float,
    n_g: float,
) -> float:
    """Annual lightning incidence to isolated structure (Eriksson 1987).

    N = 24e-6 * H_s^2.05 * N_g

    Args:
        h_s: Structure height (m).
        n_g: Ground flash density (km^-2 yr^-1).

    Returns:
        N: Expected flashes per year.
    """
    return 24e-6 * math.pow(h_s, 2.05) * n_g


def upward_flash_percentage(h_s: float) -> float:
    """Percentage of flashes that are upward-initiated.

    P_u = 52.8 * ln(H_s) - 230  (valid 78-518 m)

    Args:
        h_s: Structure effective height (m).

    Returns:
        P_u: Percentage of upward flashes (%). Clamped 0-100.
    """
    p = 52.8 * math.log(h_s) - 230.0
    return max(0.0, min(100.0, p))


def attractive_radius(
    h_s: float,
    alpha: float = 14.0,
    beta: float = 0.6,
) -> float:
    """Attractive radius of a structure for lightning.

    R_a = alpha * H_s^beta

    CIGRE: alpha=14, beta=0.6
    Whitehead et al.: alpha=2, beta=1.09

    Args:
        h_s: Structure height (m).
        alpha: Coefficient. Default: 14 (CIGRE).
        beta: Exponent. Default: 0.6 (CIGRE).

    Returns:
        R_a: Attractive radius (m).
    """
    return alpha * math.pow(h_s, beta)


def fair_weather_field(z_km: float) -> float:
    """Fair-weather atmospheric electric field vs altitude.

    E(z) = -[93.8*exp(-4.527*z) + 44.4*exp(-0.375*z)
           + 11.8*exp(-0.121*z)]  (V/m)

    Volland (1984). z in km. Negative = downward directed.

    Args:
        z_km: Altitude (km).

    Returns:
        E: Electric field (V/m). Negative = downward.
    """
    return -(
        93.8 * math.exp(-4.527 * z_km)
        + 44.4 * math.exp(-0.375 * z_km)
        + 11.8 * math.exp(-0.121 * z_km)
    )


def lightning_climate_sensitivity(
    delta_t: float,
    rate_per_degree: float = 5.5,
) -> float:
    """Percentage change in global lightning for temperature change.

    Price & Rind (1994): 5-6% per 1C warming.
    Reeve & Tuomi (1999): ~40% per 1C (from OTD data).

    Args:
        delta_t: Temperature change (C).
        rate_per_degree: Percent change per degree C. Default: 5.5.

    Returns:
        Percentage change in global flash rate (%).
    """
    return rate_per_degree * delta_t


def poisson_flash_probability(z: float, n: int) -> float:
    """Poisson probability of n flashes to a structure.

    p(n) = Z^n / n! * exp(-Z)  (Eq. 2.10)

    Used by Eriksson and Meal (1984) for risk assessment.

    Args:
        z: Expected number of flashes per year (from incidence formula).
        n: Number of flashes.

    Returns:
        p: Probability of exactly n flashes.
    """
    return (z**n / math.factorial(n)) * math.exp(-z)


if __name__ == "__main__":
    print("Ground flash density from thunderstorm days:")
    for td in [5, 10, 20, 40, 80]:
        print(f"  Td={td:3d} → Ng={ground_flash_density_from_td(td):.2f} km^-2 yr^-1")

    print("\nCloud:Ground ratio by latitude:")
    for lat in [0, 10, 20, 30, 40, 50, 60]:
        print(f"  {lat}° → z={cloud_to_ground_ratio(lat):.1f}")

    print("\nFlash rate vs cloud-top height:")
    for h in [6, 8, 10, 12, 14, 16]:
        print(f"  H={h:2d} km → F={flash_rate_from_cloud_height(h):.1f} min^-1")

    print("\nFair-weather field:")
    for z in [0, 1, 5, 10, 20, 30]:
        print(f"  z={z:2d} km → E={fair_weather_field(z):.1f} V/m")

    print("\nStructure incidence (Ng=10):")
    for hs in [10, 30, 60, 100, 200, 500]:
        n = flash_incidence_to_structure(hs, 10)
        pu = upward_flash_percentage(hs) if hs >= 78 else 0
        ra = attractive_radius(hs)
        print(f"  H={hs:4d}m → N={n:.2f}/yr, upward={pu:.0f}%, R_a={ra:.0f}m")
