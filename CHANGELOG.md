# Changelog for Mass Driver


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]


## v0.9.0 - 2023-03-12

### Added
- New optional Migration params: `commit_author_name` + `commit_author_email`,
  used to override the git commit author.


## v0.8.0 - 2023-02-24

### Added
- New file type `Activity` combines `Migration` and `Forge`
- New `Forge` named `dummy` for testing purposes
- New `git_push_first` boolean param in Forge to disable git pushing.
- New `ActivityOutcome` to capture the full result of a migration/forge sequence

### Changed
- Replace commands `run-migration` + `run-forge` by new `run`, using the
  `Activity` file type with optionals.
- Internals refactored: all Pydantic objects now under `mass_driver.models`
  (`PatchDriver`, `Forge`, `Activity`)

### Removed
- Options `--really-commit-changes` and `--dry-run`

## v0.7.0 - 2023-02-22

### Added
- New `ROADMAP.md` to clarify The Plan.

### Changed
- Upgrade minimum Python version to 3.11 to use `tomllib`
- Replace `tomlkit` with stdlib `tomllib`

### Fixed
- Migrations, once loaded from TOML, are now proper dict again
- `PatchDriver` instance now independent across repos


## v0.6.1 - 2023-02-06

### Added
- Upgrade pre-commit dependencies + poetry in Dockerfile
- Update pyproject.toml for release to Pypi

## v0.6.0 - 2023-02-04

### Added
- Forges now discovered via setuptools
- New "run-forge" subcommand for creating PRs for on-disk branches
- Implemented GithubForge for PR creation on Github
- New "Stamper" `PatchDriver` for "stamping" new files on repos

### Fixed
- Incorrect Repo creation causing silent cloning errors on some devices

## v0.5.0 - 2023-01-24

### Added
- New plugin system for including third-party PatchDrivers, based on the
  setuptools "entrypoints" system.
- CLI Subcommands for inspecting drivers, running migrations...
- PatchDriver test harness, for ease of plugin development.
- Project objectives (gherkin features in `features/`) now part of docs

### Changed
- `PatchDriver` now inherits Pydantic BaseModel (allows serialization)
- `PatchDriver` func prototype: `run(repo: Path) -> PatchResult`


### Removed
- Complex PatchDrivers (the ones requiring package dependencies)
  removed, moved to separate "plugins" repo.


## v0.4.0 - 2022-11-16

### Added
- New `Jsonpatch` Driver, for applying an RFC6902 JSON Patch
- New `PreCommit` Driver, for running `pre-commit autoupdate`
- New `ShellDriver` for running arbitrary shell commands
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
