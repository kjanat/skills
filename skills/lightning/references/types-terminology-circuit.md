# Lightning Types, Terminology & Global Electric Circuit

## Four Types of Cloud-to-Ground Lightning

| Type              | Leader Direction | Charge Lowered | Prevalence          |
| ----------------- | ---------------- | -------------- | ------------------- |
| Downward negative | Downward         | Negative       | ~90% of CG          |
| Upward negative   | Upward           | Negative       | >100 m objects only |
| Downward positive | Downward         | Positive       | <10% of CG          |
| Upward positive   | Upward           | Positive       | >100 m objects only |

Cloud discharges: ~75% of all lightning. Includes intracloud, intercloud,
cloud-to-air.

## Terminology

| Term                    | Definition                                              |
| ----------------------- | ------------------------------------------------------- |
| **Flash**               | Entire discharge event                                  |
| **Strike**              | Discharge involving grounded/airborne object            |
| **Stroke**              | CG component: leader + return stroke                    |
| **Leader**              | Self-propagating discharge; sigma ~10^4 S/m             |
| **Streamer**            | Low-conductivity precursor; air behind tip insulating   |
| **Corona**              | Streamer cluster near electrode; NOT self-propagating   |
| **Stepped leader**      | Initiates first strokes                                 |
| **Dart leader**         | Initiates subsequent strokes in pre-formed channels     |
| **Dart-stepped leader** | Hybrid; some subsequent strokes                         |
| **Continuing current**  | Low-level arc post-stroke (tens-hundreds A)             |
| **M-component**         | Transient surge in continuing current; guided-wave      |
| **ICC**                 | Initial continuous current (upward/triggered lightning) |

## Three Charge Transfer Modes

1. **Leader-return-stroke**: Leader deposits charge; return stroke neutralizes.
   Front: ~10 m (dart leader), ~100 m (return stroke).
2. **Continuing current**: Quasi-stationary arc; 10-100s A; up to 100s ms.
3. **M-component**: Counter-propagating waves on existing channel; front ~1 km;
   requires conducting channel as waveguide.

Channel conductivity during all modes: ~10^4 S/m.

## Global Electric Circuit

### Atmospheric Conductivity vs Altitude

| Altitude  | sigma (S/m) | Notes                            |
| --------- | ----------- | -------------------------------- |
| Sea level | ~10^-14     | Small ions dominate              |
| 35 km     | >10^-11     | >1000x sea level                 |
| >60 km    | Rapid rise  | Free electrons ("electrosphere") |
| 100 km    | ~10^-2      | Comparable to Earth's bulk       |

Ion production at sea level: 1-10 million pairs/m^3/s.

### Fair-Weather Electric Field

- Surface: ~100-150 V/m (directed downward, positive charge above)
- Volland (1984): E(z) = -[93.8 exp(-4.527z) + 44.4 exp(-0.375z)
  - 11.8 exp(-0.121z)] V/m (z in km)

### Classical Circuit Model

| Quantity                              | Value                               |
| ------------------------------------- | ----------------------------------- |
| Electrosphere potential               | ~300 kV (positive w.r.t. Earth)     |
| Earth surface charge                  | ~5x10^5 C (negative)                |
| Fair-weather current                  | ~1 kA total (~2 pA/m^2)             |
| Neutralization time                   | ~10 min (without thunderstorms)     |
| Global load resistance                | ~300 ohm                            |
| Active storms (any time)              | ~2000                               |
| Current per storm                     | ~0.5 A (cloud top to electrosphere) |
| Carnegie curve peak                   | ~1900 UT                            |
| CG contribution to fair-weather field | ~40 +/- 10%                         |

### Maxwell Current Density

J_M = J_E + J_C + J_L + epsilon_0 (dE/dt)

- J_E: field-dependent (ohmic + corona)
- J_C: convection (including precipitation)
- J_L: lightning current density
- Under active storms: ~10 nA/m^2

### Energy Utilization

| Quantity                | Value                                 |
| ----------------------- | ------------------------------------- |
| Energy per CG flash     | ~10^9-10^10 J (~360 kWh)              |
| Energy at strike point  | 10^6-10^7 J (10^-2 to 10^-4 of total) |
| Action integral         | ~10^5 A^2s                            |
| 1 m^2 in Florida struck | Once per 10^5 yr                      |
| 60 m tower in Florida   | ~Once per 1-2 yr                      |

Impractical for energy harvesting: bulk lost to heating air, thunder, light,
radio waves.
