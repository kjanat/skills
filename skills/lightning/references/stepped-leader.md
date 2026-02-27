# Stepped Leader Physics

## Speed

| Source                      | Speed (m/s)                           |
| --------------------------- | ------------------------------------- |
| Schonland (1956)            | 0.8-8x10^5                            |
| Berger & Vogelsanger (1966) | 0.9-4.4x10^5                          |
| Thomson et al. (1985)       | 1.3-19x10^5 (mean 5.7x10^5)           |
| Proctor et al. (1988)       | 3x10^4-4.2x10^5 (median 1.3x10^5)     |
| Beasley et al. (1983)       | 0.8-3.9x10^6 (within 100 m of ground) |

**Typical average: 2x10^5 m/s.**

## Duration

GM stepped-leader duration: **35 ms** (Rakov & Uman 1990c).
Implies ~7 km channel at 2x10^5 m/s. Range: 9-46 ms.

## Electrical Parameters

| Parameter                        | Value                        |
| -------------------------------- | ---------------------------- |
| Impulse charge (median, Berger)  | 4.5 C (95%: 1.1 C; 5%: 20 C) |
| Total charge (GM, Brook et al.)  | 6 C                          |
| Channel length (Proctor, median) | 6 km (range 3-13 km)         |
| Line charge density (avg)        | 0.7-1 mC/m                   |
| Line charge density near ground  | GM 3.4 mC/m (range 0.7-32)   |
| Average current                  | 50-63 A                      |
| Current near ground              | 100 A-5 kA, mean 1.3 kA      |
| Electric potential               | ~50 MV                       |

## Step Properties

| Parameter             | Value                         |
| --------------------- | ----------------------------- |
| Step length           | 3-200 m (typically 50 m)      |
| Interstep interval    | 5-100 us (typically 20-50 us) |
| Step duration         | ~1 us                         |
| Peak current per step | >=2-8 kA                      |
| Max dI/dt per step    | 6-24 kA/us                    |
| Charge per step       | 1-4 mC                        |
| Step temperature      | ~30,000 K                     |
| Between steps         | >=15,000 K                    |
| Core diameter         | probably <1 cm                |
| Corona sheath radius  | Several meters                |

## Streamer Zone

Estimated length: **100-200 m** ahead of tip at 50-100 MV potential.

## Step-Formation Mechanism

Based on long-spark analogy (Gorin et al. 1976):

1. **Space stem** forms ahead of leader tip in undisturbed air
2. Develops into **bidirectional space channel** (positive toward leader,
   negative forward)
3. Positive end contacts leader → **step** forms
4. Burst of negative streamers at new tip → current pulse → channel
   briefly illuminated
5. Extension speed during step: ~10^7 m/s (50x avg leader speed)

## Electric Field of Uniformly-Charged Leader

For leader extending downward from charge source at height H_m with uniform
line charge density rho_L and tip at height z_t:

```r
E_z(r,t) = rho_L/(2*pi*eps_0*r) * [
    1/sqrt(1 + z_t^2/r^2)
  - 1/sqrt(1 + H_m^2/r^2)
  - (H_m - z_t)*H_m / (r^2*(1 + H_m^2/r^2)^(3/2))
]
```

Where z_t = H_m - v*t (leader tip height), r = horizontal distance.
See `scripts/leader_fields.py` for implementation.

Close approximation (H_m >> 2r, z_t near 0):
E_z ≈ rho_L / (2*pi*eps_0*r)

## Attachment Process

### Upward Connecting Leaders

| Stroke Type                | Length        | Speed (m/s)  |
| -------------------------- | ------------- | ------------ |
| First (flat ground)        | ~20-30 m      | 0.8-2.7x10^5 |
| First (80 m tower, winter) | 25-150+ m     | 0.8-2.7x10^5 |
| Subsequent                 | ~10 m or less | ~2x10^7      |

Bidirectional return stroke from junction point (Wang et al. 1999a: junction
7-11 m height).

## Initial Breakdown

Precedes stepped leader in cloud. Duration 2-10 ms (up to 50-100 ms).

- Pulse duration: 20-40 us; interval: 70-130 us
- Distinct from stepped-leader pulses near ground (1-2 us, 15-25 us interval)

### Lightning Initiation Gap

Max measured cloud fields (~2x10^5 V/m) are ~10x below conventional breakdown
(~10^6 V/m). Possible mechanisms:

- Runaway breakdown (breakeven ~10^5 V/m at 10 km for 200 keV electrons)
- Corona onset at hydrometeor surfaces
- Enhanced local fields from precipitation
