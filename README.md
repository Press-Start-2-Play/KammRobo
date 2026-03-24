# KammRobo 🤖

A real-physics-based robot path-following simulation built with Python and Pygame. KammRobo uses a PID controller, the **Friction Circle (Kamm Circle)** model, and radius-of-curvature-based pre-emptive braking to navigate complex parametric paths.

---

## 🚀 What it does

KammRobo simulates a robot (yellow/green dot) attempting to track a target point (grey dot) along various mathematical paths. The simulation is grounded in vehicle dynamics concepts:

* **Modular Path Selection:** Choose between Hypotrochoids, Figure-Eights, Epitrochoids, and Lissajous curves via the interactive UI.
* **PID Control:** A Proportional-Integral-Derivative controller manages steering forces based on the robot's error from the target.
* **Kamm Circle Physics:** The robot has a limited "grip budget" ($\mu mg$). It must balance lateral cornering forces with longitudinal acceleration/braking.
* **Centripetal Logic:** The simulation analytically calculates the instantaneous radius of curvature ($R$) to determine the maximum safe cornering speed.
* **Drift State:** If speed exceeds the theoretical grip limit ($v > \sqrt{\mu g R}$), the robot enters a "Drift" state (yellow), losing grip until it can stabilize back onto the path.

---

## 📂 Project Structure

The project is modularized for better scalability and readability:

* **`main.py`**: The entry point. Handles the Pygame loop, event polling, and high-level orchestration.
* **`robot.py`**: Contains the `Robot` class. Encapsulates physics state, PID calculations, and friction circle logic.
* **`path_generators.py`**: Pure mathematical functions for all parametric paths and curvature logic.
* **`ui_elements.py`**: Handles the "Cyber" UI buttons, glass-effect panels, and telemetry rendering.
* **`config.py`**: Central hub for constants, colors, and physics scaling.

---

## 🛠️ Requirements & Setup

* Python 3.8+
* Pygame

1.  **Install dependencies:**
    ```bash
    pip install pygame
    ```

2.  **Run the simulation:**
    ```bash
    python main.py
    ```

---

## ⚙️ Tuning the Physics

Key constants are located in `config.py` and the `Robot` class initialization:

| Variable | Location | Effect |
| :--- | :--- | :--- |
| `PIXELS_PER_METER` | `config.py` | Scale factor (default 100). Higher = smaller world scale. |
| `co_of_friction` | `robot.py` | Grip level ($\mu$). 0.3 = Ice, 0.7 = Dry Asphalt, 1.2 = Slicks. |
| `kp / ki / kd` | `robot.py` | PID Gains. Dynamically scaled by the robot's mass for stability. |

---

## 🧠 Physics Deep Dive

### The Friction Circle
The robot's total available force is limited by the friction between the tires and the surface:
$$F_{max} = m \cdot g \cdot \mu$$

The simulation prioritizes lateral force ($F_{lat}$) to maintain the curve. Any remaining "budget" is used for longitudinal acceleration or braking ($F_{long}$):
$$F_{long\_budget} = \sqrt{F_{max}^2 - F_{lat}^2}$$

### Radius of Curvature
For any path defined by $x(t), y(t)$, the instantaneous radius $R$ is calculated as:
$$R = \frac{(x'^2 + y'^2)^{1.5}}{|x'y'' - y'x''|}$$

---

## 🤝 Contributing
KammRobo is definitely not yet a finished project and is open to contributions. I'm excited to finally make something that reflects my interest in Robotics! 

**Key areas for contribution:**
* Adding more complex path types (Splines or CSV-based race tracks).
* Implementing a "Ghost" robot with a different PID tune for performance comparison.
* Adding multi-robot collision physics.

**Let's Goooo!!** 🏎️💨

## License
MIT