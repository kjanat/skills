# Return Stroke Models

## Four Model Classes

| Class               | Approach                       | Output                     | Feature                   |
| ------------------- | ------------------------------ | -------------------------- | ------------------------- |
| Gas dynamic         | Conservation laws + EOS        | T, P, rho vs radius & time | Radial channel evolution  |
| Electromagnetic     | Lossy thin-wire antenna; MOM   | Current → remote E, B      | Antenna + TL modes        |
| Distributed-circuit | RLC transmission line          | I vs time & height         | Approximation to EM       |
| Engineering         | Specified current distribution | EM fields at all ranges    | Few adjustable parameters |

## Gas Dynamic Models

### Braginskii (1958) Channel Radius

r(t) = 9.35 \* I(t)^(1/3) \* t^(1/2)
(r in cm, I in A, t in s; sigma = 2.22x10^4 S/m)

R(t) = 1 / (sigma \* pi \* r^2(t)) (resistance/length)
W(t) = integral_0^t I^2(tau) * R(tau) dtau (energy/length)

Initial conditions: T ~10,000 K, r ~1 mm, P = 1 atm (old channel)
or rho = ambient density 1.29x10^-3 g/cm^3 (new channel).
Input current: rises to ~20 kA in few us, decays in tens of us.

### Energy Estimates

| Source               | Peak I (kA) | W (J/m)   | Notes               |
| -------------------- | ----------- | --------- | ------------------- |
| Hill (1971)          | 21          | ~3x10^3   | Corrected           |
| Plooster (1971b)     | 20          | 2.4x10^3  | 50% radiated        |
| Paxton et al. (1986) | 20          | 4x10^3    | 69% radiated        |
| Krider et al. (1968) | —           | 2.3x10^5  | Optical calibration |
| Uman (2001)          | —           | 10^5-10^6 | Electrostatic       |

**Key discrepancy**: gas dynamic → ~10^3 J/m; Krider → ~10^5 J/m.

## Channel-Base Current Functions

### Heidler Function (IEC 62305)

I(t) = (I\_0/eta) \* (t/tau\_1)^n / \[1 + (t/tau\_1)^n\] \* exp(-t/tau\_2)

- I\_0: current peak; tau\_1: front time; tau\_2: decay time
- n: exponent (~10); eta: amplitude correction factor
- Used in IEC lightning protection standards

### Double-Exponential (CIGRE)

I(t) = I\_0 \* \[exp(-alpha\*t) - exp(-beta\*t)\]

### Typical Parameters (First Stroke)

- I\_0 = 28 kA; tau\_1 = 1.8 us; tau\_2 = 95 us; n = 10 (Heidler)

## Engineering Models

### Generalized Current Equation (Rakov 1997)

I(z', t) = u(t - z'/v\_f) \* P(z') \* I(0, t - z'/v)

- u = Heaviside function
- P(z') = height-dependent attenuation factor
- v\_f = return-stroke front speed
- v = current-wave propagation speed

### Model Parameters

| Model                     | P(z')           | v        | Year |
| ------------------------- | --------------- | -------- | ---- |
| **TL** (Uman & McLain)    | 1               | v\_f     | 1969 |
| **MTLL** (Rakov & Dulzon) | 1 - z'/H        | v\_f     | 1987 |
| **MTLE** (Nucci et al.)   | exp(-z'/lambda) | v\_f     | 1988 |
| **BG** (Bruce & Golde)    | 1               | infinity | 1941 |
| **TCS** (Heidler)         | 1               | -c       | 1985 |

- H = total channel height (~7-8 km)
- lambda = decay constant (typically 2000 m)
- c = speed of light
- v typically 1.3x10^8 m/s

### Two Model Families

1. **TL-type** (TL, MTLL, MTLE): current wave propagates **upward** at v\_f
2. **TCS-type** (BG, TCS, DU): current wave propagates **downward** at -c

## Electromagnetic Field Computation

### E-Field Three-Component Decomposition

E and B fields at distance r from vertical channel (Uman et al. 1975).
Three components of E\_z(r,t):

1. **Electrostatic** (1/r^3): dominant at close range
2. **Induction** (1/r^2): intermediate range
3. **Radiation** (1/r): dominant at far range (>50 km)

Crossover distance (electrostatic = radiation): ~5-10 km for typical
return stroke parameters.

### TL Model Far-Field Relations

E\_z\_rad(r,t) = -v / (2\*pi\*eps\_0\*c^2\*r) \* I(0, t-r/c)
dE\_z\_rad/dt = -v / (2\*pi\*eps\_0\*c^2\*r) \* dI(0,t-r/c)/dt
|B\_phi\_rad| = |E\_z\_rad| / c

Equivalent form: E\_rad = -(v \* mu\_0)/(2\*pi\*r) \* dI/dt|max

### Model Validation Ranking

**Best to worst**: MTLL > DU > MTLE > TCS > BG > TL

| Criterion                        | Pass              |
| -------------------------------- | ----------------- |
| Sharp 1/r peak beyond ~1 km      | All               |
| Slow ramp >100 us (<few tens km) | All except TL     |
| Magnetic hump 10-40 us           | BG, TL, TCS       |
| Zero-crossing 50-200 km          | MTLE only         |
| Close-range (50 m) flattening    | BG, MTLL, TCS, DU |

### Range-Dependent Performance

| Model | Close (<1 km)         | Intermediate (1-200 km) | Far (>200 km) |
| ----- | --------------------- | ----------------------- | ------------- |
| TL    | Poor (no attenuation) | Good                    | Good          |
| MTLE  | Good                  | Good                    | Good          |
| MTLL  | Good                  | Good                    | Good          |
| BG    | Poor                  | Poor (field reversal)   | Acceptable    |

TL recommended for peak-current <> peak-field (simplest, equal accuracy).
MTLE and MTLL: best overall for engineering applications.

## Electromagnetic Models

| Model                    | R (ohm/m)    | v\_p (m/s) |
| ------------------------ | ------------ | ---------- |
| Podgorski & Landt (1987) | 0.7          | —          |
| Moini et al. (2000)      | 0.065-0.07   | 1.3x10^8   |
| Baba & Ishii (2001)      | 1.0 + 3 uH/m | 1.5x10^8   |

v\_p = 1/sqrt(mu\_0 \* epsilon) with epsilon > eps\_0 to slow below c.

## Distributed-Circuit (RLC) Models

Telegrapher's equations:
-dV/dz' = L \* dI/dt + R\*I
-dI/dz' = C \* dV/dt

Typical R: 0.06-3.5 ohm/m.

## Dart-Leader Models

Uniformly charged line: rho\_L(z',t) = rho\_L0 \* u\[t-(H\_m-z')/v\]

- rho\_L0\*v\*t \* delta(H\_m-z') \* u(t)

Net charge = 0 at all times (point charge at origin simulates branched
in-cloud channels).

See `scripts/return_stroke_models.py` for engineering model implementations.
