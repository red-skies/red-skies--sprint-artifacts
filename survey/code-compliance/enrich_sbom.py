#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


LICENSE_OK = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
}


_CCTLD_TO_COUNTRY = {
    "pl": "Poland",
    "fi": "Finland",
    "se": "Sweden",
    "no": "Norway",
    "dk": "Denmark",
    "de": "Germany",
    "fr": "France",
    "it": "Italy",
    "es": "Spain",
    "pt": "Portugal",
    "nl": "Netherlands",
    "be": "Belgium",
    "ch": "Switzerland",
    "at": "Austria",
    "cz": "Czechia",
    "sk": "Slovakia",
    "hu": "Hungary",
    "ro": "Romania",
    "bg": "Bulgaria",
    "gr": "Greece",
    "ie": "Ireland",
    "uk": "United Kingdom",
    "il": "Israel",
    "ir": "Iran",
    "ua": "Ukraine",
    "ru": "Russia",
    "tr": "Turkey",
    "in": "India",
    "cn": "China",
    "jp": "Japan",
    "kr": "South Korea",
    "tw": "Taiwan",
    "sg": "Singapore",
    "au": "Australia",
    "nz": "New Zealand",
    "ca": "Canada",
    "us": "United States",
    "br": "Brazil",
    "mx": "Mexico",
    "ar": "Argentina",
    "za": "South Africa",
 }

LICENSE_FLAG = {
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
}


@dataclass(frozen=True)
class PackageRef:
    ecosystem: str  # "pypi" | "npm" | "unknown"
    name: str
    version: Optional[str]


def _http_get_json(url: str, timeout_s: float = 15.0) -> Optional[Dict[str, Any]]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "sbom-enricher/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _safe_iso8601(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def _country_from_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None

    m = re.search(r"@([^>\s]+)", email.strip())
    if not m:
        return None

    domain = m.group(1).strip().lower().rstrip(".")
    if not domain or "." not in domain:
        return None

    tld = domain.split(".")[-1]
    if len(tld) != 2:
        return None

    return _CCTLD_TO_COUNTRY.get(tld)


_PYPI_REQ_RE = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[.*\])?\s*(?:==|>=|<=|~=|!=|>|<).*$")


def _parse_component_to_package_ref(component: Dict[str, Any]) -> PackageRef:
    name = (component.get("name") or "").strip()
    version = (component.get("version") or "").strip() or None
    if version == "unspecified":
        version = None

    if name.startswith("@"):
        v = version if version and version != "unspecified" else None
        return PackageRef(ecosystem="npm", name=name, version=v)

    if version and (version.startswith("^") or version.startswith("~")):
        v = version.lstrip("^~")
        return PackageRef(ecosystem="npm", name=name, version=v or None)

    if "[" in name and "]" in name:
        base = name.split("[", 1)[0]
        v = version if version and version != "unspecified" else None
        return PackageRef(ecosystem="pypi", name=base, version=v)

    m = _PYPI_REQ_RE.match(name)
    if m:
        base = m.group(1)
        return PackageRef(ecosystem="pypi", name=base, version=None)

    if version and version != "unspecified" and re.fullmatch(r"\d+(?:\.\d+)*[A-Za-z0-9.\-+]*", version):
        return PackageRef(ecosystem="pypi", name=name, version=version)

    return PackageRef(ecosystem="unknown", name=name, version=None)


def _normalize_purl(pkg: PackageRef) -> Optional[str]:
    if pkg.ecosystem == "pypi":
        if pkg.version:
            return f"pkg:pypi/{pkg.name}@{pkg.version}"
        return f"pkg:pypi/{pkg.name}"

    if pkg.ecosystem == "npm":
        if pkg.name.startswith("@"):
            scope, rest = pkg.name[1:].split("/", 1) if "/" in pkg.name else (pkg.name[1:], "")
            encoded_name = f"%40{scope}/{rest}" if rest else f"%40{scope}"
        else:
            encoded_name = pkg.name
        if pkg.version:
            return f"pkg:npm/{encoded_name}@{pkg.version}"
        return f"pkg:npm/{encoded_name}"

    return None


def _extract_license_spdx(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not raw:
        return None, None
    s = raw.strip()
    if not s:
        return None, None

    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()

    if s in LICENSE_OK or s in LICENSE_FLAG or re.fullmatch(r"[A-Za-z0-9.+-]+", s):
        return s, None

    return None, raw


def _component_set_license(component: Dict[str, Any], spdx_id: Optional[str], name: Optional[str]) -> None:
    if not spdx_id and not name:
        return
    entry: Dict[str, Any] = {"license": {}}
    if spdx_id:
        entry["license"]["id"] = spdx_id
    else:
        entry["license"]["name"] = name
    component["licenses"] = [entry]


def _component_set_supplier(component: Dict[str, Any], supplier_name: Optional[str]) -> None:
    if not supplier_name:
        return
    component["supplier"] = {"name": supplier_name}


def _component_add_external_ref(component: Dict[str, Any], ref_type: str, url: Optional[str]) -> None:
    if not url:
        return
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return
    except Exception:
        return

    refs = component.get("externalReferences")
    if not isinstance(refs, list):
        refs = []
        component["externalReferences"] = refs

    for existing in refs:
        if isinstance(existing, dict) and existing.get("url") == url:
            return

    refs.append({"type": ref_type, "url": url})


def _component_set_property(component: Dict[str, Any], name: str, value: Optional[str]) -> None:
    if not value:
        return
    props = component.get("properties")
    if not isinstance(props, list):
        props = []
        component["properties"] = props

    for p in props:
        if isinstance(p, dict) and p.get("name") == name:
            p["value"] = value
            return

    props.append({"name": name, "value": value})


def _enrich_from_pypi(pkg: PackageRef) -> Dict[str, Any]:
    url = f"https://pypi.org/pypi/{urllib.parse.quote(pkg.name)}/json"
    payload = _http_get_json(url)
    if not payload:
        return {}

    info = payload.get("info") or {}
    license_raw = info.get("license") or None

    home = info.get("home_page") or None
    project_urls = info.get("project_urls") or {}
    homepage = None
    if isinstance(project_urls, dict):
        homepage = project_urls.get("Homepage") or project_urls.get("home") or project_urls.get("homepage")

    repo = None
    if isinstance(project_urls, dict):
        repo = project_urls.get("Source") or project_urls.get("Repository") or project_urls.get("Code")

    author_name = info.get("author") or info.get("maintainer") or None
    author_email = info.get("author_email") or info.get("maintainer_email") or None

    supplier = author_name or author_email or None

    origin_country = _country_from_email(author_email)

    published = None
    if pkg.version:
        releases = payload.get("releases") or {}
        rel = releases.get(pkg.version)
        if isinstance(rel, list) and rel:
            published = _safe_iso8601(rel[0].get("upload_time_iso_8601"))

    return {
        "license_raw": license_raw,
        "homepage": homepage or home,
        "repo": repo,
        "supplier": supplier,
        "author_name": author_name,
        "author_email": author_email,
        "origin_country": origin_country,
        "published": published,
        "resolved_version": info.get("version") if not pkg.version else None,
    }


def _enrich_from_npm(pkg: PackageRef) -> Dict[str, Any]:
    encoded = pkg.name
    if pkg.name.startswith("@"):
        encoded = urllib.parse.quote(pkg.name, safe="@/")
    url = f"https://registry.npmjs.org/{encoded}"
    payload = _http_get_json(url)
    if not payload:
        return {}

    license_raw = payload.get("license")
    homepage = payload.get("homepage")

    repo = None
    repository = payload.get("repository")
    if isinstance(repository, dict):
        repo = repository.get("url")
    elif isinstance(repository, str):
        repo = repository

    author_name = None
    author_email = None
    supplier = None
    author = payload.get("author")
    if isinstance(author, dict):
        author_name = author.get("name")
        author_email = author.get("email")
        supplier = author_name or author_email
    elif isinstance(author, str):
        author_name = author
        supplier = author_name

    origin_country = _country_from_email(author_email)

    published = None
    if pkg.version:
        time = payload.get("time")
        if isinstance(time, dict):
            published = _safe_iso8601(time.get(pkg.version))

    resolved_version = None
    if not pkg.version:
        dist_tags = payload.get("dist-tags")
        if isinstance(dist_tags, dict):
            resolved_version = dist_tags.get("latest")

    return {
        "license_raw": license_raw,
        "homepage": homepage,
        "repo": repo,
        "supplier": supplier,
        "author_name": author_name,
        "author_email": author_email,
        "origin_country": origin_country,
        "published": published,
        "resolved_version": resolved_version,
    }


def _license_policy_bucket(license_id: Optional[str], license_name: Optional[str]) -> str:
    lid = license_id or ""
    lname = license_name or ""
    if lid in LICENSE_FLAG:
        return "flag"
    if lid in LICENSE_OK:
        return "ok"

    lowered = (lid or lname).lower()
    if "agpl" in lowered or re.search(r"\bgpl\b", lowered):
        return "flag"
    if "apache" in lowered or "mit" in lowered or "bsd" in lowered:
        return "ok"

    return "unknown"


def enrich_sbom(sbom: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    report: Dict[str, Any] = {
        "summary": {"ok": 0, "flag": 0, "unknown": 0, "not_enriched": 0},
        "components": [],
    }

    components = sbom.get("components")
    if not isinstance(components, list):
        return sbom, report

    for c in components:
        if not isinstance(c, dict):
            continue

        pkg = _parse_component_to_package_ref(c)
        enrichment: Dict[str, Any] = {}

        if pkg.ecosystem == "pypi":
            enrichment = _enrich_from_pypi(pkg)
        elif pkg.ecosystem == "npm":
            enrichment = _enrich_from_npm(pkg)
        else:
            pypi_try = _enrich_from_pypi(PackageRef("pypi", pkg.name, pkg.version))
            if pypi_try:
                pkg = PackageRef("pypi", pkg.name, pkg.version)
                enrichment = pypi_try
            else:
                npm_try = _enrich_from_npm(PackageRef("npm", pkg.name, pkg.version))
                if npm_try:
                    pkg = PackageRef("npm", pkg.name, pkg.version)
                    enrichment = npm_try

        if not enrichment:
            report["summary"]["not_enriched"] += 1
            report["components"].append(
                {
                    "name": c.get("name"),
                    "version": c.get("version"),
                    "ecosystem": pkg.ecosystem,
                    "license": None,
                    "policy": "unknown",
                    "author_name": None,
                    "author_email": None,
                    "origin_country": None,
                    "enriched": False,
                }
            )
            continue

        resolved_version = enrichment.get("resolved_version")
        if resolved_version and (not c.get("version") or c.get("version") == "unspecified"):
            c["version"] = resolved_version
            pkg = PackageRef(pkg.ecosystem, pkg.name, resolved_version)

        purl = _normalize_purl(pkg)
        if purl:
            c["purl"] = purl

        spdx_id, license_name = _extract_license_spdx(enrichment.get("license_raw"))
        _component_set_license(c, spdx_id=spdx_id, name=license_name)

        _component_set_supplier(c, enrichment.get("supplier"))

        _component_add_external_ref(c, "website", enrichment.get("homepage"))
        _component_add_external_ref(c, "vcs", enrichment.get("repo"))

        _component_set_property(c, "release:published", enrichment.get("published"))

        policy = _license_policy_bucket(spdx_id, license_name)
        report["summary"][policy] += 1
        report["components"].append(
            {
                "name": c.get("name"),
                "version": c.get("version"),
                "ecosystem": pkg.ecosystem,
                "license": spdx_id or license_name,
                "policy": policy,
                "author_name": enrichment.get("author_name"),
                "author_email": enrichment.get("author_email"),
                "origin_country": enrichment.get("origin_country"),
                "enriched": True,
            }
        )

    return sbom, report


def _default_enriched_name(input_filename: str) -> str:
    if input_filename.lower().endswith(".json"):
        return input_filename[:-5] + ".enriched.json"
    return input_filename + ".enriched.json"


def _default_report_name(input_filename: str) -> str:
    if input_filename.lower().endswith(".json"):
        return input_filename[:-5] + ".report.json"
    return input_filename + ".report.json"


def _enrich_one_file(input_path: str, output_path: str, report_path: Optional[str]) -> Dict[str, Any]:
    with open(input_path, "r", encoding="utf-8") as f:
        sbom = json.load(f)

    enriched, report = enrich_sbom(sbom)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, sort_keys=False)
        f.write("\n")

    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=False)
            f.write("\n")

    return report


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_path", required=True)
    parser.add_argument(
        "--out",
        dest="output_path",
        required=False,
        help="Output file path (single-file mode) or output directory (batch mode).",
    )
    parser.add_argument(
        "--report",
        dest="report_path",
        required=False,
        help="Report file path (single-file mode) or report directory (batch mode).",
    )
    args = parser.parse_args(argv)

    input_path = args.input_path
    if os.path.isdir(input_path):
        out_dir = args.output_path or input_path
        if os.path.exists(out_dir) and not os.path.isdir(out_dir):
            raise SystemExit(f"--out must be a directory when --in is a directory: {out_dir}")
        os.makedirs(out_dir, exist_ok=True)

        report_dir = args.report_path
        if report_dir is not None:
            if os.path.exists(report_dir) and not os.path.isdir(report_dir):
                raise SystemExit(f"--report must be a directory when --in is a directory: {report_dir}")
            os.makedirs(report_dir, exist_ok=True)

        total_report: Dict[str, Any] = {
            "summary": {"ok": 0, "flag": 0, "unknown": 0, "not_enriched": 0},
            "files": [],
        }

        for entry in sorted(os.listdir(input_path)):
            if not entry.lower().endswith(".json"):
                continue
            if entry.lower().endswith(".enriched.json") or entry.lower().endswith(".report.json"):
                continue

            in_file = os.path.join(input_path, entry)
            if not os.path.isfile(in_file):
                continue

            out_file = os.path.join(out_dir, _default_enriched_name(entry))
            rep_file = os.path.join(report_dir, _default_report_name(entry)) if report_dir else None

            rep = _enrich_one_file(in_file, out_file, rep_file)
            for k, v in (rep.get("summary") or {}).items():
                if k in total_report["summary"] and isinstance(v, int):
                    total_report["summary"][k] += v

            total_report["files"].append(
                {
                    "input": in_file,
                    "output": out_file,
                    "report": rep_file,
                    "summary": rep.get("summary"),
                }
            )

        if args.report_path:
            batch_report_path = os.path.join(report_dir, "sbom-enrichment.batch.report.json")
            with open(batch_report_path, "w", encoding="utf-8") as f:
                json.dump(total_report, f, indent=2, sort_keys=False)
                f.write("\n")

        return 0

    if not args.output_path:
        raise SystemExit("--out is required when --in is a file")

    _enrich_one_file(input_path, args.output_path, args.report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
