# Aircraft Lightning & Thunder

## Aircraft Lightning

### Key Statistics

- **~90%** of strikes to aircraft are **aircraft-initiated**
- US commercial rate: 1 strike per **~3000 flight hours** (~once/year)
- Most strikes at **0C temperature level** (ambient -5 to 0C)

### Bidirectional Leader Mechanism

1. Ambient field ~50 kV/m in thunderclouds
2. Aircraft extremities enhance field to breakdown (~10x at altitude)
3. **Positive leader** launches first (lower threshold); ~1 A steady
4. **Negative stepped leader** from opposite end ~ms later: ~1 kA impulses
   at ~250 us intervals, steady current increasing to ~300 A
5. Pulse bursts (recoil streamers) follow; peaks up to ~3 kA

| Aircraft | Mean Ambient E_0 | Range      |
| -------- | ---------------- | ---------- |
| CV-580   | 51 kV/m          | 25-87 kV/m |
| C-160    | 59 kV/m          | 44-75 kV/m |

### Flash Statistics (CV-580 + C-160)

| Parameter               | Mean        | Range         |
| ----------------------- | ----------- | ------------- |
| Flash duration          | 400 ms      | 140 ms-1 s    |
| Steady current          | 330 A       | max 910 A     |
| Charge through aircraft | **60 C**    | —             |
| Highest dI/dt (C-160)   | 2x10^10 A/s | mean 6.5x10^9 |
| Highest current (C-160) | **20 kA**   | mean 4.8 kA   |

### Test Standards (SAE/EUROCAE ARP5412-5414)

| Component | Description                                                  |
| --------- | ------------------------------------------------------------ |
| A         | First return stroke: 200 kA peak, 2x10^6 A^2s                |
| B         | Intermediate current                                         |
| C         | Continuing current                                           |
| D         | Subsequent stroke                                            |
| H         | Multiple-burst: 10 kA pulses (from F-106B/CV-580/C-160 data) |

### Notable Accidents

| Event                   | Aircraft | Casualties   | Cause                                |
| ----------------------- | -------- | ------------ | ------------------------------------ |
| Pan Am 707 (1963)       | B707-121 | 81           | Fuel tank explosion                  |
| Apollo 12 (1969)        | Saturn V | 0            | Vehicle-initiated; 9 sensors damaged |
| Atlas-Centaur 67 (1987) | AC-67    | Vehicle lost | Guidance computer upset              |

Apollo 12: 300 m vehicle+plume, enhancement factor ~320, breakdown in
7.5 kV/m ambient field.

---

## Thunder

### Generation Mechanisms

| Mechanism             | Frequency                  | Initial Pressure |
| --------------------- | -------------------------- | ---------------- |
| Hot channel expansion | Mainly >20 Hz (audible)    | Overpressure     |
| Electrostatic relief  | Mainly <20 Hz (infrasonic) | Underpressure    |

### Audibility

- Speed of sound: ~340 m/s at 20C
- Flash-to-bang: **~3 s/km**
- Typical range: ~25 km; extremes >100 km; at sea ~8 km

### Thunder Duration

| Location    | Median (s) |
| ----------- | ---------- |
| Socorro, NM | 15         |
| Tucson, AZ  | 18         |
| Roswell, NM | 29         |
| Houston, TX | 41         |

### Sounds

| Sound          | Source                                   | Range   |
| -------------- | ---------------------------------------- | ------- |
| Click          | Upward connecting leader                 | <100 m  |
| Whip-crack     | Return stroke in nearest segment         | <100 m  |
| Tearing cloth  | Single straight segment                  | ~100s m |
| Clap (0.2-2 s) | Simultaneous arrival from perp. segments | Typical |
| Rumble         | Moderate-weak, long duration             | Distant |

### Frequency Spectrum

- Ground flashes: mean peak **50 Hz**; range <4-125 Hz
- Cloud flashes: mean peak **28 Hz**
- Triggered at 70 m: dominant **300-900 Hz** per stroke

### Energy

- Ground flashes: mean **6.3x10^6 J**
- Cloud flashes: **1.9x10^6 J** (3x less)
- Acoustic efficiency: **0.18%** (if 1.8x10^9 J total); 2-20% (if 10^3-10^4 J/m)

### Hot Channel Expansion

1. Return stroke heats from ~10,000 K to ~30,000 K in <few us
2. Pressure reaches **~10 atm** in first 5 us
3. Shock wave: initially supersonic at **~10x speed of sound**
4. 99% of shock energy expended within **few meters**
5. Transitions to acoustic wave at 2-5 relaxation radii (R_0)

### Few's Thunder Theory

Relaxation radius: R\_0 = sqrt(W / (pi\*P\_0))
Peak frequency: f\_m = 0.63 \* C\_0 \* sqrt(P\_0/W)

| Input Energy W (J/m) | R\_0 (cm) | f\_m (Hz) |
| -------------------- | --------- | --------- |
| 10^3                 | 5.6       | 2200      |
| 10^4                 | 18        | 683       |
| 10^5                 | 56        | 216       |
| 10^6                 | 180       | 68        |

See `scripts/thunder.py` for implementation.
