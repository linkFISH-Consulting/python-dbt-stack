# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

TLDR:
- Bugfixes v0.0.1 (Revision)
- Features v0.1.0 (Minor Version)
- Breaking Changes v1.0.0 (Major Version)

## [0.3.0] - Upcoming

### Added

- New component `shrink_duckdb` to create a copy of a duckdb file that only holds specified schemas
- New component `log_dbt_versions` and helper `get_dbt_versions` to see what versions of dependencies are in the current project
- New cli argument `--step-arg` `-a` to pass strings into each step. Extraction and handling have to be done in your `step_function`, but this already provides an easy way, to e.g. pass a selection to dbt like `orchestration.py run -a 'dbt_run: --select my_model'`

### Changed
- We no longer select all steps by default. This was needed to make the `-a` option intutive.
- To select all steps use `-s all`.
- As a consequence, "all" is a reserved keyword, and you can no longer use a step like `def all()` in your orchestration script.

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


[0.2.1]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.1...v0.1.2
