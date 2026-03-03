"""Schumann resonance and Earth-ionosphere waveguide calculations.

Equations from Rakov & Uman (2003) Chapter 13, Eqs. 13.87-13.89.

All SI units.
"""

import math

C = 2.998e8  # m/s, speed of light
R_E = 6.371e6  # m, Earth radius
EPS_0 = 8.854187817e-12  # F/m
MU_0 = 4e-7 * math.pi  # H/m


def schumann_ideal_frequency(n: int) -> float:
    """Ideal Schumann resonance frequency for mode N.

    f_N = c / (2*pi*R_e) * sqrt(N*(N+1))

    Assumes perfectly conducting Earth and ionosphere.
    Observed frequencies are lower due to ionospheric losses.

    Args:
        n: Mode number (1, 2, 3, ...).

    Returns:
        f: Ideal resonant frequency (Hz).
    """
    return C / (2.0 * math.pi * R_E) * math.sqrt(n * (n + 1))


# Observed frequencies (from Table 13.1, Rakov & Uman)
OBSERVED_SCHUMANN_HZ = [7.8, 14.0, 20.0, 26.0, 33.0, 39.0, 45.0]


def schumann_q_factor(f_n: float, delta_f: float) -> float:
    """Schumann resonance Q-factor.

    Q_N = f_N / Delta_f_N

    Typical Q-factors: 3-6.
    First mode (8 Hz) damping time: ~0.5 s.

    Args:
        f_n: Resonant frequency (Hz).
        delta_f: 3-dB bandwidth (Hz).

    Returns:
        Q: Quality factor (dimensionless).
    """
    return f_n / delta_f


def schumann_damping_time(q: float, f: float) -> float:
    """Damping time for a Schumann resonance mode.

    tau = Q / (pi * f)

    Args:
        q: Quality factor.
        f: Resonant frequency (Hz).

    Returns:
        tau: Damping time (s).
    """
    return q / (math.pi * f)


def earth_ionosphere_cutoff() -> float:
    """Approximate Earth-ionosphere waveguide cutoff frequency.

    f_cutoff ≈ c / (2*h) where h ≈ 70-90 km (effective waveguide height).

    Using h = 80 km gives ~1.9 kHz. Observed: 1-3 kHz.

    Returns:
        f_cutoff: Cutoff frequency (Hz) for h=80 km.
    """
    h = 80e3  # 80 km effective height
    return C / (2.0 * h)


def whistler_dispersion(
    f: float,
    d: float,
) -> float:
    """Propagation time for whistler at frequency f.

    Eckersley dispersion law (low-frequency approximation):
    t(f) = D / sqrt(f)

    where D is the dispersion constant (s*Hz^1/2).
    Lower frequencies arrive later → whistling tone descending in pitch.

    Args:
        f: Frequency (Hz).
        d: Dispersion constant (s*Hz^1/2). Typical first-hop: 15-50.

    Returns:
        t: Propagation time (s).
    """
    return d / math.sqrt(f)


def whistler_nose_frequency(f_be: float) -> float:
    """Nose frequency of whistler (frequency of minimum travel time).

    f_nose = f_be / 4 (for homogeneous plasma along field line)

    Args:
        f_be: Electron cyclotron frequency (Hz).
             At equatorial ionosphere (B~30 uT): ~840 kHz.

    Returns:
        f_nose: Nose frequency (Hz).
    """
    return f_be / 4.0


def plasma_frequency(n_e: float) -> float:
    """Plasma frequency.

    f_pe = (1/2pi) * sqrt(n_e * e^2 / (m_e * eps_0))

    Args:
        n_e: Electron density (m^-3).
             Ionosphere: ~10^12. Upper magnetosphere: ~10^8.

    Returns:
        f_pe: Plasma frequency (Hz).
    """
    e = 1.602e-19  # C
    m_e = 9.109e-31  # kg
    return math.sqrt(n_e * e * e / (m_e * EPS_0)) / (2.0 * math.pi)


def electron_cyclotron_frequency(b: float) -> float:
    """Electron cyclotron (gyro) frequency.

    f_be = |e| * B / (2*pi*m_e)

    Args:
        b: Magnetic field strength (T). At equator: ~30e-6 T.

    Returns:
        f_be: Cyclotron frequency (Hz).
    """
    e = 1.602e-19
    m_e = 9.109e-31
    return e * b / (2.0 * math.pi * m_e)


def wait_spies_conductivity(
    z: float,
    beta: float,
    h_prime: float,
) -> float:
    """Wait & Spies (1965) ionospheric conductivity parameter.

    omega_p^2/nu_e = 2.5e5 * exp(beta*(z - h'))  (s^-1)

    Daytime: beta=0.35 km^-1, h'=72 km.
    Nighttime: beta=0.6 km^-1, h'=84 km.

    Args:
        z: Altitude (km).
        beta: Inverse scale height (km^-1).
        h_prime: Reference height (km).

    Returns:
        Conductivity parameter omega_p^2/nu_e (s^-1).
    """
    return 2.5e5 * math.exp(beta * (z - h_prime))


def wait_spies_collision_freq(z: float) -> float:
    """Wait & Spies (1965) electron collision frequency.

    nu_e = 1.816e11 * exp(-0.15*z)  (s^-1)

    Args:
        z: Altitude (km).

    Returns:
        nu_e: Electron collision frequency (s^-1).
    """
    return 1.816e11 * math.exp(-0.15 * z)


if __name__ == "__main__":
    print("Schumann Resonance Frequencies:")
    print(f"{'Mode':>6} {'Ideal (Hz)':>12} {'Observed (Hz)':>14}")
    for n in range(1, 8):
        f_ideal = schumann_ideal_frequency(n)
        f_obs = OBSERVED_SCHUMANN_HZ[n - 1] if n <= len(OBSERVED_SCHUMANN_HZ) else None
        obs_str = f"{f_obs:.1f}" if f_obs else "—"
        print(f"{n:6d} {f_ideal:12.1f} {obs_str:>14}")

    print(f"\nEarth-ionosphere cutoff (h=80km): {earth_ionosphere_cutoff():.0f} Hz")

    print(f"\nFirst mode Q=4 damping time: {schumann_damping_time(4.0, 7.8):.2f} s")

    print("\nWhistler dispersion (D=30 s*Hz^1/2):")
    for f_hz in [500, 1000, 2000, 5000, 10000]:
        t = whistler_dispersion(f_hz, 30.0)
        print(f"  f={f_hz:6d} Hz → t={t:.3f} s")

    print(
        f"\nPlasma frequency (n_e=10^12 m^-3): {plasma_frequency(1e12) / 1e6:.1f} MHz"
    )

    print(
        f"Cyclotron frequency (B=30 uT): {electron_cyclotron_frequency(30e-6) / 1e3:.0f} kHz"
    )
