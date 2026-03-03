# Distant Electromagnetic Signals

## Three Classes of Distant EM Signals

| Type                   | Band                  | Propagation                | Range                 |
| ---------------------- | --------------------- | -------------------------- | --------------------- |
| Atmospherics (sferics) | VLF 3-30 kHz          | Earth-ionosphere waveguide | 100s-10,000s km       |
| Schumann resonances    | ELF 3-60 Hz           | Standing waves in cavity   | Global                |
| Whistlers              | ELF-VLF 100 Hz-10 kHz | Along geomagnetic field    | Hemisphere-hemisphere |

## Ionospheric Layers

| Layer | Altitude (km) | n_e (day, m^-3) | n_e (night) |
| ----- | ------------- | --------------- | ----------- |
| D     | 40-90         | ~10^9           | negligible  |
| E     | 90-160        | >10^11          | ~10^9       |
| F     | 160-1000      | peak ~2x10^12   | ~2x10^11    |

## Sferics

Electromagnetic signals from lightning propagating in Earth-ionosphere
waveguide. Primary source of VLF/ELF background noise.

### Frequency Ranges

| Range | Frequencies | Propagation                        |
| ----- | ----------- | ---------------------------------- |
| VLF   | 3-30 kHz    | Earth-ionosphere waveguide; global |
| ELF   | 3 Hz-3 kHz  | Low attenuation; global            |
| LF    | 30-300 kHz  | Groundwave + skywave               |

### Key Properties

- Peak spectral energy: 5-10 kHz (from >50 km sources)
- Above 10 MHz: amplitude ~ 1/sqrt(f)
- 3-30 MHz: amplitude ~ 1/f
- Most radiated EM energy in radio frequencies, not optical
- Single return stroke RF power: ~2x10^10 W (first), ~3x10^9 W (subsequent)
- Groundwave + skywaves (1-hop, 2-hop, etc.)
- Waveguide cutoff: ~1-3 kHz
- Mean reflecting height: 86-88 km (night, ~1000 km range)

### Waveguide Propagation

- Lower boundary: Earth's surface (good conductor)
- Upper boundary: lower ionosphere (~70 km day, ~90 km night)
- Daytime ionosphere: lower, more absorptive (solar photoionization)
- Nighttime: higher, less absorptive
- Exponential conductivity model: sigma ~ exp\[beta*(z-h')\], beta ~ 0.3-0.5 km^-1

Wait & Spies ionospheric model:
omega\_p^2/nu\_e = 2.5x10^5 \* exp\[beta*(z-h')\]
nu\_e = 1.816x10^11 \* exp(-0.15\*z)

Daytime: beta=0.35 km^-1, h'=72 km. Night: beta=0.6 km^-1, h'=84 km.

### Distance Estimation from Sferics

- SAR (sferic amplitude ratio): amplitude at two frequencies → distance
- GDD (group delay difference): dispersion of VLF components
- Slow-tail timing: ELF slow tail arrives after VLF sferic; delay ~ f(distance)

## Schumann Resonances

Electromagnetic resonances of Earth-ionosphere cavity at ELF.

Ideal frequencies: f\_N = c/(2\*pi\*R\_e) \* sqrt(N\*(N+1))

| Mode N | Ideal (Hz) | Observed (Hz) | Variation  |
| ------ | ---------- | ------------- | ---------- |
| 1      | 10.6       | **7.8**       | +/- 0.5 Hz |
| 2      | 18.3       | **14**        | +/- 0.5 Hz |
| 3      | 25.9       | **20**        |            |
| 4      | 33.5       | **26**        |            |
| 5      | 41.1       | **33**        |            |
| 6      |            | **39**        |            |
| 7      |            | **45**        |            |

### Amplitudes

| Component          | Typical                |
| ------------------ | ---------------------- |
| Vertical E-field   | ~100-200 uV/m/sqrt(Hz) |
| Horizontal B-field | ~0.5-1 pT/sqrt(Hz)     |

Q-factors: 3-6. First mode damping: ~0.5 s.
~50 flashes worldwide during each damping time.

Diurnal variation: peak at 2000-2200 UT (coincides with maximum global
thunderstorm activity, primarily Africa and Americas).

### Applications

- Global lightning activity monitor (without lightning location network)
- Climate change proxy: more convection → more lightning → stronger SR
- Williams (1992): 5-6% increase in global lightning per 1C warming;
  0.2C tropical temp increase → measurable Schumann increase
- Interference sources: power lines, acoustic noise, rain

See `scripts/schumann.py` for frequency calculations.

## Whistlers

- Discovered: Barkhausen (1919), WWI. Storey (1953) proved propagation.
- First evidence of magnetosphere (Storey 1953)
- Frequency: ~100 Hz to >10 kHz (dispersed VLF 1-30 kHz)
- Lower frequencies arrive later → whistling tone
- First-hop dispersion time: ~1 s
- Path: Earth → ionosphere → magnetosphere (along field line) → conjugate hemisphere
- Source: typically CG flashes (strong VLF radiation)
- Detected at geomagnetic conjugate point

Eckersley dispersion: D = t(f)*sqrt(f) = const (independent of frequency)

Ducting: omega < omega_be/2 → density enhancement duct.
Duct diameters: ~50 km; density enhancement: 10-100%.
Plasmapause at 4-5 R_e: n_e drops 100x.

### Whistler Applications

- Probe magnetospheric electron density (density from dispersion)
- Lightning-induced electron precipitation (LEP): whistler waves scatter
  radiation belt electrons into loss cone

## Radio Noise

Lightning: dominant source of atmospheric radio noise below ~30 MHz.
Background noise levels depend on local time, season, geographic location.
Tropical regions: highest noise (most thunderstorms).
