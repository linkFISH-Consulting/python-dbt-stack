# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

TLDR:
- Bugfixes v0.0.1 (Revision)
- Features v0.1.0 (Minor Version)
- Breaking Changes v1.0.0 (Major Version)


## [1.1.0] - Upcoming

###  Fixed
- Windows: Logs with non-unicode chars should not crash us anymore (hopefully)
- Mail cli commands: Corrected ssl/tls options, fixed the logging, added timeout option.

### Dev
- Setup CI/CD Actions for ruff and mypy

### Dependencies

- Updated Dependencies. Noteworthy:
    - coasti 0.2.3 -> 0.3.0
    - coasti superset-io 0.1.2 -> 0.3.0
    - dbt-core 1.9 -> 1.12 (now pinned to < 1.13)
    - duckdb 1.5.2 -> 1.5.6 (now pinned to < 2.0)
    - copier==9.17.2 (pinned by coasti installer)
    - sqlalchemy 2.0.49 -> 2.1.6

```text
 - annotated-doc==0.0.4
 + annotated-doc==0.0.5
 - annotated-types==0.7.0
 + annotated-types==0.8.0
 + apache-hamilton==1.90.0
 + ast-serialize==0.13.1
 - azure-core==1.39.0
 - azure-identity==1.25.3
 - certifi==2026.2.25
 + certifi==2026.10.23
 - cffi==2.0.0
 - charset-normalizer==3.4.7
 + charset-normalizer==3.5.2
 - click==8.3.2
 + click==8.5.0
 - coasti==0.2.3
 + coasti==0.3.0
 - coasti-superset-io==0.1.2
 + coasti-superset-io==0.3.0
 - copier==9.17.0
 + copier==9.17.2
 - cryptography==46.0.7
 - dbt-adapters==1.22.10
 + dbt-adapters==1.24.5
 - dbt-common==1.37.3
 + dbt-common==1.39.0
 - dbt-core==1.9.10
 + dbt-core==1.12.6
 + dbt-core-experimental-parser==2.0.8
 - dbt-duckdb==1.9.6
 + dbt-duckdb==1.11.0
 - dbt-fabric==1.9.3
 - dbt-postgres==1.9.1
 + dbt-postgres==1.11.0
 - dbt-protos==1.0.443
 + dbt-protos==1.0.615
 - dbt-semantic-interfaces==0.7.5
 - dbt-sqlserver==1.9.0
 + dbt-sqlserver==1.12.1
 - distlib==0.4.0
 + distlib==0.4.4
 - duckdb==1.5.2
 + duckdb==1.5.6
 - dunamai==1.26.1
 + dunamai==1.26.3
 - filelock==3.28.0
 + filelock==4.2.4
 - funcy==2.0
 + funcy==2.1
 - identify==2.6.18
 + identify==2.6.20
 - idna==3.11
 + idna==3.20
 - importlib-metadata==8.9.0
 + importlib-metadata==10.1.0
 - iniconfig==2.3.0
 + iniconfig==2.3.1
 - lf-py-stack==1.0.3
 + lf-py-stack==1.1.0
 - librt==0.9.0
 + librt==0.16.0
 - markdown-it-py==4.0.0
 + markdown-it-py==4.2.0
 - markupsafe==3.0.3
 + markupsafe==3.0.4
 - mashumaro==3.14
 + mashumaro==3.17
 + metricflow==0.213.0
 - msal==1.36.0
 - msal-extensions==1.3.1
 - msgpack==1.1.2
 + msgpack==1.2.3
 - mypy==1.19.1
 + mypy==2.4.0
 - networkx==3.6.1
 + networkx==3.7
 - nodeenv==1.10.0
 + nodeenv==1.11.0
 - numpy==2.4.4
 + numpy==2.5.4
 + opentelemetry-api==1.45.1
 - packaging==26.1
 + packaging==26.3
 - pandas==3.0.2
 + pandas==3.1.0
 - pathspec==0.12.1
 + pathspec==1.0.4
 - platformdirs==4.9.6
 + platformdirs==4.13.5
 - pluggy==1.6.0
 + pluggy==1.7.0
 - plumbum==2.0.1
 + plumbum==2.0.2
 - polars==1.39.3
 + polars==2.1.0
 - polars-runtime-32==1.39.3
 + polars-runtime-32==2.1.0
 - pre-commit==4.5.1
 + pre-commit==4.7.0
 - prompt-toolkit==3.0.52
 + prompt-toolkit==3.0.53
 - psycopg2-binary==2.9.11
 + psycopg2-binary==2.9.13
 - pycparser==3.0
 - pydantic==2.13.2
 + pydantic==2.14.1
 - pydantic-core==2.46.2
 + pydantic-core==2.50.1
 - pygments==2.20.0
 + pygments==2.21.0
 - pyjwt==2.12.1
 - pyodbc==5.1.0
 - pytest==9.0.3
 + pytest==9.1.1
 - python-discovery==1.2.2
 + python-discovery==1.6.4
 - python-dotenv==1.2.2
 + python-dotenv==1.2.4
 - python-slugify==8.0.4
 + python-slugify==9.1.3
 - pytimeparse==1.1.8
 + pytimeparse==1.1.10
 - pytz==2026.1.post1
 + pytz==2026.5
 + rapidfuzz==3.14.6
 - requests==2.33.1
 + requests==2.34.2
 - rpds-py==0.30.0
 + rpds-py==2026.9.1
 - ruff==0.15.11
 + ruff==0.17.2
 - scipy==1.17.1
 + scipy==1.18.1
 - sf-hamilton==1.89.0
 + sf-hamilton==1.90.0
 - sqlalchemy==2.0.49
 + sqlalchemy==2.1.6
 + sqlglot==30.24.0
 - sqlparse==0.5.5
 + sqlparse==0.6.0
 + tabulate==0.10.0
 - typer==0.24.1
 + typer==0.27.3
 - types-pyyaml==6.0.12.20260408
 + types-pyyaml==6.0.12.20260906
 - typing-extensions==4.15.0
 + typing-extensions==4.16.0
 - typing-inspection==0.4.2
 + typing-inspection==0.4.4
 - urllib3==2.6.3
 + urllib3==2.8.0
 - virtualenv==21.2.4
 + virtualenv==21.14.13
 - wcwidth==0.8.2
 + wcwidth==0.9.4
 - zipp==3.23.1
 + zipp==4.1.2
```

## [1.0.2] - 2026-07-15

### Added

- [coasti installer](https://github.com/coasti-org/coasti_installer) (with [superset-io](https://github.com/coasti-org/superset_io)) now included as a dependency.

## [1.0.1] - 2026-07-02

### Added
- "WARN" Step level, and new env var to `LFPY_WARN_EXIT_1` that will cause warnings to emit exit code 1 (useful if we want warnings to end CI Pipelines)
- duckdb shrinking now has an option to pass a regex to exclude tables, even if their schema should be included: `--exclude-table-name-pattern`

### Fixed
- The `run_cli_command` no longer crashes when commands return badly encoded chars (mainly windows)
- We now return exit code 1 when any step failed. This does not cause early termination, we still run all steps.


## [1.0.0] - 2026-05-29

### Added

- Improved Readme and docs, now including the deployment instrucitons in the wheelhouse.
- CLI: Added `-q` `--quiet` option to suppress step summary tables before and after run.
- CLI: A few python tests

### Fixed
- CLI: Logging step results with messages that contain `[tags]` no longer crashes due to markup errors.

### Changed
- Breaking: CLI: removed `-a` Option, now combined with of `-s` `--select`
- Breaking: Renamed `"SKIP"` step status to `"OMIT"`, so we can use `"SKIP"` to indicate a step that was skipped due to a previous step failing (consistent with dbt's behavior)

## [0.4.0] - 2026-05-04

### Added
- Workflow to automatically generate a wheelhouse as part of each new release, so we can install all dependencies on windows servers without internet access. See `/docs/deploy_wheelhouse_offline.md`

## [0.3.0] - 2026-04-17

### Added
- New component `shrink_duckdb` to create a copy of a duckdb file that only holds specified schemas
- New component `log_dbt_versions` and helper `get_dbt_versions` to see what versions of dependencies are in the current project
- New cli argument `--step-arg` `-a` to pass strings into each step. Extraction and handling have to be done in your `step_function`, but this already provides an easy way, to e.g. pass a selection to dbt like `orchestration.py run -a 'dbt_run: --select my_model'`

### Changed
- We no longer select all steps by default. This was needed to make the `-a` option intutive.
- To select all steps use `-s all`.
- As a consequence, "all" is a reserved keyword, and you can no longer use a step like `def all()` in your orchestration script.

### Dependencies
- Auto Update

## [0.2.1] - 2026-04-07

### Fixed

- Improved formatting of logs and summary so they are more suitable for emails.
- This required adding more formatting options to `mail` and `log` methods.
- Install Guide (readme and requirements.txt export)

## [0.2.0] - 2026-04-02

### Added

- Orchestration tools via Hamilton to build minimal scripts to run a sequence of actions.
- Docs folder, we now separate README content a bit better.

### Changed

- Renamed module from `lf-dbt` to `lf-py-stack` because we do more than shipping dbt now. This should not have much impact on existing setups, because we have not used it as a module yet.

### Dependencies
- Removed duckdb lock, now using latest again (we will need to update our duckdb minimize scripts, see [here](https://github.com/duckdb/duckdb-python/issues/392))
- Updates Sub-dependencies

## [0.1.5] - 2026-01-23

- Added Option to set user and group id, and extra groups for lf_admin.

## [0.1.4] - 2026-01-14

- Added MSSQL odbc driver 18
- Updated Dependencies

## [0.1.3] - 2026-01-12

- Github Action Test

## [0.1.2] - 2026-01-12

### Fixed

- added git to base image to enable `dbt deps`

### Added

- github action for changelog reminder
- github action for auto release
- github action to push to docker registry (ghcr.io)


## [0.1.1] - 2025-12-09

-  Pinned duckdb to 1.3.2. to avoid this [issue](https://github.com/duckdb/duckdb/issues/19171)


[1.0.0]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.4.0...v1.0.0
[0.4.0]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.1...v0.1.2
