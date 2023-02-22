# Mass-driver development roadmap

An overview of the feature development roadmap, as mass-driver is ambitious and
multiple "phases" will be necessary.

Note the phases are still fuzzy, as I haven't really designed the system much
further than the first phase. Consider what's written below a healthy first
pass.

These sections are in rough order in which they'll be pursued.

## Consolidation of CLI

Before anything, polish the usecase of one-shot PR generation as CLI.

- Define & version the file interfaces (single file for both migration + forge)
- Update the commands of CLI to match that file (pause between activities)
- Create dummy `PatchDriver` and `Forge` for testing
- Set up enough testing to guarantee system
- Add optional output file to JSON (currently Pydantic objects = JSON castable)
- Create cookiecutter template (including tests) for each plugin type


- Publish JSON Schema of the `Activity` model, to enable validation/IDE completion
- Create RepoSource plugin for fetching list of repos (with sample "RepoList" = NOOP)
- Per-repo migration/forge config overrides (enabled by RepoSource)

## Persistence

Eventually, the generated data should be persisted, to enable reviewing PRs
status over time, after PR created by the oneshot PR generation system.

We need to start saving data we generate in SQL-able format (starting from
JSON). Use that as data source (repo list cacheing) and output (PR list with
migration stored).

Suggest starting with SQLite for data storage, making this easy to start with.

## API and Service

If we have data storage in SQL (such as SQLite), let's daemonize the system into
a long-running service with an API, so that migrations/forge can be triggered
from HTTP.

Note that presence of API should NOT prevent the CLI from being used still.


## Web view?

Proper user-facing web view is a great idea to base off the API, but off scope
for now because I'm no web dev, and can't be focusing on learning web tech at
the same time.

Could be a fun learning project in Django?

## Closing the control loop

Add some concepts like data sources and hooks (consider getting/cacheing package
list from Pypi.org, and new package version would trigger a Migration for
upgrading to that new package version).

In general, set up some automated rules so that migrations can be automatically
triggered on preconditions rather than always manually pushed.

Letting an automated PR creator bot loose will require a LOT of safeguards,
we'll need exponential backoffs, circuitbreakers, quiet periods, etc.

The more I think about this phase, the stronger I feel AGAINST it. We'll see.

## Dependabot-style dev update-subscriptions

Enable devs who want to get "updates" (in the generic sense, not just package
manager) to subscribe to migrations when they become available ("send me a PR
when my Dockerfile's `FROM` gets an update").

Configurable delay ("Weekly PRs for pypi, immediate for Dockerfile").

I think of this a lot like [pre-commit](https://pre-commit.com), with a dev-defined per-repo list
of subscriptions that need to be kept up to date.
