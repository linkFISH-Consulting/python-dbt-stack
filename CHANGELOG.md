# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

TLDR:
- Bugfixes v0.0.1 (Revision)
- Features v0.1.0 (Minor Version)
- Breaking Changes v1.0.0 (Major Version)

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


[0.1.5]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/linkFISH-Consulting/python-dbt-stack/compare/v0.1.3...v0.1.4
