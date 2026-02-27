# Lightning Locating Systems

## EM Spectrum of Lightning

Peak radiation: **5-10 kHz** (beyond 50 km).
Above peak: ~1/f to 10 MHz, then ~1/sqrt(f) to 10 GHz.

## Three Main Techniques

| Technique      | Frequency     | Capability                 | Accuracy |
| -------------- | ------------- | -------------------------- | -------- |
| MDF            | VLF/LF        | Ground strike point        | 1-4 km   |
| TOA            | VLF/LF to VHF | Strike point or 3D imaging | <1 km    |
| Interferometry | VHF           | 3D channel imaging         | ~2 km    |

## Magnetic Direction Finding (MDF)

Two orthogonal loops: ratio of outputs = tan(azimuth).

### Gated Wideband DF

- Developed 1970s by Krider et al.
- Bandwidth: few kHz to ~500 kHz
- Samples initial peak (first us, bottom ~100 m of channel)
- Azimuthal error: sigma = 1.8 deg (flat terrain)
- Network (100 km spacing): 2-4 km location error, ~70% DE

## Time-of-Arrival (TOA)

### VHF Short-Baseline (~10s km)

| System         | Freq                | Resolution | Notes                          |
| -------------- | ------------------- | ---------- | ------------------------------ |
| Proctor        | 253/355 MHz         | ~100 m     | 5 stations, 10-40 km baselines |
| LDAR (KSC)     | 66 MHz              | ~100 m     | 7 receivers, 20 km diameter    |
| Thomson et al. | dE/dt, 800 Hz-4 MHz | **<100 m** | 5 stations, <50 ns timing      |

### Long-Baseline (100s-1000s km)

LPATS: LF/VLF whip antennas, 200-400 km spacing, GPS timing.
Latest location errors: **<1 km**. Cloud contamination ~20%.

## US National Lightning Detection Network (NLDN)

### History

| Year    | Event                                        |
| ------- | -------------------------------------------- |
| 1976    | BLM DF system (western US)                   |
| 1989    | NLDN begins real-time operation              |
| 1994-95 | Major upgrade: combined DF + TOA             |
| 1998    | Combined with Canadian → NALDN (187 sensors) |

### Post-1995 Performance

| Parameter                      | Value                      |
| ------------------------------ | -------------------------- |
| Sensors                        | 106 (47 IMPACT + 59 LPATS) |
| Sensor spacing                 | ~300 km                    |
| **Location error (median)**    | **500 m - 1 km**           |
| **Flash detection efficiency** | **80-90%** (Ip > 5 kA)     |
| Data latency                   | <40 s                      |
| Coverage                       | 20 million km^2 (NALDN)    |

### Peak Current Estimation

TL model: **I = 0.185 * RNSS** (kA)
Range normalization exponent: -1.13.
Median estimation error: **20-30%** (validated against triggered lightning).

### Flash Grouping

- Subsequent strokes within 10 km of first
- Within 500 ms of previous stroke
- Max flash duration: 1 s; max multiplicity: 15

## Interferometry

Measures VHF phase difference between closely-spaced antennas.

| System                | Freq        | Resolution        |
| --------------------- | ----------- | ----------------- |
| SAFIR (commercial)    | 110-118 MHz | ~2 km at 100 km   |
| NMIMT (Rhodes et al.) | 274 MHz     | 1 deg (high elev) |

SAFIR vs LDAR observe **different aspects** of discharges.

## Satellite Detection

| Sensor     | Orbit          | Resolution   | DE     |
| ---------- | -------------- | ------------ | ------ |
| OTD (1995) | 735 km, 70 deg | ~10 km, 2 ms | 46-69% |
| LIS (1997) | TRMM, 35 deg   | <10 km       | ~90%   |
| DMSP       | 830 km         | ~100 km      | ~2%    |

Cannot distinguish cloud from ground flashes.

## Radar Detection

- Lightning channels reflective at RF for 100s ms (T > 5000 K)
- Reflectivity decay: ~0.2 dB/ms
- Wavelength >=10 cm needed (avoid precipitation masking)

## Electrostatic Field-Change Networks

Point-charge model: 4 unknowns → 4 stations minimum.
Dipole model: 7 unknowns → 7 stations.
Location uncertainty: 1-2 km (requires 1-2% field accuracy).
