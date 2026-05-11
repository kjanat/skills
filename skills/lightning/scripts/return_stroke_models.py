"""Engineering return-stroke models and far-field relations.

Models from Rakov (1997), Rakov & Uman (2003) Chapter 12, Eq. 12.3-12.5.

Five engineering models: TL, MTLL, MTLE, BG, TCS.
Two families: transmission-line type (upward v_f) and
traveling-current-source type (downward -c).

All SI units.
"""

import math
from collections.abc import Callable
from enum import Enum

EPS_0 = 8.854187817e-12  # F/m
MU_0 = 4e-7 * math.pi  # H/m
C = 2.998e8  # m/s


class RSModel(Enum):
    """Engineering return-stroke models."""

    TL = "TL"  # Uman & McLain 1969
    MTLL = "MTLL"  # Rakov & Dulzon 1987
    MTLE = "MTLE"  # Nucci et al. 1988
    BG = "BG"  # Bruce & Golde 1941
    TCS = "TCS"  # Heidler 1985


def attenuation_factor(
    model: RSModel,
    z_prime: float,
    h_total: float = 7500.0,
    lambda_decay: float = 2000.0,
) -> float:
    """Height-dependent current attenuation factor P(z').

    Args:
        model: Engineering model type.
        z_prime: Height along channel (m).
        h_total: Total channel height (m). Used by MTLL.
        lambda_decay: Exponential decay constant (m). Used by MTLE. Default 2000.

    Returns:
        P: Attenuation factor (dimensionless, 0 to 1).
    """
    match model:
        case RSModel.TL | RSModel.BG | RSModel.TCS:
            return 1.0
        case RSModel.MTLL:
            return max(1.0 - z_prime / h_total, 0.0)
        case RSModel.MTLE:
            return math.exp(-z_prime / lambda_decay)


def current_wave_speed(model: RSModel, v_f: float) -> float:
    """Current-wave propagation speed v for each model.

    Args:
        model: Engineering model type.
        v_f: Return-stroke front speed (m/s). Typical: 1e8 to 2e8.

    Returns:
        v: Current-wave propagation speed (m/s).
            Positive = upward (TL-type), negative = downward (TCS-type).
            Infinite for BG model (returned as math.inf).
    """
    match model:
        case RSModel.TL | RSModel.MTLL | RSModel.MTLE:
            return v_f  # upward at front speed
        case RSModel.BG:
            return math.inf  # instantaneous
        case RSModel.TCS:
            return -C  # downward at speed of light


def channel_current(
    model: RSModel,
    z_prime: float,
    t: float,
    base_current_fn: Callable[[float], float],
    v_f: float,
    h_total: float = 7500.0,
    lambda_decay: float = 2000.0,
) -> float:
    """Current at height z' and time t per engineering model.

    Eq. 12.3: I(z',t) = u(t - z'/v_f) * P(z') * I(0, t - z'/v)

    Args:
        model: Engineering model type.
        z_prime: Height along channel (m).
        t: Time (s).
        base_current_fn: Callable(t) -> float returning base current I(0,t) in A.
        v_f: Return-stroke front speed (m/s).
        h_total: Total channel height (m).
        lambda_decay: MTLE decay constant (m).

    Returns:
        I: Current at (z', t) in amperes.
    """
    # Heaviside: current zero until front reaches z'
    if t < z_prime / v_f:
        return 0.0

    p = attenuation_factor(model, z_prime, h_total, lambda_decay)
    v = current_wave_speed(model, v_f)

    if math.isinf(v):
        # BG model: current appears simultaneously everywhere
        t_retarded = t
    else:
        t_retarded = t - z_prime / v
        if t_retarded < 0:
            return 0.0

    return p * base_current_fn(t_retarded)


# --- Far-field (radiation) relations from TL model ---


def tl_radiation_e_field(
    r: float,
    v: float,
    base_current: float,
) -> float:
    """TL model far-field vertical electric radiation field.

    Eq. 12.4: E_z^rad = -v / (2*pi*eps_0*c^2*r) * I(0, t-r/c)

    Valid beyond ~50-100 km (pure radiation).
    Also usable for peak estimation at closer ranges with ~20% error.

    Args:
        r: Distance to observer (m).
        v: Return-stroke speed (m/s). Typical: 1e8 to 2e8.
        base_current: Channel-base current at retarded time (A).

    Returns:
        E_z: Radiation electric field (V/m).
    """
    return -v / (2.0 * math.pi * EPS_0 * C * C * r) * base_current


def tl_radiation_b_field(
    r: float,
    v: float,
    base_current: float,
) -> float:
    """TL model far-field azimuthal magnetic radiation field.

    |B_phi^rad| = |E_z^rad| / c

    Args:
        r: Distance (m).
        v: Return-stroke speed (m/s).
        base_current: Channel-base current at retarded time (A).

    Returns:
        B_phi: Radiation magnetic field (T).
    """
    return abs(tl_radiation_e_field(r, v, base_current)) / C


def peak_current_from_field(
    e_peak: float,
    r: float,
    v: float = 1.5e8,
) -> float:
    """Estimate peak current from measured far-field E-field peak.

    Inverts TL model: I_peak = -E_peak * 2*pi*eps_0*c^2*r / v

    NLDN formula: I = 0.185 * RNSS (kA), but this is the physics basis.

    Args:
        e_peak: Peak electric field (V/m). Should be negative by convention;
                absolute value used.
        r: Distance (m).
        v: Assumed return-stroke speed (m/s). Default 1.5e8.

    Returns:
        I_peak: Estimated peak current (A).
    """
    return abs(e_peak) * 2.0 * math.pi * EPS_0 * C * C * r / v


# --- Braginskii gas-dynamic channel radius ---


def braginskii_radius(
    i: float,
    t: float,
) -> float:
    """Braginskii (1958) channel radius for linearly increasing current.

    Simplified CGS formula: r(t) = 9.35 * I^(1/3) * t^(1/2)
    [cgs: r in cm, I in A, t in s]. Converted to SI (meters).

    Args:
        i: Current (A).
        t: Time since discharge onset (s).

    Returns:
        r: Channel radius (m).
    """
    # Original formula in cgs
    r_cm = 9.35 * math.pow(i, 1.0 / 3.0) * math.pow(t, 0.5)
    return r_cm * 1e-2  # convert cm to m


def channel_resistance_per_length(
    sigma: float,
    radius: float,
) -> float:
    """Resistance per unit channel length.

    R = 1 / (sigma * pi * r^2)

    Args:
        sigma: Conductivity (S/m).
        radius: Channel radius (m).

    Returns:
        R: Resistance per unit length (ohm/m).
    """
    return 1.0 / (sigma * math.pi * radius * radius)


# --- Heidler current function (commonly used as base current) ---


def heidler_current(
    t: float,
    i_0: float = 30e3,
    tau_1: float = 1e-6,
    tau_2: float = 50e-6,
    n: int = 10,
) -> float:
    """Heidler current function, commonly used as channel-base current.

    I(t) = (I_0 / eta) * (t/tau_1)^n / (1 + (t/tau_1)^n) * exp(-t/tau_2)

    where eta is a correction factor for peak normalization.
    Note: eta is an approximation; the exact factor requires numerically
    finding the peak of the unnormalized function. Accurate for typical
    lightning parameters (n>=5, tau_1 << tau_2).

    Args:
        t: Time (s).
        i_0: Peak current (A). Default: 30 kA (first stroke median).
        tau_1: Front time constant (s). Default: 1 us.
        tau_2: Decay time constant (s). Default: 50 us.
        n: Exponent controlling rise steepness. Default: 10.

    Returns:
        I: Current (A).
    """
    if t <= 0:
        return 0.0

    x = math.pow(t / tau_1, n)
    eta = math.exp(-(tau_1 / tau_2) * math.pow(n * tau_2 / tau_1, 1.0 / n))
    return (i_0 / eta) * x / (1.0 + x) * math.exp(-t / tau_2)


if __name__ == "__main__":
    # Demo: TL model far-field E at 100 km for 30 kA peak, v = 1.5e8 m/s
    v_rs = 1.5e8
    i_peak = 30e3
    r_obs = 100e3  # 100 km

    e_peak_val = tl_radiation_e_field(r_obs, v_rs, i_peak)
    print(f"TL far-field E at 100 km for 30 kA, v=1.5e8 m/s: {e_peak_val:.2f} V/m")
    print(f"  Normalized: {abs(e_peak_val):.2f} V/m (literature: ~6-8 V/m)")

    # Inverse: estimate current from field
    i_est = peak_current_from_field(abs(e_peak_val), r_obs, v_rs)
    print(f"  Inverse check: {i_est / 1e3:.1f} kA (should be 30 kA)")

    # Braginskii radius at 5 us for 20 kA
    r_ch = braginskii_radius(20e3, 5e-6)
    print(f"\nBraginskii radius at 5 us, 20 kA: {r_ch * 100:.2f} cm")

    # Heidler current waveform
    print("\nHeidler current (30 kA first stroke):")
    for t_us in [0.5, 1, 2, 5, 10, 20, 50, 100, 200]:
        i_val = heidler_current(t_us * 1e-6)
        print(f"  t={t_us:6.1f} us  I={i_val / 1e3:8.2f} kA")
