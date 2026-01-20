# HoldingAgentLidarEnv - Clean Architecture

## Overview

This environment implements a holding pattern navigation task with NFZ (No-Fly Zone) avoidance using a **clean separation** between environment logic and simulator communication.

## Architecture

```
envs/
├── HoldingAgentEnv.py          # RL environment (simulator-agnostic)
├── simulators/
│   ├── __init__.py
│   ├── base.py                 # Abstract SimulatorInterface
│   ├── bluesky_sim.py         # BlueSky implementation
│   └── jsbsim_sim.py          # JSBSim implementation (future)
├── example_usage.py            # Usage examples
└── README.md                   # This file
```

## Benefits of This Design

### 1. **Separation of Concerns**
- Environment logic (observations, rewards, lidar) is independent of simulator
- Simulator communication is encapsulated in separate modules
- Easy to understand, test, and maintain

### 2. **Easy Simulator Swapping**
Switch from BlueSky to JSBSim by changing one line:
```python
# Before: BlueSky
simulator = BlueSkySimulator(aircraft_id="HOLD1")

# After: JSBSim
simulator = JSBSimSimulator(aircraft_id="HOLD1")

# Environment code stays identical!
env = HoldingAgentLidarEnv(simulator=simulator, ...)
```

### 3. **Testability**
- Mock the simulator for unit tests
- Test environment logic without running full simulator
- Test simulator integration separately

### 4. **Reusability**
- Other environments can use the same simulator interfaces
- Simulator implementations can be shared across projects

## Key Components

### SimulatorInterface (Abstract Base Class)

Defines the contract all simulators must implement:
- `reset(**kwargs)` - Reset simulator
- `step(dt)` - Advance simulation
- `get_aircraft_position(aircraft_id)` - Get lat/lon
- `get_aircraft_heading(aircraft_id)` - Get heading
- `get_aircraft_speed(aircraft_id)` - Get speed
- `set_heading_change(aircraft_id, heading_change_deg)` - Command heading
- `close()` - Cleanup

### HoldingAgentLidarEnv

**Observation Space:**
- `[0]`: Normalized distance to center [0, 1]
- `[1]`: Normalized relative bearing to center [0, 1]
- `[2:2+num_rays]`: Normalized lidar distances [0, 1]

**Action Space:**
- Continuous [-1, 1] → scaled to heading change in degrees

**Features:**
- Ray-circle intersection for efficient NFZ detection
- Configurable lidar rays and range
- Optional pyproj for accurate geodetic calculations
- Equirectangular fallback for simplicity

## Algorithmic Design

### Overview

The HoldingAgentLidarEnv is a Gymnasium-compliant reinforcement learning environment that trains an aircraft to maintain a holding pattern within a circular zone while avoiding No-Fly Zones (NFZs). The agent receives observations from a simulated LIDAR sensor and controls the aircraft by commanding heading changes.

### Action Space

**Type:** Continuous, Box(1)
**Range:** [-1.0, 1.0]
**Physical Meaning:** Rate of heading change

**Algorithm:**
```
Input: action ∈ [-1, 1]
heading_change_deg = action × turn_rate_deg_s
Command aircraft to change heading by heading_change_deg
```

**Example:** With `turn_rate_deg_s = 30`:
- `action = 1.0` → Turn right at 30°/s
- `action = -1.0` → Turn left at 30°/s
- `action = 0.0` → Maintain current heading

### Observation Space

**Type:** Continuous, Box(2 + num_rays)
**Range:** [0.0, 1.0] for all dimensions (normalized)

**Components:**

1. **Distance to Center** `obs[0]`
   ```
   distance_normalized = min(distance_meters / max_radius_m, 1.0)
   ```
   - 0.0 = at center
   - 1.0 = at or beyond boundary

2. **Relative Bearing to Center** `obs[1]`
   ```
   bearing_to_center = atan2(-x, -y)  # Direction from aircraft to center
   relative_bearing = (bearing_to_center - aircraft_heading + 180) mod 360 - 180
   bearing_normalized = (relative_bearing + 180) / 360
   ```
   - 0.0 = center is 180° behind (flying away)
   - 0.5 = center is directly ahead
   - 1.0 = center is 180° behind (same as 0.0)

3. **LIDAR Distances** `obs[2:2+num_rays]`
   ```
   For each ray i in [0, num_rays):
       lidar_normalized[i] = detected_distance[i] / max_lidar_range
   ```
   - 0.0 = NFZ at aircraft position (collision)
   - 1.0 = No NFZ detected within sensor range
   - Values in between indicate NFZ distance

### LIDAR Sensor Simulation

The LIDAR system casts rays radially around the aircraft to detect NFZs using ray-circle intersection.

**Algorithm:**

```
Function: _get_lidar_data(aircraft_x, aircraft_y, aircraft_heading)

1. Initialize:
   lidar_distances = [max_lidar_range] × num_rays
   ray_angles = linspace(0°, 360°, num_rays, exclusive)

2. For each ray i:
   a. Calculate absolute ray angle:
      ray_angle_abs = (aircraft_heading + ray_angles[i]) mod 360

   b. Compute ray direction (unit vector):
      dx = sin(ray_angle_abs)  # East component
      dy = cos(ray_angle_abs)  # North component

   c. For each NFZ (center_x, center_y, radius):
      i.   Compute vector from NFZ center to aircraft:
           ox = aircraft_x - center_x
           oy = aircraft_y - center_y

      ii.  Solve ray-circle intersection (parametric form):
           Ray: P(t) = (aircraft_x, aircraft_y) + t(dx, dy)
           Circle: (x - center_x)² + (y - center_y)² = radius²

           Quadratic: at² + bt + c = 0, where:
           a = dx² + dy² = 1 (unit vector)
           b = 2(ox·dx + oy·dy)
           c = ox² + oy² - radius²

      iii. Check discriminant:
           Δ = b² - 4c

           If Δ < 0: No intersection, continue

           If Δ ≥ 0: Two solutions:
               t₁ = (-b - √Δ) / 2  # Entry point
               t₂ = (-b + √Δ) / 2  # Exit point

               If t₁ > 0:
                   distance = t₁  # In front of aircraft
               Elif t₂ > 0:
                   distance = 0   # Aircraft inside NFZ
               Else:
                   continue       # NFZ behind aircraft

      iv. Update closest hit for this ray:
          lidar_distances[i] = min(lidar_distances[i], distance)

3. Return lidar_distances
```

**Key Insights:**
- Rays are evenly distributed 360° around the aircraft
- Ray angles are **relative to aircraft heading** (body frame)
- Multiple NFZs can be detected; closest hit per ray is kept
- Ray direction uses aviation convention: 0° = North, 90° = East

**Example with 8 rays:**
```
Ray 0:   0° (straight ahead)
Ray 1:  45° (ahead-right)
Ray 2:  90° (right)
Ray 3: 135° (behind-right)
Ray 4: 180° (behind)
Ray 5: 225° (behind-left)
Ray 6: 270° (left)
Ray 7: 315° (ahead-left)
```

### Coordinate System Transformations

**Lat/Lon → Local XY:**

**Option 1: Pyproj (Accurate)**
```
proj = Proj(proj='aeqd', lat_0=center_lat, lon_0=center_lon)
x, y = proj(lon, lat)
```
- Azimuthal Equidistant projection
- Preserves distances from center
- Accurate for any radius globally

**Option 2: Equirectangular (Fast Approximation)**
```
y = (lat - center_lat) × 111319.9  # meters per degree latitude
x = (lon - center_lon) × 111319.9 × cos(center_lat)  # meters per degree longitude
```
- <1% error up to ~100km at latitudes below 60°
- Fast, no external dependencies

### Reward Function

**Algorithm:**
```
Function: _calculate_reward(observation)

1. Extract components:
   dist_normalized = obs[0]
   lidar_distances = obs[2:]

2. Base reward:
   reward = 0.1  # Small positive reward for survival

3. Constraint 1: Boundary violation
   If dist_normalized > 1.0:
       Return reward = -100, terminated = False
       (Episode continues but penalized)

4. Constraint 2: NFZ collision
   min_lidar_distance = min(lidar_distances)
   If min_lidar_distance == 0:
       Return reward = -10, terminated = False
       (Episode continues but penalized)

5. Proximity penalty (soft constraint):
   If min_lidar_distance < 0.1:
       penalty = (0.1 - min_lidar_distance) × 10
       reward -= penalty
       (Exponentially increasing penalty as NFZ gets closer)

6. Return reward, terminated
```

**Design Rationale:**
- **Survival reward (0.1)**: Encourages longer episodes
- **Boundary penalty (-100)**: Strong discouragement from leaving zone
- **Collision penalty (-10)**: Moderate penalty for NFZ violation
- **Proximity penalty**: Smooth gradient to help agent learn avoidance
- **Non-terminating violations**: Agent can recover from mistakes (more realistic)

### Episode Reset and Randomization

**Algorithm:**
```
Function: reset(seed, options)

1. Set random seed (for reproducibility):
   super().reset(seed=seed)

2. Initialize NFZs:
   If options contains 'nfzs':
       Use provided NFZs
   Else:
       Use default test NFZ: [(52.07, -34.0, 130)]

3. Randomize aircraft initial position:
   If options contains 'aircraft_initial_lat', 'aircraft_initial_lon', 'aircraft_initial_hdg':
       Use provided initial state
   Else:
       a. Sample random position within zone:
          r = max_radius × √U(0,1)  # Uniform area distribution
          θ = U(0, 360)              # Uniform angle

       b. Convert to lat/lon:
          lon, lat, heading = randomize_position_in_zone(
              center_lat, center_lon, max_radius
          )
          (Uses geodesic calculations via pyproj.Geod)

4. Reset simulator:
   simulator.reset(
       aircraft_type=aircraft_type,
       aircraft_initial_lat=lat,
       aircraft_initial_lon=lon,
       aircraft_initial_hdg=heading,
       aircraft_alt=altitude,
       speed=speed
   )

5. Get initial observation:
   obs = _get_obs()

6. Return obs, info
```

**Key Feature:** Using `√U(0,1)` for radius ensures uniform distribution across the area, not biased toward the center.

### Step Execution Flow

**Algorithm:**
```
Function: step(action)

1. Scale action to physical command:
   heading_change = action[0] × turn_rate_deg_s

2. Send command to simulator:
   simulator.set_heading_change(aircraft_id, heading_change)

3. Advance simulation:
   simulator.step()  # Steps forward by dt seconds

4. Gather new state from simulator:
   lat, lon, alt = simulator.get_aircraft_position(aircraft_id)
   heading = simulator.get_aircraft_heading(aircraft_id)

5. Convert to local coordinates:
   x, y = latlon_to_xy(lat, lon)

6. Compute observation components:
   a. Distance to center:
      dist_to_center = √(x² + y²)
      obs[0] = min(dist_to_center / max_radius, 1.0)

   b. Relative bearing to center:
      brg_to_center = atan2(-x, -y)
      rel_brg = (brg_to_center - heading + 180) mod 360 - 180
      obs[1] = (rel_brg + 180) / 360

   c. LIDAR readings:
      lidar_raw = _get_lidar_data(x, y, heading)
      obs[2:] = lidar_raw / max_lidar_range

7. Calculate reward and check termination:
   reward, terminated = _calculate_reward(obs)

8. Check truncation (handled by TimeLimit wrapper):
   truncated = (step_count >= max_episode_steps)

9. Build info dict:
   info = {
       'heading_change': heading_change,
       'distance_to_center_m': obs[0] × max_radius,
       'min_lidar_distance_m': min(obs[2:]) × max_lidar_range,
       'terminated': terminated,
       'truncated': truncated
   }

10. Return obs, reward, terminated, truncated, info
```

### Episode Length Control

Episodes are limited using Gymnasium's `TimeLimit` wrapper:
```python
env = HoldingAgentLidarEnv(...)
env = TimeLimit(env, max_episode_steps=1000)
```

This automatically sets `truncated=True` when the step limit is reached, triggering a reset.

## Usage

```python
from envs.HoldingAgentEnv import HoldingAgentLidarEnv
from envs.simulators import BlueSkySimulator

# 1. Create simulator
simulator = BlueSkySimulator(aircraft_id="HOLD1")

# 2. Create environment
env = HoldingAgentLidarEnv(
    simulator=simulator,
    center_lat=52.0,
    center_lon=4.0,
    aircraft_id="HOLD1",
    max_radius_m=10000,
    num_rays=24,
    use_pyproj=True,
    max_lidar_range=5000,
    turn_rate_deg_s=15,
    dt=1.0
)

# 3. Define NFZs in local XY coordinates (x, y, radius) in meters
nfzs = [
    (2000, 3000, 1000),   # 2km east, 3km north, 1km radius
    (-1500, -2000, 800),  # 1.5km west, 2km south, 800m radius
]

# 4. Reset and run
obs, info = env.reset(options={'nfzs': nfzs})

for _ in range(100):
    action = policy(obs)  # Your trained policy
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

env.close()
```

## Next Steps

### To use with BlueSky:
1. Implement the methods in `envs/simulators/bluesky_sim.py`
2. Connect to BlueSky server
3. Implement aircraft state queries and commands

### To add JSBSim:
1. Create `envs/simulators/jsbsim_sim.py`
2. Implement the `SimulatorInterface` methods
3. Use it with the same environment code!

## Coordinate Systems

### Lat/Lon → XY Conversion
- **With pyproj**: Azimuthal Equidistant projection (exact, works globally)
- **Without pyproj**: Equirectangular approximation (<1% error up to ~100km at lat < 60°)

### NFZ Coordinates
NFZs are specified in **local XY coordinates** (meters) relative to the center point:
- `x`: East-West (positive = East)
- `y`: North-South (positive = North)
- `radius`: Circle radius in meters

## Dependencies

**Required:**
- `gymnasium`
- `numpy`

**Optional:**
- `pyproj` - For accurate geodetic calculations (recommended for radius > 50km)
