# Changelog for Mass Driver


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]

### Added
- New `Jsonpatch` Driver, for applying an RFC6902 JSON Patch
- New `mass-driver(1)` man page output to `make docs`


## v0.3.1 - 2022-11-11


### Changed
- PatchDriver API simplified, now using single func for detect + patch:
  called via `PatchDriver.run(repo: Path, dry_run: bool)`.
- CLI simplified when exposing `PatchDriver.run()`, now uses either `--dry-run`
  (the default setup) or `--really-commit-changes` for committing (not pushing)


## v0.3.0 - 2022-11-11

### Added
- Poetry Driver stub for major version of packages in `pyproject.toml`.
  Showcases JSON Pointers (RFC6901) for structured fields modification.


## v0.2.0 - 2022-11-11

### Added
- Basic clone/detect/patch/commit workflow, with basic Github support


## v0.1.0 - 2022-11-10
### Added
- New python module `mass_driver`, exposed as shell command `mass-driver`
