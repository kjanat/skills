# Dart Leader, Continuing Current & M-Components

## Dart Leader

Traverses residual channel of preceding stroke.

| Parameter                         | Value                            |
| --------------------------------- | -------------------------------- |
| Speed                             | (0.3-2.4)x10^7 m/s, typical 10^7 |
| Duration                          | 1-2 ms                           |
| Line charge density               | ~1 mC/m                          |
| Average current                   | 1-2 kA                           |
| Step length (dart-stepped)        | ~10 m                            |
| Interstep interval (dart-stepped) | ~6-8 us                          |
| Channel conditioning lifetime     | ~100 ms                          |

Speed increases approaching ground. Luminous diameter: ~1 m.

**Dart-stepped leader**: hybrid; occurs when preceding interstroke interval
is long or channel partially decayed. Speed: 0.5-1.7x10^6 m/s (slower than
pure dart). Step length ~10 m vs ~50 m for stepped leader.

## Continuing Current (CC)

Quasi-stationary arc following return stroke.

| Parameter           | Value                             |
| ------------------- | --------------------------------- |
| Magnitude           | tens-hundreds of A                |
| Duration            | tens-hundreds of ms; up to 500 ms |
| Charge transferred  | typically 10+ C; up to >200 C     |
| Channel temperature | ~4000 K (lower bound for arc)     |
| Incidence           | ~30-50% of CG flashes             |
| Positive flashes    | Nearly all have CC                |

Longer CC duration correlates with higher damage potential (burn-through,
fire ignition). Positive lightning CC can reach kA-level (up to tens of kA
in winter storms).

## M-Components

Current/luminosity surges superimposed on continuing current.

| Parameter          | Value               |
| ------------------ | ------------------- |
| Peak current       | tens-hundreds of A  |
| Charge per M-event | 0.1-0.5 C (typical) |
| Duration           | ~0.5 ms             |
| Risetime (10-90%)  | ~500 us             |
| Wave speed         | (2.5-3.0)x10^7 m/s  |
| Typical interval   | 2-100 ms            |

### Two-Wave Model (Rakov et al. 1995)

Before ground contact (t < H/v):
I(z',t) = I(H, t - (H-z')/v)

After ground contact (t >= H/v):
I(z',t) = I(H, t-(H-z')/v) + I(H, t-(H+z')/v)

- v = M-wave propagation speed
- I(H,t) = current injected at channel top = 1/2 of ground-level current
- Ground reflection coefficient = 1
- See `scripts/m_component.py`

Key distinction from leader-return-stroke: M-component requires existing
conducting channel; luminosity enhancement travels both up AND down from
junction point.

## J- and K-Processes

Interstroke processes connecting different parts of flash.

### J-Process

- Slow (~10^4 m/s) charge redistribution between strokes
- Duration: tens of ms
- Manifests as slow E-field change between return strokes
- Probably involves positive leader extension in cloud

### K-Process

- Rapid (~10^5-10^6 m/s) transient within cloud channel
- Duration: ~1 ms; interval: ~10 ms
- Interpreted as "recoil streamers" or "attempted dart leaders"
- Charge per event: ~1.4 C; average current ~1.4 kA
- Often occur during J-process

## Regular Pulse Bursts (RPBs)

| Parameter           | Value                            |
| ------------------- | -------------------------------- |
| Pulses per burst    | 18-24                            |
| Interpulse interval | 5-7.2 us                         |
| Burst duration      | 117-161 us                       |
| Propagation speed   | 1.2-5.6x10^6 m/s (mean 2.7x10^6) |
| Step length         | 7-30 m (mean 14 m)               |

Similar to dart-stepped leaders near ground. Occur during late (final) stage
of cloud discharges.

## Interstroke Interval

| Parameter      | Value                  |
| -------------- | ---------------------- |
| Geometric mean | ~60 ms                 |
| Range          | 7-500 ms               |
| Without CC     | shorter intervals      |
| Following CC   | longer (channel cools) |

Shorter intervals → more likely dart leader (channel hot).
Longer intervals → more likely dart-stepped (channel partially decayed).
Very long → new stepped leader to different ground point.
