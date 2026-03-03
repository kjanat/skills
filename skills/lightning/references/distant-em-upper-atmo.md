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

## Upper-Atmosphere Phenomena

Transient luminous events (TLEs): optical emissions above thunderstorms,
first confirmed 1989 (Franz et al.).

| Phenomenon    | Altitude (km) | Color                   | Duration    | Association       |
| ------------- | ------------- | ----------------------- | ----------- | ----------------- |
| Blue starters | 18-26         | Blue                    | ~200 ms     | Not individual CG |
| Blue jets     | 18-43         | Blue                    | ~200 ms     | Not individual CG |
| Red sprites   | 40-90         | Red body, blue tendrils | few-tens ms | Large +CG         |
| Sprite halos  | 70-85         | Diffuse                 | ~1 ms       | +CG and -CG       |
| Elves         | ~90           | Expanding circles       | <1 ms       | Radiation fields  |

### Sprites

| Property               | Value                                    |
| ---------------------- | ---------------------------------------- |
| Altitude range         | 40-90 km (mesosphere)                    |
| Horizontal extent      | 5-40 km                                  |
| Vertical extent        | Up to 50 km                              |
| Duration               | ~5-300 ms                                |
| Color                  | Red (upper body), blue/purple (tendrils) |
| Luminosity             | ~10-600 kR                               |
| Typical delay after CG | 1-5 ms                                   |

- Most luminous 40-90 km; clusters >40 km wide
- Brightness: 25-50 kR (video); peak 0.5-10 MR (1 ms)
- Spectrum: red = N2 first positive; blue = N2+ first negative
- 86% coincidence with +CG (Boccippio et al. 1995); >95% triggered by +CG
- Required: charge moment change >~120-350 C·km within ~6 ms
- Charge transfer: 25-325 C in first 5 ms of positive strokes
- Long continuing currents provide sustained charge transfer
- Occurrence rate: ~0.5-1% of positive CG flashes produce sprites
- Sprite currents: 1-4 kA; charge 5-42 C
- Over stratiform regions of MCSs, not near convective core
- Contain fine structure: tendrils (downward) and branches (upward)
- "Columniform" sprites: simple vertical columns, shorter delay after CG
- "Carrot" sprites: broader, more structured

### Blue Jets

| Property | Value                   |
| -------- | ----------------------- |
| Altitude | 15-40 km (stratosphere) |
| Speed    | ~10^5 m/s (upward)      |
| Duration | ~200-300 ms             |
| Color    | Blue (N2+ emission)     |
| Width    | ~1 km base              |

- Speed: ~10^5 m/s (similar to stepped leader)
- Terminal altitude: 33-43 km
- Cone shape, apex angle 6.5-31.5 deg (mean 14.7)
- Brightness: ~0.5 MR base, ~7 kR top
- Propagate upward from cloud tops as narrow cones
- Not directly associated with specific CG flashes
- Blue starters: shorter, reaching only ~25 km
- "Gigantic jets": rare; extend from cloud top to ~70-90 km

### Elves

| Property          | Value                        |
| ----------------- | ---------------------------- |
| Altitude          | ~85-95 km (lower ionosphere) |
| Horizontal extent | 200-600 km diameter          |
| Duration          | <1 ms (typically ~0.3 ms)    |
| Shape             | Expanding ring/disk          |

- Caused by return-stroke EMP/radiation fields accelerating ionospheric electrons
- Both polarities of lightning
- Much more common than sprites
- Inan et al. (1991): predicted theoretically before optical confirmation

### Upward Discharges from Cloud Tops

- Vonnegut (1965): first reports of luminous channels above thunderstorms
- Can extend 10+ km above cloud top
- Distinct from blue jets (more lightning-like in character)

### Terrestrial Gamma-Ray Flashes (TGFs)

- Discovered by BATSE on CGRO satellite (Fishman et al. 1994)
- Duration: 0.2-3.5 ms
- Energy: up to 20 MeV photons
- Associated with thunderstorms (initially thought sprites; now: upward leaders)
- ~50 per day globally
- Runaway electrons gain more energy from ambient E than lost in collisions
- Predicted by Wilson (1925a,b)
- Important for lower-to-middle atmosphere energy coupling

### Runaway Breakdown

- Gurevich et al. (1992): ambient cosmic-ray electrons accelerated by
  thunderstorm E-field exceeding "breakeven" threshold (~100 kV/m at 6 km)
- Relativistic runaway electron avalanche (RREA)
- May explain initiation gap: observed max field (~200 kV/m) << conventional
  breakdown (~1 MV/m at same altitude)
- X-rays: detected in association with stepped leaders (Moore et al. 2001)

### Lightning-Induced Electron Precipitation (LEP)

- VLF waves from lightning propagate into magnetosphere
- Scatter radiation belt electrons via wave-particle interaction
- Precipitated electrons enhance ionization at 60-90 km
- Observable as localized ionospheric disturbances
- May affect mesospheric ozone chemistry

### Ionospheric Effects

#### Conductivity Perturbations

- Lightning heats lower ionosphere → transient conductivity changes
- Duration: seconds to minutes
- Detectable via VLF transmitter signal perturbations ("trimpi" events)
- Sprites also modify ionospheric conductivity

#### Quasi-Electrostatic (QE) Heating

- Thundercloud electric field extends to ionosphere
- Can modify electron energy distribution in D-region
- Contributes to sprite generation mechanism
