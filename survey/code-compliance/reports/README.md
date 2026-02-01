# SBOM Enrichment Reports
Generated: `2026-01-29T16:16:13Z`
## How to reproduce
From `survey/code-compliance/`:

```bash
python3 enrich_sbom.py --in . --out ./out --report ./reports
python3 reports/write_readme.py
```
## Risk flags
- `license_non_mit_flag`: `true` if at least one component has a license value present and it is not exactly `MIT`.
- `hostile_origin_flag`: `true` if at least one component has `origin_country` in {Russia, China, Iran}.
  - `origin_country` is best-effort and derived from the author email ccTLD (e.g. `.ru`, `.cn`, `.ir`).
## Outputs
- Enriched SBOMs: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/out`
- Per-SBOM reports: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports`
### Components (exploded)
| SBOM | Component | Version | Ecosystem | License | Policy | Author | Author Email | Origin Country | license_non_mit | hostile_origin | enriched |
|---|---|---|---|---|---|---|---|---|---:|---:|---:|
| `AutoNav-main-sbom-cyclonedx` | `gymnasium>=0.29.0` | `1.2.3` | `pypi` | `MIT License` | `ok` | `` | `Farama Foundation <contact@farama.org>` | `` | true | false | true |
| `AutoNav-main-sbom-cyclonedx` | `numpy>=1.20.0` | `2.4.1` | `pypi` | `` | `unknown` | `Travis E. Oliphant et al.` | `NumPy Developers <numpy-discussion@python.org>` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `stable-baselines3>=2.0.0` | `2.7.1` | `pypi` | `MIT` | `ok` | `Antonin Raffin` | `antonin.raffin@dlr.de` | `Germany` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `tensorboard>=2.0.0` | `2.20.0` | `pypi` | `Apache 2.0` | `ok` | `Google Inc.` | `packages@tensorflow.org` | `` | true | false | true |
| `AutoNav-main-sbom-cyclonedx` | `pyyaml>=6.0.0` | `6.0.3` | `pypi` | `MIT` | `ok` | `Kirill Simonov` | `xi@resolvent.net` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `matplotlib>=3.5.0` | `3.10.8` | `pypi` | `License agreement for matplotlib versions 1.3.0 and later =====================…` | `ok` | `John D. Hunter, Michael Droettboom` | `Unknown <matplotlib-users@python.org>` | `` | true | false | true |
| `AutoNav-main-sbom-cyclonedx` | `pygame>=2.0.0` | `2.6.1` | `pypi` | `LGPL` | `unknown` | `A community project.` | `pygame@pygame.org` | `` | true | false | true |
| `AutoNav-main-sbom-cyclonedx` | `pyproj>=3.0.0` | `3.7.2` | `pypi` | `` | `unknown` | `pyproj contributors` | `Jeff Whitaker <jeffrey.s.whitaker@noaa.gov>` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `pytest>=7.0.0` | `9.0.2` | `pypi` | `` | `unknown` | `Holger Krekel, Bruno Oliveira, Ronny Pfannschmidt, Floris B…` | `` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `pytest-cov>=4.0.0` | `7.0.0` | `pypi` | `` | `unknown` | `` | `Marc Schlaich <marc.schlaich@gmail.com>` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `black>=22.0.0` | `26.1.0` | `pypi` | `` | `unknown` | `` | `Łukasz Langa <lukasz@langa.pl>` | `Poland` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `isort>=5.0.0` | `7.0.0` | `pypi` | `` | `unknown` | `` | `Timothy Crosley <timothy.crosley@gmail.com>, staticdev <sta…` | `` | false | false | true |
| `AutoNav-main-sbom-cyclonedx` | `mypy>=0.990` | `1.19.1` | `pypi` | `MIT` | `ok` | `` | `Jukka Lehtosalo <jukka.lehtosalo@iki.fi>` | `Finland` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `fastapi` | `0.128.0` | `pypi` | `` | `unknown` | `` | `=?utf-8?q?Sebasti=C3=A1n_Ram=C3=ADrez?= <tiangolo@gmail.com>` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `uvicorn[standard]` | `0.40.0` | `pypi` | `` | `unknown` | `` | `Tom Christie <tom@tomchristie.com>` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `pydantic-settings` | `2.12.0` | `pypi` | `` | `unknown` | `` | `Samuel Colvin <s@muelcolvin.com>, Eric Jolibois <em.joliboi…` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `loguru` | `0.7.3` | `pypi` | `` | `unknown` | `` | `Delgan <delgan.py@gmail.com>` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `aiofiles` | `25.1.0` | `pypi` | `Apache-2.0` | `ok` | `` | `Tin Tvrtkovic <tinchester@gmail.com>` | `` | true | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@emotion/react` | `^11.14.0` | `npm` | `MIT` | `ok` | `Emotion Contributors` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@emotion/styled` | `^11.14.1` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@microsoft/fetch-event-source` | `^2.0.1` | `npm` | `MIT` | `ok` | `Microsoft` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@mui/icons-material` | `^7.3.5` | `npm` | `MIT` | `ok` | `MUI Team` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@mui/material` | `^7.3.5` | `npm` | `MIT` | `ok` | `MUI Team` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@mui/material-nextjs` | `^7.3.5` | `npm` | `MIT` | `ok` | `MUI Team` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `js-yaml` | `^4.1.1` | `npm` | `MIT` | `ok` | `Vladimir Zapparov` | `dervus.grim@gmail.com` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `leaflet` | `^1.9.4` | `npm` | `BSD-2-Clause` | `ok` | `` | `` | `` | true | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `next` | `15.3.5` | `pypi` | `MIT` | `ok` | `saenews` | `contact@advaitlabs.com` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `re-resizable` | `^6.11.2` | `npm` | `MIT` | `ok` | `bokuweb` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `react` | `^19.0.0` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `react-dom` | `^19.0.0` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `react-hot-toast` | `^2.6.0` | `npm` | `MIT` | `ok` | `Timo Lins` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `react-leaflet` | `^5.0.0` | `npm` | `Hippocratic-2.1` | `unknown` | `Paul Le Cam` | `paul@ulem.net` | `` | true | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `uuid` | `^13.0.0` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `zustand` | `^5.0.8` | `npm` | `MIT` | `ok` | `Paul Henschel` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@eslint/eslintrc` | `^3` | `npm` | `MIT` | `ok` | `Nicholas C. Zakas` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@tailwindcss/postcss` | `^4` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@types/js-yaml` | `^4.0.9` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@types/leaflet` | `^1.9.21` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@types/node` | `^20` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@types/react` | `^19` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `@types/react-dom` | `^19` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `eslint` | `^9` | `npm` | `MIT` | `ok` | `Nicholas C. Zakas` | `nicholas+npm@nczconsulting.com` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `eslint-config-next` | `15.3.5` | `pypi` | `` | `unknown` | `` | `` | `` | false | false | false |
| `Rakia-C2-main-sbom-cyclonedx` | `tailwindcss` | `^4` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `Rakia-C2-main-sbom-cyclonedx` | `typescript` | `^5` | `npm` | `Apache-2.0` | `ok` | `Microsoft Corp.` | `` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `gymnasium` | `1.2.3` | `pypi` | `MIT License` | `ok` | `` | `Farama Foundation <contact@farama.org>` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `numpy` | `2.4.1` | `pypi` | `` | `unknown` | `Travis E. Oliphant et al.` | `NumPy Developers <numpy-discussion@python.org>` | `` | false | false | true |
| `Rakia-main-sbom-cyclonedx` | `matplotlib` | `3.10.8` | `pypi` | `License agreement for matplotlib versions 1.3.0 and later =====================…` | `ok` | `John D. Hunter, Michael Droettboom` | `Unknown <matplotlib-users@python.org>` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `streamlit` | `1.53.1` | `pypi` | `Apache License 2.0` | `ok` | `Snowflake Inc` | `hello@streamlit.io` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `stable-baselines3[extra]` | `2.7.1` | `pypi` | `MIT` | `ok` | `Antonin Raffin` | `antonin.raffin@dlr.de` | `Germany` | false | false | true |
| `Rakia-main-sbom-cyclonedx` | `torch` | `2.10.0` | `pypi` | `BSD-3-Clause` | `ok` | `` | `PyTorch Team <packages@pytorch.org>` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `torchvision` | `0.25.0` | `pypi` | `BSD` | `ok` | `PyTorch Core Team` | `soumith@pytorch.org` | `` | true | false | true |
| `Rakia-main-sbom-cyclonedx` | `torchaudio` | `2.10.0` | `pypi` | `` | `unknown` | `Soumith Chintala, David Pollack, Sean Naren, Peter Goldsbor…` | `soumith@pytorch.org` | `` | false | false | true |
| `Rakia-main-sbom-cyclonedx` | `pyglet` | `2.1.12` | `pypi` | `` | `unknown` | `` | `Alex Holkner & contributors <Alex.Holkner@gmail.com>` | `` | false | false | true |
| `Rakia-main-sbom-cyclonedx` | `scipy` | `1.17.0` | `pypi` | `Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Developers. All rights rese…` | `flag` | `` | `SciPy Developers <scipy-dev@python.org>` | `` | true | false | true |
| `jsbsim_server-main-sbom-cyclonedx` | `grpcio` | `1.76.0` | `pypi` | `Apache License 2.0` | `ok` | `The gRPC Authors` | `grpc-io@googlegroups.com` | `` | true | false | true |
| `jsbsim_server-main-sbom-cyclonedx` | `jsbsim` | `1.2.3` | `pypi` | `LGPL 2.1` | `unknown` | `Jon S. Berndt et al.` | `jsbsim-users@lists.sourceforge.net` | `` | true | false | true |
| `jsbsim_server-main-sbom-cyclonedx` | `loguru` | `0.7.3` | `pypi` | `` | `unknown` | `` | `Delgan <delgan.py@gmail.com>` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `cors` | `^2.8.5` | `npm` | `MIT` | `ok` | `Troy Goode` | `troygoode@gmail.com` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `express` | `^4.19.2` | `npm` | `MIT` | `ok` | `TJ Holowaychuk` | `tj@vision-media.ca` | `Canada` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `js-yaml` | `^4.1.0` | `npm` | `MIT` | `ok` | `Vladimir Zapparov` | `dervus.grim@gmail.com` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `leaflet` | `^1.9.4` | `npm` | `BSD-2-Clause` | `ok` | `` | `` | `` | true | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `react` | `^18.3.1` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `react-dom` | `^18.3.1` | `npm` | `MIT` | `ok` | `` | `` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `react-leaflet` | `^4.2.1` | `npm` | `Hippocratic-2.1` | `unknown` | `Paul Le Cam` | `paul@ulem.net` | `` | true | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `@vitejs/plugin-react` | `^4.3.4` | `npm` | `MIT` | `ok` | `Evan You` | `` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `concurrently` | `^9.1.0` | `npm` | `MIT` | `ok` | `Kimmo Brunfeldt` | `` | `` | false | false | true |
| `red-skies--experiments-manager-master-sbom-cyclonedx` | `vite` | `^6.0.6` | `npm` | `MIT` | `ok` | `Evan You` | `` | `` | false | false | true |
| `rl-agent-renderer-master-sbom-cyclonedx` | `fastapi` | `0.110.0` | `pypi` | `` | `unknown` | `` | `=?utf-8?q?Sebasti=C3=A1n_Ram=C3=ADrez?= <tiangolo@gmail.com>` | `` | false | false | true |
| `rl-agent-renderer-master-sbom-cyclonedx` | `uvicorn[standard]` | `0.27.1` | `pypi` | `` | `unknown` | `` | `Tom Christie <tom@tomchristie.com>` | `` | false | false | true |
| `rl-agent-renderer-master-sbom-cyclonedx` | `httpx` | `0.27.0` | `pypi` | `BSD-3-Clause` | `ok` | `` | `Tom Christie <tom@tomchristie.com>` | `` | true | false | true |
| `skysim-main-sbom-cyclonedx` | `geographiclib` | `2.1` | `pypi` | `MIT` | `ok` | `Charles Karney` | `karney@alum.mit.edu` | `` | false | false | true |
| `skysim-main-sbom-cyclonedx` | `jsbsim` | `1.2.3` | `pypi` | `LGPL 2.1` | `unknown` | `Jon S. Berndt et al.` | `jsbsim-users@lists.sourceforge.net` | `` | true | false | true |
| `skysim-main-sbom-cyclonedx` | `pynput` | `1.8.1` | `pypi` | `LGPLv3` | `unknown` | `Moses Palmér` | `moses.palmer@gmail.com` | `` | true | false | true |
| `skysim-main-sbom-cyclonedx` | `pytest` | `9.0.2` | `pypi` | `` | `unknown` | `Holger Krekel, Bruno Oliveira, Ronny Pfannschmidt, Floris B…` | `` | `` | false | false | true |
| `skysim-main-sbom-cyclonedx` | `loguru` | `0.7.3` | `pypi` | `` | `unknown` | `` | `Delgan <delgan.py@gmail.com>` | `` | false | false | true |
| `skysim-main-sbom-cyclonedx` | `PyYAML` | `6.0.3` | `pypi` | `MIT` | `ok` | `Kirill Simonov` | `xi@resolvent.net` | `` | false | false | true |
| `skysim_bridge-main-sbom-cyclonedx` | `websockets>=12.0` | `16.0` | `pypi` | `` | `unknown` | `` | `Aymeric Augustin <aymeric.augustin@m4x.org>` | `` | false | false | true |
| `skysim_wrapper-main-sbom-cyclonedx` | `loguru` | `0.7.3` | `pypi` | `` | `unknown` | `` | `Delgan <delgan.py@gmail.com>` | `` | false | false | true |
| `skysim_wrapper-main-sbom-cyclonedx` | `pydantic` | `2.12.5` | `pypi` | `` | `unknown` | `` | `Samuel Colvin <s@muelcolvin.com>, Eric Jolibois <em.joliboi…` | `` | false | false | true |
| `skysim_wrapper-main-sbom-cyclonedx` | `pyyaml` | `6.0.3` | `pypi` | `MIT` | `ok` | `Kirill Simonov` | `xi@resolvent.net` | `` | false | false | true |

### Batch aggregate
- Batch report: `/home/tomer/projects/matrix/red-skies--sprint-artifacts/survey/code-compliance/reports/sbom-enrichment.batch.report.json`
- Totals: ok=52, flag=1, unknown=27, not_enriched=1
