# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-01-12

### Fixed

- added git to base image to enable `dbt deps`

### Added

- github action for changelog reminder
- github action for auto release
- github action to push to docker registry (ghcr.io)


## [0.1.1] - 2025-12-09

-  Pinned duckdb to 1.3.2. to avoid this [issue](https://github.com/duckdb/duckdb/issues/19171)
