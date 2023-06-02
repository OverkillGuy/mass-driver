# Changelog for Mass Driver


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]


### Added
- New `file_ownership` parameter for `stamper`, defaulting to `0664`.

### Fixed
- Exit codes harmonized:
  - `0` for success
  - `1` for failures during the main function
  - `2` for argument parsing errors
- `stamper` driver now creates any missing parent folder to the target
- Remove test depending on `git clone` from Github: Faster, offline tests now


## v0.13.1 - 2023-04-17

### Fixed
- `scan` command now uses `--json-outfile` as expected


## v0.13.0 - 2023-04-17

### Added
- New `scan` feature for scanning repos with arbitrary python functions. See
  new "Scanning" docs:
  - Scanners are plugins declared under `mass-driver.scanners`, linking to
    functions like `my_scanner(repo: Path) -> dict[str, Any]`
  - Alternative `scanners` command to list out detected, available scanners
  - New TOML file entry `[mass-driver.scan]`, with subkey `scanner_names` used
    to select which scanner plugins to enable.
  - Simple scanners `root-files` and `dockerfile-from` provided for reference
  - New fixture `massdriver_scan` and `massdriver_scan_check` for testing scanners
- New optional CLI parameter `--json-outfile` for `run` and `scan`, to save the
  activity outcome to JSON files for analysis

### Changed
- Test fixture `massdrive_check_file` now returns unchecked `result` and
  `reference` blobs for equality assertion (`assert result == reference`) to be
  done by the caller. This enables plugins like `pytest-clarity` to show
  colorful diff. Users of `massdrive_check_file` need to change (on pain of lack
  of test assertion):

```diff
- massdrive_check_file(workdir)
+ result, reference = massdrive_check_file(workdir)
+ assert result == reference, "Massdriver result should match reference"
```


## v0.12.0 - 2023-04-05

### Added
- Auto-detect repo's base branch for Forge: parameter `base_branch` now
  optional, defaulting to repo's default branch


## v0.11.0 - 2023-04-02

### Added
- New `github-app` forge plugin for creating PRs on Github when running
  mass-driver as a Github App
- New Forge params:
  - `forge_config` dict, for Forge-specific non-sensitive config to keep in
    config file, complementing envvars. Similar to `driver_config` for
    Migration.
  - `interactive_pause_every` int, for blocking the Forge, pausing for
    confirmation interactively every few PRs generated. Disabled by default, set
    to 1 to block every PR, or 5 every 5...


## v0.10.0 - 2023-04-02


### Removed
- Unused `migration_name` field of Migration now removed

### Added
- `Forge` subclasses can now grab config via envvars prefixed `FORGE_`. Observe
  that `Forge` now derives from `pydantic.BaseSettings`, see [BaseSettings
  docs](https://docs.pydantic.dev/usage/settings/).
- New, simpler testing fixture `massdrive_check_file` for PatchDriver that affect single files


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
