---
name: lightning
description: >-
  Comprehensive lightning physics knowledge base derived from Rakov & Uman
  (2003) "Lightning: Physics and Effects". Covers discharge types, current
  parameters, leader/return-stroke physics, cloud electrification, protection,
  detection systems, atmospheric effects, and quantitative reference data.
  Use when answering questions about lightning physics, electromagnetic fields,
  thunderstorm electricity, lightning protection, or atmospheric electrical
  phenomena.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
  source: "Rakov V.A., Uman M.A. - Lightning: Physics and Effects (2003, Cambridge University Press)"
---

# Lightning Physics Knowledge Base

Quantitative reference on lightning physics, effects, and protection. All data
from Rakov & Uman (2003) unless noted.

## Reading Order

| Task                                            | File                                       |
| ----------------------------------------------- | ------------------------------------------ |
| Lightning types, terminology, global circuit    | `references/types-terminology-circuit.md`  |
| Flash rates, density, geographic distribution   | `references/incidence-statistics.md`       |
| Thundercloud charge structure, electrification  | `references/cloud-electrification.md`      |
| Stepped leader physics                          | `references/stepped-leader.md`             |
| Return stroke currents, speed, channel, fields  | `references/return-stroke.md`              |
| Dart leader, continuing current, M-components   | `references/dart-leader-m-component.md`    |
| Positive, upward, and triggered lightning       | `references/positive-upward-triggered.md`  |
| Cloud discharges and winter lightning           | `references/cloud-winter-discharges.md`    |
| Aircraft interaction and thunder                | `references/aircraft-thunder.md`           |
| Return stroke modeling (engineering + physical) | `references/return-stroke-models.md`       |
| Sferics, Schumann resonances, sprites, TLEs     | `references/distant-em-upper-atmo.md`      |
| NOx production, extraterrestrial lightning      | `references/chemistry-extraterrestrial.md` |
| Lightning locating systems (NLDN, satellite)    | `references/locating-systems.md`           |
| Protection methods, grounding, standards        | `references/protection-standards.md`       |
| Human hazards, safety, ball lightning           | `references/human-hazards-unusual.md`      |

## Quick Reference: Key Parameters

### Flash Structure

| Parameter                    | Typical Value    |
| ---------------------------- | ---------------- |
| Strokes per flash            | 3-5 (range 1-26) |
| Flash duration               | 200-300 ms       |
| Interstroke interval         | 60 ms            |
| Total charge per flash       | 20 C             |
| Energy per flash             | 10^9-10^10 J     |
| Single-stroke flashes        | 15-20%           |
| Multiple ground terminations | ~50% of flashes  |

### Current Parameters (Berger et al. 1975)

| Parameter                     | First Stroke (median) | Subsequent (median) |
| ----------------------------- | --------------------- | ------------------- |
| Peak current                  | 30 kA                 | 12 kA               |
| Max dI/dt                     | 12 kA/us              | 40 kA/us            |
| Front duration (2 kA to peak) | 5.5 us                | 1.1 us              |
| Duration (to half-peak)       | 75 us                 | 32 us               |
| Impulse charge                | 4.5 C                 | 0.95 C              |
| Action integral               | 5.5x10^4 A^2s         | 6.0x10^3 A^2s       |

### Process Speeds

| Process          | Speed (m/s)             |
| ---------------- | ----------------------- |
| Stepped leader   | 2x10^5 (average)        |
| Dart leader      | 10^7 (typical)          |
| Return stroke    | (1-2)x10^8 (c/3 to c/2) |
| M-component wave | (2.5-3)x10^7            |

### Channel Properties

| Property         | Value                   |
| ---------------- | ----------------------- |
| Peak temperature | 28,000-31,000 K         |
| Peak pressure    | ~8 atm (first 5 us)     |
| Electron density | 8x10^17 cm^-3 (at 5 us) |
| Channel radius   | 1-4 cm                  |
| Conductivity     | ~10^4 S/m               |

### Lightning Types

| Type                 | Fraction            | Notes                                  |
| -------------------- | ------------------- | -------------------------------------- |
| Downward negative CG | ~90% of CG          | Most common                            |
| Downward positive CG | <10% of CG          | Higher peak currents at extremes       |
| Cloud discharges     | ~75% of all         | Intracloud, intercloud, cloud-to-air   |
| Upward (neg + pos)   | From >100 m objects | Only from tall structures/mountaintops |

### Global Statistics

| Quantity                        | Value                                      |
| ------------------------------- | ------------------------------------------ |
| Global flash rate               | 45 +/- 5 per second (satellite)            |
| Cloud:CG ratio (z)              | ~3 average (range 1-10+)                   |
| Land:ocean flash ratio          | ~7.7                                       |
| Active thunderstorms (any time) | ~2000                                      |
| US annual CG flashes            | ~25 million                                |
| US flash density range          | 0.1 (Pacific) to >14 (Florida) km^-2 yr^-1 |

### Positive Lightning Extremes

| Parameter       | 50%           | 5%            |
| --------------- | ------------- | ------------- |
| Peak current    | 35 kA         | 250 kA        |
| Charge transfer | 80 C          | 350 C         |
| Action integral | 6.5x10^5 A^2s | 1.5x10^7 A^2s |

## Terminology

| Term               | Definition                                                      |
| ------------------ | --------------------------------------------------------------- |
| Flash              | Entire lightning discharge                                      |
| Stroke             | Component of CG discharge (leader + return stroke)              |
| Leader             | Self-propagating discharge, conductivity ~10^4 S/m              |
| Streamer           | Low-conductivity precursor; air remains insulating              |
| Corona             | Non-self-propagating cluster of streamers near electrode        |
| Continuing current | Quasi-stationary arc (tens-hundreds of A, up to hundreds of ms) |
| M-component        | Current/luminosity surge during continuing current              |
| ICC                | Initial continuous current (upward/triggered lightning)         |

## Three Modes of Charge Transfer to Ground

1. **Leader-return-stroke**: Leader deposits charge; return stroke neutralizes.
   Front lengths: ~10 m (dart leader), ~100 m (return stroke).
2. **Continuing current**: Quasi-stationary arc; tens-hundreds of A; up to
   hundreds of ms.
3. **M-component**: Guided-wave perturbation in continuing current; front
   length ~1 km; requires existing conducting channel.

Key distinction: leader-return-stroke occurs without conducting path (leader
creates it); M-component requires existing path.
