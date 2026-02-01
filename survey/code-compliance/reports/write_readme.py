#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


def _load_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _fmt_path(p: str) -> str:
    return p.replace("\\", "/")


def _md_table_cell(value: Any, max_len: int = 80) -> str:
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    s = " ".join(s.split())
    s = s.replace("|", "\\|")
    s = s.replace("`", "\\`")

    if len(s) > max_len:
        s = s[: max_len - 1] + "…"
    return s


def _report_summary(report: Optional[Dict[str, Any]]) -> Dict[str, int]:
    summary = (report or {}).get("summary")
    if not isinstance(summary, dict):
        return {"ok": 0, "flag": 0, "unknown": 0, "not_enriched": 0}

    out: Dict[str, int] = {"ok": 0, "flag": 0, "unknown": 0, "not_enriched": 0}
    for k in out.keys():
        v = summary.get(k)
        if isinstance(v, int):
            out[k] = v
    return out


def _iter_report_files(reports_dir: str) -> List[str]:
    if not os.path.isdir(reports_dir):
        return []
    files = []
    for entry in sorted(os.listdir(reports_dir)):
        if not entry.endswith(".report.json"):
            continue
        if entry == "sbom-enrichment.batch.report.json":
            continue
        files.append(os.path.join(reports_dir, entry))
    return files


def _derive_dimensions(report: Dict[str, Any]) -> Dict[str, Any]:
    components = report.get("components")
    if not isinstance(components, list):
        components = []

    total = 0
    enriched_true = 0
    licenses_missing = 0
    author_name_present = 0
    author_email_present = 0
    origin_country_present = 0
    ecosystems: Dict[str, int] = {}

    license_non_mit_count = 0
    hostile_origin_count = 0
    hostile_countries = {"Russia", "China", "Iran"}

    for c in components:
        if not isinstance(c, dict):
            continue
        total += 1

        if c.get("enriched") is True:
            enriched_true += 1

        if not c.get("license"):
            licenses_missing += 1

        if c.get("author_name"):
            author_name_present += 1
        if c.get("author_email"):
            author_email_present += 1
        if c.get("origin_country"):
            origin_country_present += 1

        lic = c.get("license")
        if lic and str(lic).strip() and str(lic).strip() != "MIT":
            license_non_mit_count += 1

        if c.get("origin_country") in hostile_countries:
            hostile_origin_count += 1

        eco = c.get("ecosystem") or "unknown"
        ecosystems[str(eco)] = ecosystems.get(str(eco), 0) + 1

    return {
        "components_total": total,
        "components_enriched": enriched_true,
        "licenses_missing": licenses_missing,
        "author_name_present": author_name_present,
        "author_email_present": author_email_present,
        "origin_country_present": origin_country_present,
        "license_non_mit_count": license_non_mit_count,
        "license_non_mit_flag": license_non_mit_count > 0,
        "hostile_origin_count": hostile_origin_count,
        "hostile_origin_flag": hostile_origin_count > 0,
        "ecosystems": ecosystems,
    }


def _is_non_mit_license(license_value: Optional[str]) -> bool:
    if not license_value:
        return False
    v = str(license_value).strip()
    if not v:
        return False
    return v != "MIT"


def _is_hostile_origin(origin_country: Optional[str]) -> bool:
    return origin_country in {"Russia", "China", "Iran"}


def _generate_component_rows(reports_dir: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for rep_path in _iter_report_files(reports_dir):
        rep = _load_json(rep_path)
        if rep is None:
            continue

        sbom_name = os.path.basename(rep_path)[: -len(".report.json")]
        components = rep.get("components")
        if not isinstance(components, list):
            components = []

        for c in components:
            if not isinstance(c, dict):
                continue
            license_value = c.get("license")
            origin_country = c.get("origin_country")

            rows.append(
                {
                    "sbom": sbom_name,
                    "component": c.get("name"),
                    "version": c.get("version"),
                    "ecosystem": c.get("ecosystem"),
                    "license": license_value,
                    "policy": c.get("policy"),
                    "author_name": c.get("author_name"),
                    "author_email": c.get("author_email"),
                    "origin_country": origin_country,
                    "license_non_mit": _is_non_mit_license(license_value),
                    "hostile_origin": _is_hostile_origin(origin_country),
                    "enriched": c.get("enriched") is True,
                }
            )

    return rows


def _render_markdown(component_rows: List[Dict[str, Any]], out_dir: str, reports_dir: str) -> str:
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    lines: List[str] = []
    lines.append("# SBOM Enrichment Reports\n")
    lines.append(f"Generated: `{now}`\n")

    lines.append("## How to reproduce\n")
    lines.append(
        "From `survey/code-compliance/`:\n\n"
        "```bash\n"
        "python3 enrich_sbom.py --in . --out ./out --report ./reports\n"
        "python3 reports/write_readme.py\n"
        "```\n"
    )

    lines.append("## Risk flags\n")
    lines.append(
        "- `license_non_mit_flag`: `true` if at least one component has a license value present and it is not exactly `MIT`.\n"
        "- `hostile_origin_flag`: `true` if at least one component has `origin_country` in {Russia, China, Iran}.\n"
        "  - `origin_country` is best-effort and derived from the author email ccTLD (e.g. `.ru`, `.cn`, `.ir`).\n"
    )

    lines.append("## Outputs\n")
    lines.append(f"- Enriched SBOMs: `{_fmt_path(out_dir)}`\n")
    lines.append(f"- Per-SBOM reports: `{_fmt_path(reports_dir)}`\n")

    lines.append("### Components (exploded)\n")
    lines.append(
        "| SBOM | Component | Version | Ecosystem | License | Policy | Author | Author Email | Origin Country | license_non_mit | hostile_origin | enriched |\n"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---:|---:|---:|\n")

    for r in component_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} | {} | {} |\n".format(
                _md_table_cell(r.get("sbom"), max_len=120),
                _md_table_cell(r.get("component"), max_len=120),
                _md_table_cell(r.get("version"), max_len=60),
                _md_table_cell(r.get("ecosystem"), max_len=30),
                _md_table_cell(r.get("license"), max_len=80),
                _md_table_cell(r.get("policy"), max_len=30),
                _md_table_cell(r.get("author_name"), max_len=60),
                _md_table_cell(r.get("author_email"), max_len=60),
                _md_table_cell(r.get("origin_country"), max_len=40),
                str(bool(r.get("license_non_mit"))).lower(),
                str(bool(r.get("hostile_origin"))).lower(),
                str(bool(r.get("enriched"))).lower(),
            )
        )

    batch_report_path = os.path.join(reports_dir, "sbom-enrichment.batch.report.json")
    batch = _load_json(batch_report_path)
    if batch is not None:
        bsum = _report_summary(batch)
        lines.append("\n### Batch aggregate\n")
        lines.append(f"- Batch report: `{_fmt_path(batch_report_path)}`\n")
        lines.append(
            f"- Totals: ok={bsum['ok']}, flag={bsum['flag']}, unknown={bsum['unknown']}, not_enriched={bsum['not_enriched']}\n"
        )

    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=None,
        help="Folder containing out/ and reports/ (default: parent folder of this script)",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root) if args.root else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(root, "out")
    reports_dir = os.path.join(root, "reports")

    os.makedirs(out_dir, exist_ok=True)

    out_readme_path = os.path.join(out_dir, "README.md")
    reports_readme_path = os.path.join(reports_dir, "README.md")

    component_rows = _generate_component_rows(reports_dir=reports_dir)
    md = _render_markdown(component_rows=component_rows, out_dir=out_dir, reports_dir=reports_dir)

    with open(out_readme_path, "w", encoding="utf-8") as f:
        f.write(md)

    with open(reports_readme_path, "w", encoding="utf-8") as f:
        f.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
