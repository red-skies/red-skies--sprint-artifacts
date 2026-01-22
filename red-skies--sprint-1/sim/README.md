# SIM

## Validate positioning (WGS84)

To validate that the mission objects are positioned correctly in WGS84 (lat/lon), render the mission + objects to a PNG.

From the repository root, run:

```bash
python3 red-skies--sprint-artifacts/red-skies--sprint-1/sim/customer_mission_definition/render_wgs84.py \
  --objects red-skies--sprint-artifacts/red-skies--sprint-1/sim/customer_mission_definition/objects.yaml \
  --mission red-skies--sprint-artifacts/red-skies--sprint-1/sim/customer_mission_definition/mission.yaml \
  --out red-skies--sprint-artifacts/red-skies--sprint-1/sim/customer_mission_definition/mission_render.png
```

Expected output:
- `mission_render.png`

What to check:
- The **blue circle** (playground) covers all **red circles** (NFZs)
- The **aircraft** marker is at the top-left of the playground bounding box
- The aircraft **heading arrow** points toward the playground center
