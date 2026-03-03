# Return Stroke: Current, Speed, Channel & Fields

## Current Parameters (Berger et al. 1975, Monte San Salvatore)

### Negative First Strokes

| Parameter                  | 95%    | 50%          | 5%       |
| -------------------------- | ------ | ------------ | -------- |
| Peak current (kA)          | 14     | **30**       | 80       |
| Max dI/dt (kA/us)          | 5.5    | **12**       | 32       |
| Front duration (us)        | 1.8    | **5.5**      | 18       |
| Duration to half-peak (us) | 30     | **75**       | 200      |
| Impulse charge (C)         | 1.1    | **4.5**      | 20       |
| Stroke charge (C)          | 1.3    | **5.2**      | 24       |
| Action integral (A^2s)     | 6x10^3 | **5.5x10^4** | 5.5x10^5 |

### Negative Subsequent Strokes

| Parameter                  | 95%      | 50%          | 5%       |
| -------------------------- | -------- | ------------ | -------- |
| Peak current (kA)          | 4.6      | **12**       | 30       |
| Max dI/dt (kA/us)          | 12       | **40**       | 120      |
| Front duration (us)        | 0.22     | **1.1**      | 4.5      |
| Duration to half-peak (us) | 6.5      | **32**       | 140      |
| Impulse charge (C)         | 0.22     | **0.95**     | 4.0      |
| Action integral (A^2s)     | 5.5x10^2 | **6.0x10^3** | 5.2x10^4 |

### Flash-Level Parameters

| Parameter           | 95%  | 50%     | 5%       |
| ------------------- | ---- | ------- | -------- |
| Flash charge (C)    | 1.3  | **7.5** | 40       |
| Flash duration (ms) | 0.15 | **13**  | 1100     |
| Strokes per flash   | —    | 3-5     | up to 26 |

## Peak Current Distribution (CIGRE)

| Percentile | First Stroke (kA) | Subsequent (kA) |
| ---------- | ----------------- | --------------- |
| 99%        | 4                 | 4.9             |
| 95%        | 14                | 4.6             |
| 50%        | 30                | 12              |
| 5%         | 80                | 29.6            |
| 1%         | 100               | —               |

Log-normal distribution with geometric mean ~30 kA (first), ~12 kA
(subsequent). Two first-stroke populations: median 61 kA (first component)
and 33.3 kA (second component).

See `references/detailed-statistical-tables.md` for extended percentile data.

## Return-Stroke Speed

| Source                  | Speed (10^8 m/s)   | Notes                   |
| ----------------------- | ------------------ | ----------------------- |
| Schonland et al. (1935) | 0.8-1.6            | First 2.4 km            |
| Idone & Orville (1982)  | 0.9-1.6 (mean 1.2) | 63 subsequent strokes   |
| Mach & Rust (1993)      | 1.0-2.4 (mean 1.7) | Segments <500 m         |
| Wang et al. (1999a)     | 1.2-1.9 (mean 1.5) | Triggered, bottom 400 m |

Typical: **(1-2)x10^8 m/s** (c/3 to 2c/3). Speed decreases with height.

## Channel Properties

| Property                   | Value                                            |
| -------------------------- | ------------------------------------------------ |
| Peak temperature           | 28,000-31,000 K (within 5 us)                    |
| Initial pressure           | ~8 atm (5 us after current rise)                 |
| Electron density           | 8x10^17 cm^-3 at 5 us; 10^15 at 750 us           |
| Radius (optically bright)  | 0.5-2 cm                                         |
| Corona sheath radius       | Several meters                                   |
| Conductivity               | ~2x10^4 S/m                                      |
| Resistance per unit length | 0.035 ohm/m (at 20 kA); ~3.5 ohm/m (dart leader) |
| Opacity (at peak T)        | 40% at 6000 A; near-complete at 3000 A           |

T decays from ~20,000 K at 20 us to ~10,000 K at 200 us. Channel luminosity
lasts ~100 us for first stroke, ~50 us for subsequent.

## Electromagnetic Fields

### Far-Field (Radiation) at Distance r

From TL model (valid >50-100 km):

E_z_rad = -v/(2*pi*eps_0*c^2*r) * I(0, t-r/c)

dE_z_rad/dt = -v/(2*pi*eps_0*c^2*r) * dI(0,t-r/c)/dt

|B_phi_rad| = |E_z_rad|/c

### Field Peaks (Normalized to 100 km)

| Parameter              | First Stroke    | Subsequent |
| ---------------------- | --------------- | ---------- |
| E-field peak (V/m)     | 6-8             | 3-6        |
| dE/dt peak (V/m/us)    | —               | 5-20       |
| E/I ratio (V/m per kA) | ~0.22 (typical) | ~0.22      |

### Close-Range Fields

At <100 m, leader-return-stroke appears as asymmetric V-shaped pulse.
Half-peak width: ~3.2 us at 30 m, ~7.3 us at 50 m, ~13 us at 110 m.

Leader E-field change varies as r^-1 (most events) — consistent with uniform
charge on lower channel.

## Optical Properties

| Property                | First Stroke                        | Subsequent |
| ----------------------- | ----------------------------------- | ---------- |
| Luminous channel length | 1-10 km                             | Same path  |
| Peak optical power      | ~10^9 W (integrated over UV-vis-IR) | ~10^8 W    |
| Time to peak luminosity | ~70 us (bottom); ~120 us (top)      | Faster     |
| Rise time (10-90%)      | 15-21 us (video derived)            | 5-10 us    |

Channel tortuosity: "straight" segments 5-70 m; mean direction change ~16 deg
per segment (randomly distributed).
