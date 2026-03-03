# Rocket-Triggered Lightning

## History

First triggered discharge: 1960, small rockets trailing grounded wires from
research vessel off Florida coast (Newman 1965). First over land: 1973,
Saint-Privat d'Allier, France.

## Classical Triggering

- Rocket at ~150-200 m/s trailing grounded wire (~0.2 mm diameter)
- Typical wire length: 400-700 m
- At 200-300 m: enhanced field → upward positive leader
- Wire vaporizes ~1-2 ms after leader inception; arc channel replaces wire
- After ICC (if any), downward dart leaders + return strokes follow
- Ground E-field threshold: **4-10 kV/m** (Florida)
- Triggering potential at rocket altitude: **-3.6 MV**

## Altitude Triggering

- Ungrounded wire + insulating gap → bidirectional leader
- Short floating segment (~50-400 m)
- Positive charge up, negative charge down
- Downward leader: stepped, like natural first-stroke leader
- Produces first-stroke-like events (vs classical → subsequent-stroke-like)
- More difficult to achieve; requires higher ambient fields

## Triggering Success Rate

| Program                | Location       | Success Rate     |
| ---------------------- | -------------- | ---------------- |
| KSC, Florida           | Cape Canaveral | ~50-70%          |
| Camp Blanding, Florida | North FL       | ~50%             |
| Saint-Privat d'Allier  | France         | ~50-60%          |
| Various Japan sites    | Hokuriku coast | ~50-80% (winter) |

Success depends on: ambient E-field, storm proximity, rocket trajectory, wire length.

## Return-Stroke Current (Triggered)

| Parameter         | Florida KSC | France   |
| ----------------- | ----------- | -------- |
| Median peak (kA)  | **12.1**    | **9.8**  |
| Max dI/dt (kA/us) | **91.4**    | **36.8** |
| n                 | 305 / 134   | 54 / 47  |

Triggered RS ≈ **subsequent strokes** in natural lightning.
GM peaks from 6 experiments: narrow range 9.9-15 kA.

## Triggered vs Natural Comparison

| Parameter           | Triggered (subsequent)  | Natural (subsequent)    |
| ------------------- | ----------------------- | ----------------------- |
| Peak current        | 12 kA (GM)              | 12 kA (median)          |
| Max dI/dt           | ~100 kA/us              | 40 kA/us (median)       |
| Charge              | ~1 C                    | 1.4 C                   |
| Return stroke speed | (1-2)x10^8 m/s          | (1-2)x10^8 m/s          |
| Channel base height | Ground                  | Ground                  |
| Initial stage       | ICC (no stepped leader) | Stepped leader + 1st RS |

Key difference: classical triggering does not produce equivalent of natural
first return stroke. Altitude triggering can produce stepped-leader-like
first stroke.

## ICC Parameters (Triggered)

| Parameter               | Typical                | Range           |
| ----------------------- | ---------------------- | --------------- |
| Current                 | 100-400 A              | Up to few kA    |
| Duration                | ~300-500 ms            | ~100 ms to >1 s |
| Charge                  | 30-50 C (some >100 C)  | --              |
| Superimposed ICC pulses | ~kA peak, ~ms duration | --              |

## Key Finding: Grounding Independence

GM peak currents: **10-14 kA** regardless of grounding resistance
(0.1 ohm to 64 kohm). Lightning lowers its own grounding impedance via
fulgurites, surface arcing (up to 20 m), underground plasma channels.

## Scientific Applications

Measurement advantages:

- Known strike point: instruments immediately around channel base
- Current measured directly at ground (shunt resistor)
- Simultaneous multi-parameter: current, EM fields, optical, acoustic
- Repeatable conditions for channel-base characterization

Key results:

- Validated NLDN calibration (peak current vs field relationship)
- M-component mechanism confirmed (counter-propagating waves)
- Step voltage/touch voltage measurements for grounding studies
- Lightning interaction with power lines: direct injection experiments
- Soil ionization and transient grounding impedance measurements

## Major Triggered-Lightning Facilities

| Facility              | Location     | Active Years | Key Focus                             |
| --------------------- | ------------ | ------------ | ------------------------------------- |
| KSC / ICLRT           | Florida, USA | 1983-present | Comprehensive; power lines, grounding |
| Camp Blanding         | Florida, USA | 1993-present | Power systems, EM fields              |
| Saint-Privat d'Allier | France       | 1973-1996    | Pioneer program                       |
| Cachoeira Paulista    | Brazil       | 1999-present | Tropical lightning                    |
| Hokuriku coast sites  | Japan        | 1977-present | Winter lightning, power lines         |
| Langmuir Lab          | New Mexico   | 1972-1991    | High altitude (3.2 km ASL)            |

## Unsuccessful Techniques (as of 2003)

- Laser beams (plasma sigma ~10^-3 S/m vs copper 5.8x10^7)
- Microwave beams
- Water jets
- Transient flames
