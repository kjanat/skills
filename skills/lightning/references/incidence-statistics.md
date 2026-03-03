# Lightning Incidence & Statistics

## Global Flash Rate

- Brooks (1925): ~100 flashes/s (cloud + ground)
- Satellite (OTD+LIS): **45 +/- 5 s^-1**
- US annual CG flashes: ~25 million

## Flash Rate vs Storm Properties

| Storm Type              | Rate                                 |
| ----------------------- | ------------------------------------ |
| Average cell            | ~3 min^-1                            |
| Florida air-mass        | ~1 min^-1 CG                         |
| Severe storms (mean CG) | 2-6 min^-1                           |
| Severe (peak CG)        | ~20 min^-1                           |
| Severe Florida (total)  | 60-500 min^-1                        |
| MCC                     | 1000+ CG/hr for 9 hr; peak 60 min^-1 |

Flash rate vs cloud height: F = 3.44x10^-5 * H^4.9 (Williams 1985).

Updraft threshold: ~6-7 m/s (mean) or 10-12 m/s (peak).

## Ground Flash Density (Ng)

### Ng-Td Relationships

| Source                     | Formula           | Notes                   |
| -------------------------- | ----------------- | ----------------------- |
| Anderson et al. (1984a)    | Ng = 0.04*Td^1.25 | IEEE/CIGRE standard     |
| Kolokolov & Pavlova (1972) | Ng = 0.036*Td^1.3 | USSR                    |
| MacGorman et al. (1984)    | Ng = 0.054*Th^1.1 | Th = thunderstorm hours |
| Eriksson (1987)            | Ng = 0.04*Th      | South Africa            |

### US Flash Density

| Region        | Ng (km^-2 yr^-1) |
| ------------- | ---------------- |
| Pacific Coast | <=0.1            |
| Florida       | >=14             |

### Multiple Ground Terminations

- ~50% of CG flashes strike >1 point
- Separation: 0.3-7.3 km (Florida)
- Average terminations/flash: 1.7

## Cloud:Ground Ratio (z = Nc/Ng)

| Latitude  | z   |
| --------- | --- |
| 0-20 deg  | 4.0 |
| 20-40 deg | 3.2 |
| 40-60 deg | 1.9 |

Average z: ~3 (range 2-10+).
Prentice & Mackerras: z = 4.16 + 2.16*cos(3*lambda).

## Incidence to Structures

Eriksson (1987): N = 24x10^-6 \* Hs^2.05 \* Ng flashes/yr

| Height (m) | % Upward |
| ---------- | -------- |
| <100       | ~0       |
| 150        | 23       |
| 200        | 50       |
| 300        | 80       |
| >500       | ~100     |

Pu = 52.8*ln(Hs) - 230 (valid 78-518 m)

## Climate Sensitivity

- 5-6% change in global lightning per 1C warming (Price & Rind 1994)
- Alternative: 40% per 1C (Reeve & Tuomi 1999, OTD)
- Order of magnitude increase per 2C wet-bulb rise
- Minimum reliable observation period: 11 years (1 solar cycle)

## Seasonal Variation

- Summer: <5% positive flashes
- Winter: up to 80% positive (NE US, February)
- Single-stroke flashes: summer ~40%, winter >80%

## Geographic Patterns

| Factor                 | Effect                                  |
| ---------------------- | --------------------------------------- |
| Land:ocean flash ratio | 7.7 (monthly avg)                       |
| NH vs SH summer        | 1.4x more during NH summer              |
| Mountains              | ~1.7x higher Ng                         |
| Urban enhancement      | 40-85% increase over/downwind of cities |

See `scripts/incidence.py` for Ng-Td formulas, structure incidence, and
flash probability calculations.
