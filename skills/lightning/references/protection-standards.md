# Lightning Protection & Standards

## Four Damage Mechanisms

| Property       | Mechanism                         | Key Values                          |
| -------------- | --------------------------------- | ----------------------------------- |
| Peak current I | Resistive voltage V=RI            | 30 kA into 250 ohm → 7.5 MV         |
| Max dI/dt      | Inductive voltage V=L*dI/dt       | 10^10 A/s × 1 uH/m → 10 kV/m wire   |
| Charge ∫Idt    | Burn-through (arc-metal ~5-10 V)  | CC causes more damage than RS       |
| Action ∫I^2dt  | Joule heating, explosive fracture | Neg 5%: 5.5x10^5 A^2s; Pos 5%: 10^7 |

## Protection Types

### Structural: Air Terminals + Down Conductors + Grounding

### Surge Protection Devices (SPDs)

| Type            | Action                        | Examples                        |
| --------------- | ----------------------------- | ------------------------------- |
| Voltage crowbar | Short to ground (~20 V arc)   | Gas tubes, SCRs                 |
| Voltage clamp   | Clamp ~30-50% above operating | MOVs, Zener diodes              |
| Circuit filter  | Reflect/absorb unwanted freq  | Series inductors                |
| Isolation       | Large series impedance        | Optical isolators, transformers |

SPDs connected in **parallel** with equipment.
Multi-stage: primary (entrance) → secondary (outlets); coordinate clamping
voltages.

## Zone of Protection Methods

### Rolling Sphere (IEC 61024-1)

| Protection Level | Sphere R (m) | Min I_peak (kA) | Interception Prob |
| ---------------- | ------------ | --------------- | ----------------- |
| I                | 20           | 2.9             | 99%               |
| II               | 30           | 5.4             | 97%               |
| III              | 45           | 10.1            | 91%               |
| IV               | 60           | 15.7            | 84%               |

Mesh sizes: Level I = 5x5 m, II = 10x10 m, III = 15x15 m, IV = 20x20 m.

### Striking Distance Formula

r = A * I^b (meters, kiloamperes)

| Source                | A    | b    |
| --------------------- | ---- | ---- |
| Love (1973) / IEEE    | 10.0 | 0.65 |
| Armstrong & Whitehead | 6.0  | 0.80 |
| Brown & Whitehead     | 6.4  | 0.75 |

See `scripts/protection.py` for implementations.

## Grounding

Hemispherical electrode: R_gr = rho / (2*pi*a)
Vertical rod (Dwight 1936): R\_gr = (1/(2*pi*sigma*l)) \* \[ln(8l/d) - 1\]

R inversely proportional to rod length and conductivity; **relatively
independent of rod diameter**.

### Soil Resistivity

| Material    | rho (ohm*m) |
| ----------- | ----------- |
| Ocean water | 0.1-0.5     |
| Clay        | 25-70       |
| Sandy clay  | 40-300      |
| Sand        | 1000-3000   |
| Moraine     | 1000-10,000 |

### Soil Breakdown

E_b: 100-500 kV/m. For I=30 kA, sigma=10^-3 S/m, E_b=300 kV/m:
breakdown radius r_0 ≈ 4 m.

### Conductor Specs (IEC 61024-1)

| Material  | Min Cross-Section            |
| --------- | ---------------------------- |
| Copper    | 16 mm^2 (solid tape 50 mm^2) |
| Aluminum  | 25 mm^2                      |
| Steel     | 50 mm^2                      |
| Stainless | 100 mm^2                     |

Rod tip: Moore et al. (2000): blunt rods struck, NO sharp rods struck
in 5-year test. Optimal tip height:radius ≈ 680:1.

## Topological Shielding

Perfect Faraday cage → no internal voltage differences.
Practical: nested shields; wires pass through SPDs at each boundary.
Level 1 (building): limit to ~500-1000 V. Level 2 (cabinet): <few volts.

## Non-Conventional (Disputed)

**Lightning eliminators** (charge-transfer arrays): NO scientific evidence.
**ESE (early streamer emission)**: rejected by most scientists. Moore 7-year
test: no ESE or sharp rods struck; only blunt rods struck.

## Test Standards

| Standard             | Waveform                           |
| -------------------- | ---------------------------------- |
| Power equipment      | 1.2/50 us voltage, 8/20 us current |
| Telecom protectors   | 10/1000 us (50-500 A)              |
| Ring wave            | 0.5 us rise, 100 kHz oscillation   |
| Service entrance SPD | 10/350 us current                  |

Protection efficacy: unprotected:protected damage ratio ~60:1.
