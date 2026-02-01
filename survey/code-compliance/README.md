# SBOM Enrichment (Process + Outputs)
Generated: `2026-01-29T13:45:56Z`
## What we did
We produced **enriched CycloneDX SBOMs** by combining two phases:

1. **Dependency extraction / SBOM creation (baseline)**
   - Python projects: parse dependency manifests such as `requirements.txt` (and optionally `pyproject.toml` / `poetry.lock`) to extract package names and version constraints.
   - Node/TypeScript projects: parse `package.json` + lockfiles (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`) to extract package names and versions.
   - TypeScript configuration like `tsconfig.json` can help identify the project layout/build context, but it is **not** a dependency source of record (dependencies come from `package.json`/lockfiles).

   The baseline SBOMs in this folder were captured as CycloneDX JSON (spec v1.5).

2. **Auto-enrichment of SBOM components (this repo’s tooling)**
   - For each `component` in the SBOM, infer ecosystem (**PyPI** vs **npm**) from the component name/version format.
   - Query public registries to fill in missing metadata:
     - **PyPI**: `https://pypi.org/pypi/<name>/json`
     - **npm**: `https://registry.npmjs.org/<name>`
   - Write back into CycloneDX component fields:
     - `licenses`
     - `supplier` (best-effort)
     - `externalReferences` (homepage + VCS URL)
     - `properties.release:published` (best-effort publish time)

   Additionally, we classify licenses into a simple policy bucket:

   - **ok**: MIT / BSD / Apache
   - **flag**: GPL / AGPL (and LGPL)
   - **unknown**: anything else or missing

## Usage

Run commands from this directory:

```bash
cd survey/code-compliance
```

Enrich a single CycloneDX SBOM JSON file:

```bash
python3 enrich_sbom.py \
  --in AutoNav-main-sbom-cyclonedx.json \
  --out AutoNav-main-sbom-cyclonedx.enriched.json \
  --report AutoNav-main-sbom-cyclonedx.report.json
```

Batch enrich all `*.json` files in this folder into `./out` and `./reports` (directories are auto-created if missing):

```bash
python3 enrich_sbom.py \
  --in . \
  --out ./out \
  --report ./reports
```

Regenerate `README.md` (overwrites it) from the current `./out` + `./reports` contents:

```bash
python3 write_readme.py
```

## Outputs
- Enriched SBOMs: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out`
- Per-SBOM reports: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports`
### Summary table
| SBOM | Enriched SBOM | Report | ok | flag | unknown | not_enriched |
|---|---|---:|---:|---:|---:|---:|
| `AutoNav-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/AutoNav-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/AutoNav-main-sbom-cyclonedx.report.json` | 6 | 0 | 7 | 0 |
| `Rakia-C2-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/Rakia-C2-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/Rakia-C2-main-sbom-cyclonedx.report.json` | 25 | 0 | 2 | 5 |
| `Rakia-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/Rakia-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/Rakia-main-sbom-cyclonedx.report.json` | 1 | 0 | 0 | 9 |
| `jsbsim_server-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/jsbsim_server-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/jsbsim_server-main-sbom-cyclonedx.report.json` | 0 | 0 | 0 | 3 |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/red-skies--experiments-manager-master-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/red-skies--experiments-manager-master-sbom-cyclonedx.report.json` | 9 | 0 | 1 | 0 |
| `rl-agent-renderer-master-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/rl-agent-renderer-master-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/rl-agent-renderer-master-sbom-cyclonedx.report.json` | 1 | 0 | 2 | 0 |
| `skysim-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/skysim-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/skysim-main-sbom-cyclonedx.report.json` | 0 | 0 | 0 | 6 |
| `skysim_bridge-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/skysim_bridge-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/skysim_bridge-main-sbom-cyclonedx.report.json` | 0 | 0 | 1 | 0 |
| `skysim_wrapper-main-sbom-cyclonedx` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out/skysim_wrapper-main-sbom-cyclonedx.enriched.json` | `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/skysim_wrapper-main-sbom-cyclonedx.report.json` | 0 | 0 | 0 | 3 |

### Batch aggregate
- Batch report: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/sbom-enrichment.batch.report.json`
- Totals: ok=42, flag=0, unknown=13, not_enriched=26
