import argparse
import math
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


def _deg_per_meter_lat() -> float:
    return 1.0 / 111_000.0


def _deg_per_meter_lon(lat_deg: float) -> float:
    return 1.0 / (111_000.0 * max(1e-6, abs(math.cos(math.radians(lat_deg)))))


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def _extract_objects(objects_yaml: Dict[str, Any]) -> List[Dict[str, Any]]:
    objs = objects_yaml.get("objects")
    if not isinstance(objs, list):
        raise ValueError("objects.yaml missing top-level 'objects' list")
    out: List[Dict[str, Any]] = []
    for o in objs:
        if isinstance(o, dict):
            out.append(o)
    return out


def _circle_from_object(o: Dict[str, Any]) -> Tuple[str, float, float, float]:
    oid = str(o.get("id", ""))
    geos = o.get("geolocation")
    if not (isinstance(geos, list) and geos and isinstance(geos[0], dict)):
        raise ValueError(f"object {oid}: invalid geolocation")
    lat = float(geos[0]["lat"])
    lon = float(geos[0]["lon"])
    radius = o.get("radius")
    if not (isinstance(radius, list) and radius and isinstance(radius[0], (int, float))):
        raise ValueError(f"object {oid}: invalid radius")
    r_m = float(radius[0])
    return oid, lat, lon, r_m


def _svg_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_html(
    playground: Tuple[str, float, float, float],
    nfzs: List[Tuple[str, float, float, float]],
    aircraft: Tuple[float, float, float],
    out_html: Path,
    size_px: int = 1200,
) -> None:
    pg_id, pg_lat, pg_lon, pg_r_m = playground
    ac_lat, ac_lon, ac_heading = aircraft

    deg_lat = _deg_per_meter_lat()
    deg_lon = _deg_per_meter_lon(pg_lat)

    min_lat = pg_lat - pg_r_m * deg_lat
    max_lat = pg_lat + pg_r_m * deg_lat
    min_lon = pg_lon - pg_r_m * deg_lon
    max_lon = pg_lon + pg_r_m * deg_lon

    for _, lat, lon, r_m in nfzs:
        dlat = r_m * deg_lat
        dlon = r_m * _deg_per_meter_lon(lat)
        min_lat = min(min_lat, lat - dlat)
        max_lat = max(max_lat, lat + dlat)
        min_lon = min(min_lon, lon - dlon)
        max_lon = max(max_lon, lon + dlon)

    pad = 0.05
    lat_span = max(1e-9, max_lat - min_lat)
    lon_span = max(1e-9, max_lon - min_lon)
    min_lat -= lat_span * pad
    max_lat += lat_span * pad
    min_lon -= lon_span * pad
    max_lon += lon_span * pad

    def xy(lat: float, lon: float) -> Tuple[float, float]:
        x = (lon - min_lon) / (max_lon - min_lon) * size_px
        y = (max_lat - lat) / (max_lat - min_lat) * size_px
        return x, y

    def circle_px(lat: float, lon: float, r_m: float) -> Tuple[float, float, float, float]:
        cx, cy = xy(lat, lon)
        rx = r_m * _deg_per_meter_lon(lat) / (max_lon - min_lon) * size_px
        ry = r_m * deg_lat / (max_lat - min_lat) * size_px
        return cx, cy, rx, ry

    pg_cx, pg_cy, pg_rx, pg_ry = circle_px(pg_lat, pg_lon, pg_r_m)

    ac_x, ac_y = xy(ac_lat, ac_lon)
    heading_rad = math.radians(ac_heading)
    arrow_len = size_px * 0.08
    ax2 = ac_x + arrow_len * math.sin(heading_rad)
    ay2 = ac_y - arrow_len * math.cos(heading_rad)

    elements: List[str] = []

    elements.append(
        f'<ellipse cx="{pg_cx:.2f}" cy="{pg_cy:.2f}" rx="{pg_rx:.2f}" ry="{pg_ry:.2f}" '
        'fill="rgba(59,130,246,0.08)" stroke="rgba(59,130,246,0.9)" stroke-width="2" />'
    )
    elements.append(
        f'<text x="{pg_cx + 8:.2f}" y="{pg_cy - 8:.2f}" font-size="14" fill="#1f2937">'
        f'{_svg_escape(pg_id)}</text>'
    )

    for nfz_id, lat, lon, r_m in nfzs:
        cx, cy, rx, ry = circle_px(lat, lon, r_m)
        elements.append(
            f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
            'fill="rgba(239,68,68,0.10)" stroke="rgba(239,68,68,0.95)" stroke-width="2" />'
        )
        elements.append(
            f'<text x="{cx + 6:.2f}" y="{cy - 6:.2f}" font-size="12" fill="#7f1d1d">'
            f'{_svg_escape(nfz_id)}</text>'
        )

    elements.append(f'<circle cx="{ac_x:.2f}" cy="{ac_y:.2f}" r="5" fill="#111827" />')
    elements.append(
        f'<line x1="{ac_x:.2f}" y1="{ac_y:.2f}" x2="{ax2:.2f}" y2="{ay2:.2f}" '
        'stroke="#111827" stroke-width="2" />'
    )

    center_bearing = _bearing_deg(ac_lat, ac_lon, pg_lat, pg_lon)

    header = (
        "<div style='font-family: ui-sans-serif, system-ui; padding: 10px; color: #111827'>"
        f"<div><b>WGS84 bounds</b>: lat [{min_lat:.6f}, {max_lat:.6f}] lon [{min_lon:.6f}, {max_lon:.6f}]</div>"
        f"<div><b>Playground</b>: center ({pg_lat:.6f}, {pg_lon:.6f}) radius_m {pg_r_m:.2f}</div>"
        f"<div><b>Aircraft</b>: ({ac_lat:.6f}, {ac_lon:.6f}) heading {ac_heading:.2f} bearing_to_center {center_bearing:.2f}</div>"
        "</div>"
    )

    html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Mission Render (WGS84)</title>
  <style>
    body {{ margin: 0; background: #ffffff; }}
    .wrap {{ width: {size_px}px; margin: 0 auto; }}
    svg {{ width: {size_px}px; height: {size_px}px; background: #f8fafc; border: 1px solid #e5e7eb; }}
  </style>
</head>
<body>
  <div class=\"wrap\">{header}
    <svg viewBox=\"0 0 {size_px} {size_px}\" xmlns=\"http://www.w3.org/2000/svg\" shape-rendering=\"geometricPrecision\">
      <defs>
        <pattern id=\"grid\" width=\"50\" height=\"50\" patternUnits=\"userSpaceOnUse\">
          <path d=\"M 50 0 L 0 0 0 50\" fill=\"none\" stroke=\"#e5e7eb\" stroke-width=\"1\" />
        </pattern>
      </defs>
      <rect width=\"100%\" height=\"100%\" fill=\"url(#grid)\" />
      {''.join(elements)}
    </svg>
  </div>
</body>
</html>
"""

    out_html.write_text(html, encoding="utf-8")


def _chrome_screenshot(html_path: Path, out_png: Path, size_px: int) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={size_px},{size_px + 140}",
        f"--screenshot={str(out_png)}",
        str(html_path.as_uri()),
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"chrome screenshot failed: {proc.stderr.strip()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--objects", default="objects.yaml")
    ap.add_argument("--mission", default="mission.yaml")
    ap.add_argument("--out", default="mission_render.png")
    ap.add_argument("--size", type=int, default=1200)
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    objects_path = Path(args.objects)
    mission_path = Path(args.mission)
    if not objects_path.is_absolute():
        objects_path = here / objects_path
    if not mission_path.is_absolute():
        mission_path = here / mission_path

    objects_yaml = _load_yaml(objects_path)
    mission_yaml = _load_yaml(mission_path)

    objs = _extract_objects(objects_yaml)

    playground_obj = next((o for o in objs if o.get("id") == "playground"), None)
    if not isinstance(playground_obj, dict):
        raise ValueError("objects.yaml: missing object with id=playground")

    playground = _circle_from_object(playground_obj)

    nfzs: List[Tuple[str, float, float, float]] = []
    for o in objs:
        if not isinstance(o, dict):
            continue
        if o.get("behavior") != "no_fly_zone":
            continue
        if o.get("type") != "circle":
            continue
        nfzs.append(_circle_from_object(o))

    mission = mission_yaml.get("mission")
    if not isinstance(mission, dict):
        raise ValueError("mission.yaml: missing top-level 'mission'")
    platforms = mission.get("platforms")
    if not (isinstance(platforms, list) and platforms and isinstance(platforms[0], dict)):
        raise ValueError("mission.yaml: mission.platforms must be a list")

    aircraft_platform = platforms[0]
    init_state = aircraft_platform.get("initial_state")
    if not isinstance(init_state, dict):
        raise ValueError("mission.yaml: platforms[0].initial_state must be a mapping")

    pos = init_state.get("position")
    if not isinstance(pos, dict):
        raise ValueError("mission.yaml: initial_state.position must be a mapping")

    ac_lat = float(pos["lat"])
    ac_lon = float(pos["lon"])
    ac_heading = float(init_state.get("heading", 0.0))

    out_png = Path(args.out)
    if not out_png.is_absolute():
        out_png = here / out_png

    out_html = out_png.with_suffix(".html")

    _render_html(playground=playground, nfzs=nfzs, aircraft=(ac_lat, ac_lon, ac_heading), out_html=out_html, size_px=args.size)
    _chrome_screenshot(out_html, out_png, args.size)

    print(str(out_png))


if __name__ == "__main__":
    main()
