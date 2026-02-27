# Atmospherics, Schumann Resonances & Whistlers (Chapter 13)

## Atmospherics (Sferics)

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

### Waveguide Propagation

- Lower boundary: Earth's surface (good conductor)
- Upper boundary: lower ionosphere (~70 km day, ~90 km night)
- Daytime ionosphere: lower, more absorptive (solar photoionization)
- Nighttime: higher, less absorptive
- Exponential conductivity model: sigma ~ exp\[beta*(z-h')\], beta ~ 0.3-0.5 km^-1

### Distance Estimation from Sferics

- SAR (sferic amplitude ratio): amplitude at two frequencies → distance
- GDD (group delay difference): dispersion of VLF components
- Slow-tail timing: ELF slow tail arrives after VLF sferic; delay ~ f(distance)

## Schumann Resonances (Table 13.1)

Electromagnetic resonances of Earth-ionosphere cavity at ELF.

| Mode | Frequency (Hz) | Variation  |
| ---- | -------------- | ---------- |
| 1    | 7.8            | +/- 0.5 Hz |
| 2    | 14             | +/- 0.5 Hz |
| 3    | 20             |            |
| 4    | 26             |            |
| 5    | 33             |            |
| 6    | 39             |            |
| 7    | 45             |            |

### Amplitudes

| Component          | Typical                |
| ------------------ | ---------------------- |
| Vertical E-field   | ~100-200 uV/m/sqrt(Hz) |
| Horizontal B-field | ~0.5-1 pT/sqrt(Hz)     |

Diurnal variation: peak at 2000-2200 UT (coincides with maximum global
thunderstorm activity, primarily Africa and Americas).

### Applications

- Global lightning activity monitor (without lightning location network)
- Climate change proxy: more convection → more lightning → stronger SR
- Williams (1992): 5-6% increase in global lightning per 1C warming
- Interference sources: power lines, acoustic noise, rain

## Whistlers (Section 13.5)

Dispersed VLF signals (1-30 kHz) from lightning propagating along
geomagnetic field lines through magnetosphere.

### Characteristics

- Descending tone: higher frequencies arrive first (frequency-dependent group velocity)
- Duration: ~1 s
- Path: Earth → ionosphere → magnetosphere (along field line) → conjugate hemisphere
- Source: typically CG flashes (strong VLF radiation)
- Detected at geomagnetic conjugate point

### Applications

- Probe magnetospheric electron density (density from dispersion)
- First evidence of magnetosphere (Storey 1953)
- Lightning-induced electron precipitation (LEP): whistler waves scatter
  radiation belt electrons into loss cone

## Radio Noise

Lightning: dominant source of atmospheric radio noise below ~30 MHz.
Background noise levels depend on local time, season, geographic location.
Tropical regions: highest noise (most thunderstorms).
