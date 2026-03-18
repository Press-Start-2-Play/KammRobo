# KammRobo 🤖

A real-physics-based robot path-following simulation built with Python and Pygame. MuBot uses a PID controller, the Friction Circle (Kamm Circle) model, and radius-of-curvature-based pre-emptive braking to follow a Lissajous curve as realistically as possible.

---

## What it does

It simulates a robot trying to stay on a moving target point along a parametric path. The physics are grounded in real vehicle dynamics concepts:

- **PID steering** — proportional, integral, and derivative gain control drives the robot toward the target dot
- **Friction Circle** — lateral and longitudinal forces share a single grip budget (μmg), modeled after the Kamm Circle
- **Centripetal force** — the simulation computes the instantaneous radius of curvature and checks whether speed exceeds the grip limit
- **Pre-emptive braking** — when the path is sharpening (dR/dt < 0), the robot brakes ahead of the corner
- **Drift detection** — if the robot exceeds the theoretical grip limit it snaps back to the nearest point on the path

The robot turns **yellow** when drifting, **green** when stable.

---

## Demo

The path is a modified Lissajous curve:

```
x(t) = cx + 250·cos(1.2t)
y(t) = cy + 180·sin(1.1t)
```

The red dot is the target. KammRobo chases after it in real time.

---

## Requirements

- Python 3.8+
- Pygame

Install dependencies:

```bash
pip install pygame
```

---

## Run it

```bash
python robot_sim.py
```

Close the window to exit.

---

## Tuning

All key constants are at the top of `robot_sim.py`:

| Constant | Default | Effect |
|---|---|---|
| `PIXELS_PER_METER` | `100` | Scale factor — higher = more grip force |
| `co_of_friction` | `0.7` | Grip level (μ). Try 0.3 for ice, 1.2 for race slicks |
| `kp` | `8.0` | How aggressively the robot steers toward the target |
| `ki` | `0.5` | Corrects accumulated drift over time |
| `kd` | `1.5` | Dampens oscillation |

---

## Physics notes

Forces are computed in **pixel-space** (pixels per second²), scaled from SI units using `PIXELS_PER_METER = 100`. This means:

- `g = 9.80665 m/s²` → `980.665 px/s²`
- `max_frictional_force = m · g_px · μ` ≈ `686 px-force`
- Radius of curvature `R` is derived analytically from the path derivatives

The centripetal force check is: `F_lat = mv²/R`, where `v` is in px/s and `R` is in px.

---

## License

MIT
