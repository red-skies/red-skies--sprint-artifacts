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


def _sbom_base_name(enriched_filename: str) -> str:
    if enriched_filename.endswith(".enriched.json"):
        return enriched_filename[: -len(".enriched.json")]
    return os.path.splitext(enriched_filename)[0]


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

        eco = c.get("ecosystem") or "unknown"
        ecosystems[str(eco)] = ecosystems.get(str(eco), 0) + 1

    return {
        "components_total": total,
        "components_enriched": enriched_true,
        "licenses_missing": licenses_missing,
        "author_name_present": author_name_present,
        "author_email_present": author_email_present,
        "origin_country_present": origin_country_present,
        "ecosystems": ecosystems,
    }


def _generate_table_rows(out_dir: str, reports_dir: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not os.path.isdir(reports_dir):
        return rows

    for entry in sorted(os.listdir(reports_dir)):
        if not entry.endswith(".report.json"):
            continue
        if entry == "sbom-enrichment.batch.report.json":
            continue

        rep_path = os.path.join(reports_dir, entry)
        rep = _load_json(rep_path)
        if rep is None:
            continue

        base = entry[: -len(".report.json")]
        enriched_path = os.path.join(out_dir, base + ".enriched.json")

        rows.append(
            {
                "name": base,
                "enriched": enriched_path,
                "report": rep_path,
                "summary": _report_summary(rep),
                "dims": _derive_dimensions(rep),
            }
        )

    return rows


def _render_markdown(rows: List[Dict[str, Any]], out_dir: str, reports_dir: str) -> str:
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    lines: List[str] = []
    lines.append("# SBOM Enrichment (Process + Outputs)\n")
    lines.append(f"Generated: `{now}`\n")

    lines.append("## What we did\n")
    lines.append(
        "We produced **enriched CycloneDX SBOMs** by combining two phases:\n\n"
        "1. **Dependency extraction / SBOM creation (baseline)**\n"
        "   - Python projects: parse dependency manifests such as `requirements.txt` (and optionally `pyproject.toml` / `poetry.lock`) to extract package names and version constraints.\n"
        "   - Node/TypeScript projects: parse `package.json` + lockfiles (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`) to extract package names and versions.\n"
        "   - TypeScript configuration like `tsconfig.json` can help identify the project layout/build context, but it is **not** a dependency source of record (dependencies come from `package.json`/lockfiles).\n\n"
        "   The baseline SBOMs in this folder were captured as CycloneDX JSON (spec v1.5).\n\n"
        "2. **Auto-enrichment of SBOM components (this repo’s tooling)**\n"
        "   - For each `component` in the SBOM, infer ecosystem (**PyPI** vs **npm**) from the component name/version format.\n"
        "   - Query public registries to fill in missing metadata:\n"
        "     - **PyPI**: `https://pypi.org/pypi/<name>/json`\n"
        "     - **npm**: `https://registry.npmjs.org/<name>`\n"
        "   - Write back into CycloneDX component fields:\n"
        "     - `licenses`\n"
        "     - `supplier` (best-effort)\n"
        "     - `externalReferences` (homepage + VCS URL)\n"
        "     - `properties.release:published` (best-effort publish time)\n\n"
        "   Additionally, we classify licenses into a simple policy bucket:\n\n"
        "   - **ok**: MIT / BSD / Apache\n"
        "   - **flag**: GPL / AGPL (and LGPL)\n"
        "   - **unknown**: anything else or missing\n"
    )

    lines.append("## How to reproduce\n")
    lines.append(
        "From this directory:\n\n"
        "```bash\n"
        "python3 enrich_sbom.py --in . --out ./out --report ./reports\n"
        "```\n"
    )

    lines.append("## Outputs\n")
    lines.append(f"- Enriched SBOMs: `{_fmt_path(out_dir)}`\n")
    lines.append(f"- Per-SBOM reports: `{_fmt_path(reports_dir)}`\n")

    lines.append("### Summary table\n")
    lines.append(
        "| SBOM | Enriched SBOM | Report | components_total | components_enriched | ok | flag | unknown | not_enriched | ecosystems | licenses_missing | author_name_present | author_email_present | origin_country_present |\n"
    )
    lines.append(
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|\n"
    )

    for r in rows:
        name = r["name"]
        enriched = _fmt_path(r["enriched"])
        report = r.get("report")
        report_cell = _fmt_path(report) if report else "(missing)"
        s = r["summary"]
        d = r.get("dims") or {}
        eco = d.get("ecosystems") or {}
        eco_cell = ", ".join([f"{k}:{eco[k]}" for k in sorted(eco.keys())]) if isinstance(eco, dict) else ""
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |\n".format(
                name,
                enriched,
                report_cell,
                d.get("components_total", 0),
                d.get("components_enriched", 0),
                s["ok"],
                s["flag"],
                s["unknown"],
                s["not_enriched"],
                eco_cell,
                d.get("licenses_missing", 0),
                d.get("author_name_present", 0),
                d.get("author_email_present", 0),
                d.get("origin_country_present", 0),
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

    root = os.path.abspath(args.root) if args.root else os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    out_dir = os.path.join(root, "out")
    reports_dir = os.path.join(root, "reports")
    readme_path = os.path.join(out_dir, "README.md")

    os.makedirs(out_dir, exist_ok=True)

    rows = _generate_table_rows(out_dir=out_dir, reports_dir=reports_dir)
    md = _render_markdown(rows=rows, out_dir=out_dir, reports_dir=reports_dir)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
