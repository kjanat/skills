# Chapters 12–14: Modeling, Distant EM Environment, Upper-Atmosphere Effects

> Source: Rakov & Uman (2003), *Lightning: Physics and Effects*, pp. 394–506

---

## Chapter 12 — Modeling of Lightning Processes

### 12.1 Return-Stroke Model Classification

Four classes of return-stroke models, distinguished by governing equations:

| Class                               | Approach                                                                  | Primary Output                            | Key Feature                                    |
| ----------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------- |
| **(i) Gas dynamic** ("physical")    | Conservation of mass/momentum/energy + 2 eqs of state                     | T, P, ρ vs. radial coord & time           | Radial evolution of channel segment            |
| **(ii) Electromagnetic**            | Lossy thin-wire antenna; numerical solution of Maxwell's eqs (MOM)        | Current distribution → remote E, B fields | Includes antenna-mode + TL-mode current        |
| **(iii) Distributed-circuit** (RLC) | Transient process on vertical transmission line (R, L, C per unit length) | Channel current vs. time & height         | Approximation to EM models                     |
| **(iv) Engineering**                | Specified spatial/temporal current distribution based on observations     | EM fields at 10s of m to 100s of km       | Few adjustable parameters (1–2 + base current) |

### 12.2 Gas Dynamic Models

**Braginskii (1958) channel radius:**

```r
r(t) ≈ 9.35 [I(t)]^(1/3) · t^(1/2)
```

- r in cm, I in A, t in s
- Electrical conductivity σ = 2.22 × 10⁴ S m⁻¹
- Ambient air density = 1.29 × 10⁻³ g cm⁻³

**Resistance per unit length:**

```r
R(t) = [σ · π · r²(t)]⁻¹
```

**Energy input per unit length:**

```r
W(t) = ∫₀ᵗ I²(τ) R(τ) dτ
```

**Gas dynamic model initial conditions:**

- Channel temperature: ~10,000 K
- Channel radius: ~1 mm
- Pressure: 1 atm (older channel) or mass density equal to ambient (~10⁻³ g cm⁻³, newer channel)
- Input current: rises to ~20 kA in a few µs, decays in tens of µs

**Paxton et al. (1986, 1990) — most advanced gas dynamic model:**

- Temperature, mass density, pressure, electrical conductivity vs. radius at 0.074–91 µs

#### Lightning Energy Estimates (Table 12.1)

| Source                     | Current Peak (kA) | Input Energy (J m⁻¹)       | % Kinetic  | % Radiated   | Notes                                                   |
| -------------------------- | ----------------- | -------------------------- | ---------- | ------------ | ------------------------------------------------------- |
| Hill (1971, 1977a)         | 21                | 1.5×10⁴ (~3×10³ corrected) | 9% (25 µs) | ~2% (25 µs)  | Factor ~5 overestimate due to conductivity error        |
| Plooster (1971b)           | 20                | 2.4×10³                    | 4% (35 µs) | ~50% (35 µs) | Crude radiative transport                               |
| Paxton et al. (1986, 1990) | 20                | 4×10³                      | 2% (64 µs) | 69% (64 µs)  | Individual T-dependent opacities                        |
| Dubovoy et al. (1991–95)   | 20                | 3×10³                      | —          | 25% (~55 µs) | 10 wavelength intervals; magnetic pinch                 |
| Borovsky (1998)            | —                 | 2×10²–1×10⁴                | —          | —            | Electrostatic energy, ρ_L = 100–500 µC m⁻¹              |
| Krider et al. (1968)       | single stroke     | 2.3×10⁵                    | —          | 0.38%        | Optical calibration vs. lab sparks                      |
| Uman (1987, 2001)          | —                 | (1–10)×10⁵                 | —          | —            | Electrostatic considerations (5 C from 5 km, 10⁸–10⁹ V) |

**Key discrepancy:** Gas dynamic models predict ~10³ J m⁻¹; Krider et al. inferred ~10⁵ J m⁻¹. Two orders of magnitude unresolved.

### 12.3 Electromagnetic Models

| Model                     | Resistive Loading (Ω m⁻¹) | Inductive Loading | Phase velocity v_p (m s⁻¹) |
| ------------------------- | ------------------------- | ----------------- | -------------------------- |
| Podgorski & Landt (1987)  | 0.7                       | —                 | —                          |
| Moini et al. (1997, 2000) | 0.065–0.07                | —                 | 1.3×10⁸ (ε = 5.3ε₀)        |
| Baba & Ishii (2001)       | 1.0                       | 3 µH m⁻¹          | 1.5×10⁸                    |
| Borovsky (1995)           | 16                        | —                 | — (single sinusoid only)   |

**Key relation:**

```r
v_p = (µ₀ε)^(-1/2)    with ε > ε₀ to reduce speed below c
```

### 12.4 Distributed-Circuit (RLC) Models

**Telegrapher's equations:**

```r
-∂V(z',t)/∂z' = L · ∂I(z',t)/∂t + R·I(z',t)     (12.1)

-∂I(z',t)/∂z' = C · ∂V(z',t)/∂t                    (12.2)
```

- R, L, C = series resistance, inductance, shunt capacitance per unit length
- Dynamic quantities: L = ∂φ/∂I, C = ∂ρ/∂V

**Typical R values used:**

- Price & Pierce (1977): R ≈ 0.06 Ω m⁻¹
- Little (1978): R = 1 Ω m⁻¹
- Takagi & Takeuti (1983): R = 0.08 Ω m⁻¹
- Rakov (1998): R = 3.5 Ω m⁻¹ (dart-leader channel)

**Gorin & Markin (1975) example:** V₀ = 50 MV with instantaneously discharged corona sheath, or V₀ = 10 MV with no corona sheath.

### 12.5 Engineering Models

**Generalized current equation (Rakov 1997):**

```r
I(z', t) = u(t - z'/v_f) · P(z') · I(0, t - z'/v)     (12.3)
```

- u = Heaviside function
- P(z') = height-dependent attenuation factor
- v_f = return-stroke front speed
- v = current-wave propagation speed

#### Engineering Model Parameters (Table 12.2)

| Model                     | P(z')      | v   | Year |
| ------------------------- | ---------- | --- | ---- |
| **TL** (Uman & McLain)    | 1          | v_f | 1969 |
| **MTLL** (Rakov & Dulzon) | 1 - z'/H   | v_f | 1987 |
| **MTLE** (Nucci et al.)   | exp(-z'/λ) | v_f | 1988 |
| **BG** (Bruce & Golde)    | 1          | ∞   | 1941 |
| **TCS** (Heidler)         | 1          | -c  | 1985 |

- H = total channel height
- λ = current decay constant (typically 2000 m)
- c = speed of light

**DU model (Diendorfer & Uman 1990):** Two-component TCS with exponential front modifier

- Time constant τ_D = 0.1 µs (charge decay to 1/e)
- v* = v_f / (1 + v_f/c)

**Two model families:**

1. **Transmission-line type** (TL, MTLL, MTLE): current wave propagates **upward** at v = v_f
2. **Traveling-current-source type** (BG, TCS, DU): current wave propagates **downward** at v = -c

#### TL Model Far-Field Relation

**Electric radiation field:**

```r
E_z^rad(r, t) = [-v/(2πε₀c²r)] · I(0, t - r/c)     (12.4)
```

**Time derivative:**

```r
∂E_z^rad/∂t = [-v/(2πε₀c²r)] · ∂I(0, t-r/c)/∂t     (12.5)
```

**Magnetic radiation field:** |B_φ^rad| = |E_z^rad|/c

### 12.6 Model Validation Summary

**Ranking of engineering models (descending order):** MTLL > DU > MTLE > TCS > BG > TL

| Criterion                                        | Models that Pass                 |
| ------------------------------------------------ | -------------------------------- |
| (i) Sharp initial peak ∝ 1/r beyond ~1 km        | All models                       |
| (ii) Slow ramp >100 µs at <few tens km (E field) | All except TL                    |
| (iii) Magnetic hump 10–40 µs at <few tens km     | BG, TL, TCS (not MTLE)           |
| (iv) Zero-crossing at 50–200 km                  | MTLE only (not BG, TL, TCS)      |
| Close-range (50 m) field flattening              | BG, MTLL, TCS, DU (not TL, MTLE) |

**Specific-return-stroke testing (Thottappillil & Uman 1993):**

- 18 triggered-lightning events; TL, MTLE, DU: ~20% mean error in peak field; TCS: ~40%
- TL recommended for peak-current ↔ peak-field estimation (simplest, equal accuracy)

### 12.7 Dart-Leader Models

**Uniformly-charged-line model (Eq. 12.6):**

```r
ρ_L(z', t) = ρ_L0 · u[t - (H_m - z')/v] - ρ_L0 · v·t · δ(H_m - z') · u(t)
```

- ρ_L0 = constant line charge density
- H_m = height of charge source
- v = front speed; δ = Dirac delta function
- Net charge = 0 at all times (point charge at origin simulates branched in-cloud channels)

**Borovsky (1995) dart-leader model:** R = 600 Ω m⁻¹, dominant sinusoid ~160 kHz; criticised as predicting >10× attenuation in 100 m.

**Bazelyan (1995):** RLC model with R = 10–100 Ω m⁻¹ (initial); predicted M-component-like currents → concluded electron impact ionization must be included.

**Jurenka & Barreto (1982, 1985):** Electron-pressure wave model; electron acoustic velocity ~10⁶ m s⁻¹ → similar to dart-leader speeds; criticised by Borovsky (1995).

### 12.8 Stepped-Leader Models

**Baum (1990a) lossless TL model predictions (varying corona sheath radius 0.1–2 m):**

- Propagation speeds: 0.26c–0.62c
- Charge density: 11–220 µC m⁻¹
- Longitudinal current: 2.1–17 kA
- Assumed effective breakdown field: 2 MV m⁻¹, core radius 1 mm

**Step-formation models:** Bondiou-Clergerie et al. (1996) — bidirectional leader fluid-dynamic model; Larigaldie et al. (1992) — MOM with time-varying R.

### 12.9 M-Component Model

**"Two-wave" (guided-wave) model (Rakov et al. 1995):**

Before ground contact (t < H/v):

```r
I(z', t) = I(H, t - (H - z')/v)                        (12.7)
```

After ground contact (t ≥ H/v):

```r
I(z', t) = I(H, t - (H - z')/v) + I(H, t - (H + z')/v)   (12.8)
```

- v = M-wave propagation speed (~2.5–3.0 × 10⁷ m s⁻¹)
- I(H, t) = current injected at channel top = ½ of total ground-level current
- Each wave follows TL model; ground reflection coefficient = 1

---

## Chapter 13 — Distant Lightning EM Environment

### 13.1 Overview

Three classes of distant EM signals:

| Type                       | Frequency Band           | Propagation                        | Range                    |
| -------------------------- | ------------------------ | ---------------------------------- | ------------------------ |
| **Atmospherics (sferics)** | VLF (3–30 kHz), up to LF | Earth–ionosphere waveguide modes   | 100s to 10,000s km       |
| **Schumann resonances**    | ELF (3–60 Hz)            | Standing waves in spherical cavity | Global                   |
| **Whistlers**              | ELF–VLF (100 Hz–10 kHz)  | Along geomagnetic field lines      | Hemisphere to hemisphere |

### 13.2 Ionosphere/Magnetosphere Background

**Ionospheric layers:**

- **D region:** 40–90 km; n_e ~ 10⁹ m⁻³ (day), negligible (night)
- **E region:** 90–160 km; n_e > 10¹¹ m⁻³ (day), ~10⁹ m⁻³ (night)
- **F region:** 160–1000 km; peak n_e ~ 2×10¹² m⁻³ (day), 2×10¹¹ m⁻³ (night)
- **Magnetosphere:** >1000 km; inner part = plasmasphere (extends 4–5 Earth radii to plasmapause)

**Particle interaction equation:**

```r
-iωmv = qE + q(v × B₀_z) - mνv     (13.1)
```

**Cyclotron (gyro) frequencies:**

```r
ω_bi = Z_i|e|B₀_z / m_i     (ions)
ω_be = -|e|B₀_z / m_e       (electrons)     (13.6)
```

- ω_be ~ 2π × 1 MHz at equatorial ionosphere (B ~ 30 µT)
- Increases by factor ~2 toward poles

**Plasma frequency:**

```r
ω_pe² = n_e·e² / (m_e·ε₀)     (13.34)
```

- ~10 MHz in ionosphere (n_e ~ 10¹² m⁻³)
- ~1 kHz in upper magnetosphere (n_e ~ 10⁸ m⁻³)

**Phase and group velocity:**

```r
v_p = ω/k     (13.8)
v_g = ∂ω/∂k   (13.9)
```

### 13.3 Atmospherics (Sferics)

**Composition:** Groundwave + sequence of skywaves (1-hop, 2-hop, etc.)

- Atmosphere conducting above 70–90 km altitude
- Earth–ionosphere waveguide cutoff: ~1–3 kHz

**Skywave timing — source range and ionospheric height:**

Planar approximation:

```r
r = (c/2) · (Δt₂² - 4Δt₁²) / (4Δt₁ - Δt₂)     (13.79)

h = (c/2) · (Δt₁·Δt₂)^(1/2) · (Δt₂ - Δt₁)^(1/2) / (4Δt₁ - Δt₂)^(1/2)     (13.80)
```

Spherical geometry (1st hop):

```r
h₁ = R_e·cos²(r/2R_e) + [(cΔt₁+r)/2]² - 1 + R_e²·cos²(r/2R_e) - 1]^(1/2)     (13.81)
```

**Key measurements:**

- Mean ionospheric reflecting height: 86–88 km (night, ~1000 km range)
- Schonland et al. (1940): observed sferics 200–3000+ km at night

**Slow-tail separation (Wait 1962):**

```r
√t_s = 0.3 · r / (√(2h·ω_r)) + δ_c     (13.83)
```

- δ_c ≈ 5 ms (source term)
- Day effective conductivity: ~1×10⁻⁶ S m⁻¹
- Night effective conductivity: ~3×10⁻⁶ S m⁻¹

**Empirical range relations (Hepburn & Pierce 1953):**

```r
Day:   t = 0.33r - 350 (µs);   τ/4 = 500 + 0.23r (µs)
Night: t = 0.13r - 140 (µs);   τ/4 = 500 + 0.8r  (µs)
```

(r in km)

**Ionospheric conductivity model (Wait & Spies 1965):**

```r
ω_p²/ν_e = 2.5 × 10⁵ exp[β(z - h')]     (s⁻¹)     (13.85)

ν_e = 1.816 × 10¹¹ exp(-0.15z)            (s⁻¹)     (13.86)
```

- β = inverse scale height (km⁻¹)
- h' = reference height (km)
- Day-time east–west: β = 0.35 km⁻¹, h' = 72 km
- Night-time: β = 0.6 km⁻¹, h' = 84 km

### 13.4 Schumann Resonances

**Ideal cavity resonant frequencies:**

```r
f_N⁰ = (c / 2πR_e) · √[N(N+1)]     (13.88)
```

- R_e = 6400 km; 2πR_e = 40,000 km
- Ideal: f₁ = 10.6, f₂ = 18.3, f₃ = 25.9 Hz

#### Table 13.1 — Principal Schumann Resonance Characteristics

| Property                         | Vertical E Field            | Horizontal B Field          |
| -------------------------------- | --------------------------- | --------------------------- |
| Resonant frequencies (Hz)        | 7.8, 14, 20, 26, 33, 39, 45 | 7.8, 14, 20, 26, 33, 39, 45 |
| Diurnal variation                | ±0.5 Hz                     | ±0.5 Hz                     |
| Amplitude                        | ~100–200 µV m⁻¹ Hz⁻¹/²      | ~0.5–1 pT Hz⁻¹/²            |
| Diurnal amplitude variation      | ±50–100 µV m⁻¹ Hz⁻¹/²       | ±0.25–0.5 pT Hz⁻¹/²         |
| Time of max (western hemisphere) | 2000–2200 UT                | 2000–2200 UT                |
| Polarization                     | Linear (vertical)           | Linear (horizontal)         |

**Q-factor:**

```r
Q_N = f_N / Δf_N     (13.87)
```

- Average Q-factors: 3–6
- First mode (8 Hz): damping time ~0.5 s
- ~50 flashes worldwide during 0.5 s damping time

**Q-bursts:** Individual large-lightning excitations; exceed background by factor ≥10; 50–100 per hour; correlated with large positive CG flashes that produce sprites.

**Cavity conductivity:**

- Earth: 10⁻⁴ S m⁻¹ (sand) to 5 S m⁻¹ (salt water) → σ ≫ ωε₀ at ELF → perfect conductor
- Atmosphere conducting above 45–60 km at ELF; σ ~ 2×10⁻¹⁰ to 4×10⁻⁹ S m⁻¹

**Slab-ionosphere model (Wait 1962a,b):**

```r
E_r(θ,ω) = [iI(ω)ds·m(m+1)] / [4πωε₀hR_e²] × Σ[(2n+1)P_n(cosθ)] / [n(n+1) - m(m+1)]     (13.89)
```

**Climate link:** Williams (1992) demonstrated 6-year correlation between tropical temperature variations and first Schumann mode intensity. 0.2°C increase → measurable increase in Schumann resonance.

### 13.5 Whistlers

**Discovery:** Barkhausen (1919) — whistling tones on German army receivers, WWI. Storey (1953) — proved hemisphere-to-hemisphere propagation along geomagnetic field lines; first evidence of plasma beyond F-layer.

**Frequency range:** ~100 Hz to >10 kHz
**First-hop dispersion time:** ~1 s

**Refractive index for whistler-mode propagation (along B₀):**

```r
n_i = [ω_pe² / ω(|ω_be| - ω)]^(1/2)     (13.97)
```

- n_i ≫ 1 (e.g., ~100 at F-layer peak for f ~ 5 kHz)
- Therefore θ_t ≈ 0 → propagation essentially vertical in ionosphere

**Propagation time:**

```r
t(ω) = ∫ v_g⁻¹ dl     (13.98)

v_g⁻¹ = (µ₀ε₀)^(1/2) · ω_pe / [2ω^(1/2) · |ω_be|^(1/2) · (1 - ω/|ω_be|)^(3/2)]     (13.99)
```

**Eckersley dispersion law (low-frequency approximation, ω ≪ ω_be):**

```r
D = t(f) · f^(1/2) = [(µ₀ε₀)^(1/2) / (2√(2π))] · ∫ ω_pe / |ω_be|^(1/2) dl     (13.102)
```

- D = dispersion (independent of frequency)
- Lower frequencies arrive later → whistling tone

**Nose frequency:** f_n = f_be/4 (homogeneous plasma) — frequency of minimum propagation time

**Ducting conditions:**

- ω < ω_be/2: ducted in electron-density enhancement along field line
- ω > ω_be/2: ducted in electron-density trough
- Duct diameters: ~50 km; density enhancement: 10–100%
- Duct lifetimes: minutes to hours

**Plasmapause:** Abrupt density decrease at 4–5 Earth radii; n_e ~ 100 cm⁻³ just below, two orders of magnitude less above. First identified via whistler measurements (Carpenter 1966).

### 13.6 Radio Noise

- ~100 flashes/s worldwide → continuous background EM noise
- Noise dip at 1–3 kHz (waveguide cutoff)
- Below cutoff: whistlers, hiss, chorus, Schumann resonances
- Above cutoff: sferic pulses with ~1–100 ms separation
- Tropical stations (e.g., Kochi, Japan) show substantially higher noise than high-latitude stations

---

## Chapter 14 — Lightning Effects in Middle and Upper Atmosphere

### 14.1 Overview

| Phenomenon        | Altitude (km)         | Color                   | Association                                 | Duration             |
| ----------------- | --------------------- | ----------------------- | ------------------------------------------- | -------------------- |
| **Blue starters** | 18–26                 | Blue                    | Not associated with individual CG lightning | ~200 ms              |
| **Blue jets**     | 18–43                 | Blue                    | Not associated with individual CG lightning | ~200 ms              |
| **Red sprites**   | 40–90 (most luminous) | Red body, blue tendrils | Large +CG flashes                           | Few ms to tens of ms |
| **Sprite halos**  | 70–85                 | Diffuse                 | +CG and −CG                                 | ~1 ms                |
| **Elves**         | ~90                   | Expanding circles       | Individual lightning (radiation fields)     | <1 ms                |

Predicted since Wilson (1925a,b) via runaway electrons; first recorded by Franz et al. (1990).

### 14.2 Upward Lightning from Cloud Tops

- Similar to cloud-to-air discharges but projecting upward
- Photographed at night from U-2 aircraft at 20 km (Vonnegut et al. 1989)
- Short length relative to sprites/jets
- Associated with storms having large vertical development

### 14.3 Blue Starters

**Wescott et al. (1996) — 28 events over Arkansas thunderstorm:**

- Length: <10 km, typically a few km
- Origin altitude: mean 18 km (σ = 0.9 km)
- Top altitude: 18–26 km
- Upward speed: 2.7×10⁴ to 1.5×10⁵ m s⁻¹ (decreases during propagation)
- Brightness: ~1 MR near origin
- Mean volume: 2.4×10⁹ m³
- Only 3% of light from ionized N₂ → "at least partially ionized"
- Not coincident with CG lightning; CG flash rate decreased ~3 s after starter
- Associated with very strong updrafts

### 14.4 Blue Jets

**Wescott et al. (1995) — 56 jets over Arkansas storm:**

- Upward speed: ~10⁵ m s⁻¹ (similar to stepped-leader speed below cloud)
- Terminal altitude: 33–43 km
- Shape: cone, apex angle 6.5°–31.5° (mean 14.7°); trumpet-shaped flare at top
- Duration: ~200 ms of luminosity, then fades along whole path simultaneously
- Brightness: ~0.5 MR at base, ~7 kR at top
- Rate: ~2.8 per minute during active storm period

**Color photograph (Fig. 14.3):** Base ~19 km, tip ~40 km over Indian Ocean.

**Wescott et al. (2001a):** Observed jet separating from stem and continuing upward:

- Initial speed: 23 km s⁻¹
- Brightens at 133 ms
- Separated top propagates at 91 km s⁻¹ for additional 133 ms

**Models:**

- Pasko et al. (1996a): +300–400 C charge at 20 km → streamer-type ionization channel
- Sukhorukov et al. (1996a): attachment-controlled ionization wave carrying negative charge upward via electron avalanches; requires >100 C positive charge removal at cloud top

### 14.5 Red Sprites

**Morphology:**

- **"Carrot" sprites:** Bright red head (65–75 km), red hair/glow above (to 95 km), blue tendrils below (to ~20–40 km)
- **"Angel" sprites:** Head + diffuse halo ("sprite halo") above
- **"Columniform" sprites:** Vertical cylinders ~10 km high, <1 km diameter; uniform brightness

**Physical characteristics:**

- Most luminous: 40–90 km altitude
- Cluster horizontal extent: >40 km; volumes >10⁴ km³
- Individual luminous elements: tens of meters to few hundred meters (65–80 km)
- Initial development: columniform near 75 km → upward/downward corona-like streamers at >10⁷ m s⁻¹

**Optical intensity:**

- Average (standard video): 25–50 kR; max recorded 600 kR
- Photometer measurements: peak 0.5–10 MR (1 ms duration)
- Sprite halos: 0.1 MR to tens of MR (1 ms duration)
- Spectral passband correction: actual brightness ~6× measured

**Spectral properties:**

- Red: first positive band of N₂
- Blue: N₂ second positive (399.8 nm) and N₂⁺ first negative (427.8 nm)
- Blue emission precedes red (initial energetic ionization → secondary processes)

**Duration:**

- Sprites: few ms to many tens of ms
- Sprite halos: ~1 ms
- Elves: <1 ms

**Lightning association:**

- Primarily large +CG strokes (Boccippio et al. 1995: 86% and 78% coincidence in two MCSs)
- Median current of sprite-producing +CG = 2× non-sprite-producing +CG
- Two sprites observed with −CG (Barrington-Leigh et al. 1999): charge-moment changes up to 1550 C km in 5 ms
- Occur above stratiform precipitation region of MCSs, not near high-reflectivity core

**Charge transfer values:**

- Cummer & Inan (1997): 25–325 C in first 5 ms of positive strokes
- Bell et al. (1998): peak continuing current 6–180 kA; charge transfer 10–112 C

**Sprite ELF radiation (Cummer et al. 1998):**

- Current moments: 100–200 kA km
- Peak sprite currents: 1–4 kA
- Charge transfers: 5–42 C
- Average current density j ~ 3 µA m⁻²
- At 80 km (σ ~ 10⁻⁷ S m⁻¹): E ~ 33 V m⁻¹

**Sprite generation mechanisms:**

1. Rapid removal of ~100 C positive charge → short time delay (<16.7 ms)
2. Initial removal of 10–50 C → followed by slower charge transfer to ~100 C total → longer delay (40–120 ms)

### 14.6 Elves

- Occur at ~90 km in lower ionosphere
- Expanding circles of light from point above causative flash
- Duration: <1 ms
- Caused by radiation fields of return strokes (and possibly initial breakdown) accelerating ionospheric electrons
- Accompany many lightning flashes (both polarities)

### 14.7 Runaway Electrons, X-rays, Gamma-rays

**Runaway electrons:** Gain more energy from ambient E field between collisions than they lose in collisions → continue accelerating.

- Predicted by Wilson (1925a,b) as mechanism for cloud-top-to-ionosphere discharge
- Important in coupling energy from lower atmosphere to middle atmosphere and ionosphere

**Key phenomena:**

- Lightning-produced X-rays and gamma-rays
- Terrestrial gamma-ray flashes (TGFs)
- Potential production of runaway breakdown in thunderstorm electric fields

### 14.8 Ionosphere/Magnetosphere Interactions

**Lightning effects on ionosphere:**

- Sprites and elves change lower ionospheric properties
- Altered VLF radiowave propagation (well documented)
- Thundercloud quasi-static electric fields penetrate ionosphere → heating → potential infrared glow at ionospheric bottom

**Whistler-induced precipitation:**

- Whistlers in magnetospheric ducts → interaction with energetic radiation-belt electrons
- Precipitation of electrons → enhanced ionization and optical emissions in lower ionosphere
- X-rays detectable to ~30 km altitude

---

## Cross-Chapter Summary: Key Quantitative Parameters

| Parameter                                  | Value                              | Source                         |
| ------------------------------------------ | ---------------------------------- | ------------------------------ |
| Return-stroke input energy (gas dynamic)   | ~(2–4) × 10³ J m⁻¹                 | Table 12.1                     |
| Return-stroke input energy (Krider)        | 2.3 × 10⁵ J m⁻¹                    | Krider et al. (1968)           |
| MTLE decay constant λ                      | 2000 m                             | Nucci et al. (1988a)           |
| DU time constant τ_D                       | 0.1 µs                             | Thottappillil & Uman (1993)    |
| M-component wave speed v                   | 2.5–3.0 × 10⁷ m s⁻¹                | Rakov et al. (1995)            |
| Dart-leader speed                          | typically >10⁷ m s⁻¹               | Section 4.7                    |
| Ionospheric reflecting height (night)      | 86–88 km                           | Caton & Pierce (1952)          |
| Earth–ionosphere waveguide cutoff          | ~1–3 kHz                           | Section 13.3                   |
| Schumann resonance f₁ (observed)           | 7.8 Hz                             | Table 13.1                     |
| Schumann resonance Q-factor                | 3–6                                | Sentman (1995)                 |
| Whistler first-hop dispersion time         | ~1 s                               | Section 13.5                   |
| Whistler refractive index (F-layer, 5 kHz) | ~100                               | Eq. 13.97                      |
| Sprite altitude range                      | 40–90 km                           | Sentman et al. (1995)          |
| Sprite peak brightness                     | 0.5–10 MR                          | Cummer et al. (1998)           |
| Sprite peak current                        | 1–4 kA                             | Cummer et al. (1998)           |
| Blue-jet speed                             | ~10⁵ m s⁻¹                         | Wescott et al. (1995)          |
| Blue-jet terminal altitude                 | 33–43 km                           | Wescott et al. (1995)          |
| Elves altitude                             | ~90 km                             | Section 14.4                   |
| Elves duration                             | <1 ms                              | Barrington-Leigh et al. (2001) |
| Sprite-producing +CG charge transfer       | 25–325 C (first 5 ms)              | Cummer & Inan (1997)           |
| Plasmapause electron density               | ~100 cm⁻³ (below); ~1 cm⁻³ (above) | Carpenter (1966)               |
