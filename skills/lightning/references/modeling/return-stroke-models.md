# Return Stroke Modeling (Chapter 12)

## Four Classes of Models

| Class                           | Approach                                                          | Primary Output                            | Key Feature                                |
| ------------------------------- | ----------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------ |
| (i) Gas dynamic                 | Conservation of mass/momentum/energy + 2 eqs of state             | T, P, rho vs radial coord & time          | Radial evolution of channel segment        |
| (ii) Electromagnetic            | Lossy thin-wire antenna; numerical Maxwell's eqs (MOM)            | Current distribution → remote E, B fields | Antenna-mode + TL-mode current             |
| (iii) Distributed-circuit (RLC) | Transient on vertical transmission line (R, L, C per unit length) | Channel current vs time & height          | Approximation to EM models                 |
| (iv) Engineering                | Specified spatial/temporal current from observations              | EM fields at 10s m to 100s km             | Few adjustable params (1-2 + base current) |

## Gas Dynamic Models (Braginskii 1958)

Channel radius: r(t) = 9.35 \[I(t)\]^(1/3) * t^(1/2)

- r in cm, I in A, t in s
- sigma = 2.22x10^4 S/m; ambient density = 1.29x10^-3 g/cm^3

Resistance per unit length: R(t) = \[sigma \* pi \* r^2(t)\]^-1

Input current: rises to ~20 kA in few us, decays in tens of us.
Initial conditions: T ~10,000 K, r ~1 mm, P = 1 atm (old channel)
or rho = ambient (new channel).

## Engineering Models

### Transmission Line (TL) Model (Uman & McLain 1969)

I(z,t) = I(0, t - z/v) for z <= vt; 0 for z > vt

- Current travels up at speed v without modification
- v = return stroke speed (~1-2x10^8 m/s)
- Simplest; predicts far-field well

### Modified TL Models

| Model                 | Current Attenuation                              | Reference                |
| --------------------- | ------------------------------------------------ | ------------------------ |
| MTLL (linear)         | I(0,t-z/v) * (1 - z/H)                           | Rakov & Dulzon (1987)    |
| MTLE (exponential)    | I(0,t-z/v) * exp(-z/lambda)                      | Nucci et al. (1988)      |
| TCS                   | I(0,t-z/v) * f(z,v)                              | Heidler & Hopf (1994)    |
| DU (traveling source) | Special treatment of current waveshape vs height | Diendorfer & Uman (1990) |

lambda (MTLE): ~2000 m; H (MTLL): ~7-8 km; v: typically 1.3x10^8 m/s.

### Bruce-Golde (BG) Model

I(z,t) = I(0,t) for z <= vt

- Current instantaneously uniform up to wavefront
- Unrealistic but simple for some calculations

## Channel-Base Current Functions

### Heidler Function (IEC 62305)

I(t) = (I_0/eta) * (t/tau_1)^n / \[1 + (t/tau_1)^n\] \* exp(-t/tau_2)

- I_0: current peak; tau_1: front; tau_2: decay
- n: exponent (~10); eta: amplitude correction factor
- Used in IEC lightning protection standards

### Double-Exponential (CIGRE)

I(t) = I\_0 * \[exp(-alpha*t) - exp(-beta*t)\]

### Typical Parameters (First Stroke)

- I\_0 = 28 kA; tau\_1 = 1.8 us; tau_2 = 95 us; n = 10 (Heidler)

## Electromagnetic Field Computation

### General Formulation

E and B fields at distance r from vertical channel (Uman et al. 1975):
Three components of E_z(r,t):

1. **Electrostatic** (1/r^3): dominant at close range
2. **Induction** (1/r^2): intermediate range
3. **Radiation** (1/r): dominant at far range (>50 km)

Crossover distance (electrostatic = radiation): ~5-10 km for typical
return stroke parameters.

Far-field peak: E\_rad = -(v \* mu_0)/(2\*pi\*r) \* dI/dt|max (for TL model)

## Model Testing

Models tested against: (1) triggered-lightning current + fields at
known distances, (2) natural-lightning fields at multiple stations.

| Model | Close range (<1 km)   | Intermediate (1-200 km) | Far field (>200 km) |
| ----- | --------------------- | ----------------------- | ------------------- |
| TL    | Poor (no attenuation) | Good                    | Good                |
| MTLE  | Good                  | Good                    | Good                |
| MTLL  | Good                  | Good                    | Good                |
| BG    | Poor                  | Poor (field reversal)   | Acceptable          |

MTLE and MTLL: best overall performers for engineering applications.
