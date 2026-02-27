# Distant EM Environment & Upper-Atmosphere Effects

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

- Groundwave + skywaves (1-hop, 2-hop, etc.)
- Waveguide cutoff: ~1-3 kHz
- Mean reflecting height: 86-88 km (night, ~1000 km range)

Wait & Spies ionospheric model:
omega\_p^2/nu\_e = 2.5x10^5 \* exp\[beta*(z-h')\]
nu\_e = 1.816x10^11 \* exp(-0.15\*z)

Daytime: beta=0.35 km^-1, h'=72 km. Night: beta=0.6 km^-1, h'=84 km.

## Schumann Resonances

Ideal frequencies: f\_N = c/(2\*pi\*R\_e) \* sqrt(N\*(N+1))

| Mode N | Ideal (Hz) | Observed (Hz) |
| ------ | ---------- | ------------- |
| 1      | 10.6       | **7.8**       |
| 2      | 18.3       | **14**        |
| 3      | 25.9       | **20**        |
| 4      | 33.5       | **26**        |
| 5      | 41.1       | **33**        |

Amplitude: ~100-200 uV/m/sqrt(Hz) (E); ~0.5-1 pT/sqrt(Hz) (B).
Q-factors: 3-6. First mode damping: ~0.5 s.
~50 flashes worldwide during each damping time.

Williams (1992): 0.2C tropical temp increase → measurable Schumann increase.

See `scripts/schumann.py` for frequency calculations.

## Whistlers

- Discovered: Barkhausen (1919), WWI. Storey (1953) proved propagation.
- Frequency: ~100 Hz to >10 kHz
- Lower frequencies arrive later → whistling tone
- First-hop dispersion time: ~1 s

Eckersley dispersion: D = t(f)*sqrt(f) = const (independent of frequency)

Ducting: omega < omega_be/2 → density enhancement duct.
Duct diameters: ~50 km; density enhancement: 10-100%.
Plasmapause at 4-5 R_e: n_e drops 100x.

## Upper-Atmosphere Phenomena

| Phenomenon    | Altitude (km) | Color                   | Duration    | Association       |
| ------------- | ------------- | ----------------------- | ----------- | ----------------- |
| Blue starters | 18-26         | Blue                    | ~200 ms     | Not individual CG |
| Blue jets     | 18-43         | Blue                    | ~200 ms     | Not individual CG |
| Red sprites   | 40-90         | Red body, blue tendrils | few-tens ms | Large +CG         |
| Sprite halos  | 70-85         | Diffuse                 | ~1 ms       | +CG and -CG       |
| Elves         | ~90           | Expanding circles       | <1 ms       | Radiation fields  |

### Sprites

- Most luminous 40-90 km; clusters >40 km wide
- Brightness: 25-50 kR (video); peak 0.5-10 MR (1 ms)
- Spectrum: red = N2 first positive; blue = N2+ first negative
- 86% coincidence with +CG (Boccippio et al. 1995)
- Charge transfer: 25-325 C in first 5 ms of positive strokes
- Sprite currents: 1-4 kA; charge 5-42 C
- Over stratiform regions of MCSs, not near convective core

### Blue Jets

- Speed: ~10^5 m/s (similar to stepped leader)
- Terminal altitude: 33-43 km
- Cone shape, apex angle 6.5-31.5 deg (mean 14.7)
- Brightness: ~0.5 MR base, ~7 kR top

### Elves

- ~90 km; <1 ms duration
- Caused by return-stroke radiation fields accelerating ionospheric electrons
- Both polarities of lightning

### Terrestrial Gamma-Ray Flashes (TGFs)

- Runaway electrons gain more energy from ambient E than lost in collisions
- Predicted by Wilson (1925a,b)
- Important for lower-to-middle atmosphere energy coupling
