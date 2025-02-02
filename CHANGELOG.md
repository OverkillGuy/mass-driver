# Changelog for Mass Driver

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]

### Changed

- **BREAKING**: Upgraded pydantic to v2
  - **ACTION REQUIRED** Check your package for Pydantic warnings, follow the
  [pydantic v2 migration guide](https://docs.pydantic.dev/latest/migration).
- **BREAKING**: `ActivityOutcome` rewritten from structure of arrays (dict,
  specifically), into an array-of-structure.
  - Allows for inspection of each repo's entire status, instead of slicing per
    "activity". Per-repo granularity is required to offload activities to
    individual workers, for future performance improvements via concurrency.
  - Each of the new per-repo `RepoOutcome` objects contains a top-level error +
    a per-activity outcome containing error too, allowing for top-level status
    reporting of error + detail of error for each phase (like "Forge failed for
    this repo because the pre-requisite Clone activity failed")
  - **ACTION REQUIRED**: Review any script depending on the JSON result of
    `ActivityOutcome` object.
- **BREAKING**: `ClonedRepo.cloned_path` is now `str`, not `DirectoryPath`.
  - Weaker type means no check for existence of the actual folder, allowing
    for URLs like `s3://`, avoiding actual `tmp_dir` use in local testing.
  - **ACTION REQUIRED****: Update your `PatchDriver`s, replacing
    `repo.cloned_path` with `Path(repo.cloned_path)` in the `run(repo:
    ClonedRepo)` function.
- **BREAKING**: `Forge` plugins no longer require the `pr_statuses` property
  - PRs will be ranked during the `review-pr` command based on the number of PRs
    of each `Forge`-defined status.
  - **ACTION REQUIRED**: Remove `pr_statuses` property from your Forge plugins
- **BREAKING**: Rename `--json-outfile` flag to `--output` (`-o` abbreviation).
- Updated to python-template v1.7.2 (from 1.3.0)

### Added

- New `--debug` argument to the `run` command, to get a `breakpoint` early on
- New `ExceptionRecord` class, used in field `PatchResult.error`, captures
  exceptions found during execution, while remaining serializable.
- New `Error` class for capturing for each repo, what went wrong in any phase
- `ClonedRepo` now includes `commit_hash` string, to know what you cloned
- Add `GlobFileEditor.before_run()` to run arbitrary code before processing the
  first file
- New function `replace_many` in `patchdrivers.brick`, to replace many patterns
  in a string at once. Perfect for the kind of file `sed` replacement
- `PatchDriver` Pydantic base class now allows extra fields by default ([Pydantic Extra fields](https://docs.pydantic.dev/latest/concepts/models/#extra-fields))
- Test fixture `massdriver_runlocal` now takes `extra_args` optional argument to
  allow any CLI flags to be used in tests

### Fixed

- Activity files that are not valid TOML no longer crash mass-driver
- Repos with migration failed (`PatchOutcome != PATCHED_OK`) no longer get
  sent for Forge activity

## v0.18.0 - 2023-11-21

### Added

- New `SingleFileEditor`, derived from `PatchDriver`, for editing single files.
  - Parameter `target_file`, will be fed its text content to `process_file()`.
  - Use via `from mass_driver.drivers.bricks import SingleFileEditor`.
- New `GlobFileEditor`, similarly for editing multiple files from glob pattern.
  - Use via `from mass_driver.drivers.bricks import GlobFileEditor`.

## v0.17.1 - 2023-11-13

### Added

- Update `pyGithub` to `2.1.1`, now throttles Github API to avoid ratelimits

### Fixed

- Catch and log import errors during activity loading, previously silent crashes

## v0.17.0 - 2023-11-12

### Added

- Completing an activity (source, migration, forge) now summarizes results
  - Breakdown of repo count per outcome type, then sorted list of repos per type
- **FASTER**: Optional, experimental multi-threaded per-repo processsing!
  Handling of clone, scan, patching is done as individual thread per repo, with
  N=8 pooled threads.
  - Early data shows a x6 improvement in performance, as cloning
    one repo doesn't block others anymore.
  - Enable via new experimental flag `run --parallel`, defaulting to `False`

### Changed

- **BREAKING**: Renamed`Repo` to `SourcedRepo` in `mass_driver.models.repository`
  - This exposes better the idea of "a Repo as it was Source-d", in contrast to
    `ClonedRepo` "a Repo after it was cloned".
  - Also avoids clashes with `git.Repo` object from gitpython dependency.
- Replaced all `print()` calls to `logging` module
- Loggers used are mostly nested:
  - from `root` (default)
  - to `run` (or other file-activity-based)
  - to `run.repo.<repo-id>` for logs for a specific repo's processing
  - to subloggers like `run.repo.<repo-id>.driver.<driver-plugin-name>`
- `PatchDriver` now has a `logger` obj for such customized logging:
  Repo-processing sets `Patchdriver.logger` named
  `run.repo.<repo-id>.driver.<driver-plugin-name>`
  - **ACTION**: Please replace any `print` with `self.logger.info`!

## v0.16.4 - 2023-11-04

### Fixed

- Attempting to run a Forge activity with `git_push_first=True`, without
  migration or scan activity, no longer causes exit without processing any
  repos. Clone step invoked properly mean remote-clone URLs are now supported,
  converted to local filepaths internally.
- `make docs` now works again with `sphinx-autodoc2`: Pinned `astroid` dep to
  `2.15.8` (< 3.0.0) to avoid the regression caused by unpinned `astroid`.

## v0.16.3 - 2023-09-11

### Fixed

- `ShellDriver` no longer crashes due to irrelevant dataclass import
- Updated `pyGithub`, fixes "missing cryptography" error
- Error messages for bad config file for Sources no longer insist wrongly about
  "Forge config error". Now detecting the validation error's model properly.
- Failing to load a scanner that was selected in config now throws `ImportError`
  on the first plugin-load failure, instead of silently skipping the scanner.

### Changed

- Updated to python-template v1.3.0 (from 1.1.0)

## v0.16.2 - 2023-07-25

### Fixed

- `github-app` forge no longer crashes due to type confusion on a param.

## v0.16.1 - 2023-07-15

### Fixed

- Formatting of the % of PR per status back to 2 digits precision not 11.

## v0.16.0 - 2023-07-13

Breaking interface of `Forge` to facilitate new `view-pr` feature.

### Added

- New `view-pr` feature for bulk reviewing the status of PRs that already exist.

### Changed

- **BREAKING**: New `Forge.get_pr_status()`, required from derived classes,
  returning a string status, used as key to group PRs together for summary
  purposes.
- **BREAKING**: New `Forge.pr_statuses` property, required from derived classes,
  returning a list of all possible string statuses of `Forge.get_pr_status()`,
  sorted from most complete (e.g. merged) to least complete (e.g. not merged,
  has merge-conflicts).

### Removed

- **BREAKING**: Removed `Forge.get_pr()`, which had unclear return type anyway.

## v0.15.0 - 2023-07-05

### Changed

Major break of interface: Rework of the cloning system, merges migration/scan
codepaths, enabling use of Source-discovered information in `PatchDriver.run`.

- **BREAKING**: `PatchDriver.run()` passes `ClonedRepo` obj, not `pathlib.Path`.
  - Any use of `repo` in your `PatchDriver.run()` should use `repo.cloned_path`.
  - See `ClonedRepo` docs, contains information derived from `Source`, such as
    `patch_data` field, arbitrary source-issued information dict.
- **BREAKING**: `tests.fixtures.massdrive()` now returns 3-item-tuple, not 2.
  - Returned tuple: `PatchResult`, `ForgeResult`, `ScanResult` (or `None`)
  - Any tests using `fixtures.massdrive` should now set `mig, forge, scan =`...
  - Swap `fixtures.massdrive_scan` with `fixtures.massdrive` accepting 2 junk arg
- **BREAKING**: `mass-driver scan` CLI removed, now part of `mass-driver run`.
  Activity flow for `run` command is now:
  - Source discovery phase (if any, or from CLI), generating `Repo` list
  - Main phase, iterating over each Repo, first to clone them =`ClonedRepo` list
  - Inside main phase, scan (if any), generating `ScanResult`
  - Inside main phase, migrate (if any), generating `MigrationResult`
  - After main phase,  interactively pause for review if requested
  - Forge activity, iterating over each repo again, creating `ForgeResult`
- **BREAKING**: `models.source` module renamed to `models.repository`.

### Added

- Scan+Migration+Forge can now ALL happen in one run command:
  - Clones one repo, then scanning it, then migrating it, then next repo
  - Can thus do all of Source -> [Clone] -> Scan -> Migrate -> Forge
- New `csv-filelist` Source for importing repos in CSV file format
- New `tests.fixture.massdrive_runlocal()` func to enable source testing

### Fixed

- Secret tokens for Github plugins no longer leak on config dump
  (`--json-outfile` flag), by replacing `str` with `pydantic.SecretStr`.
  - Docs updated to warn downstream devs about this risk.
- Pin `pydantic` to `1.*`, as breaking version `2.0` was just released.

## v0.14.0 - 2023-06-08

### Added

- New `source` feature for discovering what repos to patch/scan.
  - `Source`s are plugins with `discover()` method, returning `Repo`s by ID.
  - Alternative `sources` subcommand to list and detail them
  - New TOML file entry `[mass-driver.source]`, with subkey `source_name` used
    to select which source plugin to enable.
  - Simple sources provided:
    - `repo-list` for in-activity-file repository list
    - `repo-filelist` to point to a separate file listing repos
    - `template-filelist` to expand a template against a file listing repos
  - `github-search` and `github-app-search` Sources for Github Repository search
  - CLI args `--repo-path` and `--repo-filelist` still available, overriding any
    source, so that `massdriver.source` is only required if lacking CLI args
- CI (pytest, pre-commit) set up via Github Actions: [PR #1](https://github.com/OverkillGuy/mass-driver/pull/1)

## v0.13.2 - 2023-06-03

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
- New, simpler testing fixture `massdrive_check_file` for PatchDriver that
  affect single files

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
