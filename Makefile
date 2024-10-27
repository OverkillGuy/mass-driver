# Run 'make help' to see guidance on usage of this Makefile

# Load .env file if any, for secrets+values (string value, scripts fail in .env)
ifneq (,$(wildcard ./.env))
	include .env
	export
endif

# Variables set as fallback: descending priority is:
# - 'make' invocation-level overrides
# - values stored in .env, loaded
# - Fallback values using ?=, see below:
DOCKER_IMAGE_NAME?=mass-driver
DOCKER_REGISTRY?=
APP_VERSION?=$(shell poetry version --short)

## Default command, run via 'make' or 'make all'
.PHONY: all
all: install lint test docs build install-hooks

## Generate the help message by reading the Makefile
.PHONY: help
help:
	@echo "This makefile contains the following targets, from most commonly used to least: (docs first, then target name)"
	@awk \
		'/^##/ {sub(/## */,""); print} \
		/^[a-z0-9-]+:/ && !/.PHONY:/ \
			{sub(/:.*/, ""); print "⮡   \033[31;1;4m" $$0 "\033[0m\n" }' \
		Makefile

## Set up the virtualenv and install the package + dependencies
.PHONY: install
install:
	poetry install

## Run the linters and formatters on all files (not just staged for commit)
.PHONY: lint
lint:
	pre-commit run --all --all-files

## Run the tests
.PHONY: test
test:
	poetry run pytest

.PHONY: clear
clear:
	-find .mass_driver/ -delete

ACTION=run --no-pause
FILE=clone.toml
OUTPUT=
.PHONY: run
run: clear  # Remember to export GITHUB_API_TOKEN beforehand (unless dummy forge)
	poetry run mass-driver ${ACTION} ${FILE} ${OUTPUT}

.PHONY: docs
docs: clean-docs
	cd docs && make html
	poetry run doc2dash \
		--force \
		--name mass-driver \
		docs/build/html \
		--destination docs/build/docset \
		--icon docs/source/_static/icon_small.png

.PHONY: clean-docs
clean-docs:
	-find docs/build/ -delete

## Serve the generated docs on a port of localhost
.PHONY: docs-serve
docs-serve:
	cd docs/build/html && python3 -m http.server

## Build the wheel/tarball package
.PHONY: build
build:
	poetry build

## Set up the pre-commit hooks to execute on next git commit
.PHONY: install-hooks
install-hooks:
	pre-commit install

## Build the 'release' docker image (just the package installed)
.PHONY: docker-build-release
docker-build-release: export-requirements
	docker build \
		-t "${DOCKER_REGISTRY}${DOCKER_IMAGE_NAME}:${APP_VERSION}" \
		-f release.Dockerfile \
		.

## Build the 'dev' docker image (all tools and code)
.PHONY: docker-build-dev
docker-build-dev:
	docker build -t ${DOCKER_IMAGE_NAME}-dev .

##  Make a release commit + tag, creating Changelog entry
##  Set BUMP variable to any of poetry-supported (major, minor, patch)
##  or number (1.2.3 etc), see 'poetry version' docs for details
##  Default the bump to a patch (v1.2.3 -> v1.2.4)
BUMP=patch
.PHONY: release
release:
# Set the new version Makefile variable after the version bump
	$(eval NEW_VERSION := $(shell poetry version --short ${BUMP}))
	$(eval TMP_CHANGELOG := $(shell mktemp))
	sed \
		"s/\(## \[Unreleased\]\)/\1\n\n## v${NEW_VERSION} - $(shell date +%Y-%m-%d)/" \
		CHANGELOG.md > ${TMP_CHANGELOG}
	mv --force ${TMP_CHANGELOG} CHANGELOG.md
	git add CHANGELOG.md pyproject.toml
	git commit -m "Bump to version v${NEW_VERSION}"
	git tag --annotate "v${NEW_VERSION}" \
		--message "Release v${NEW_VERSION}"

##  Less commonly used commands

##  Generate/update the poetry.lock file
.PHONY: lock
lock:
	poetry lock --no-update

##  Update dependencies (within pyproject.toml specs)
##  Update the lock-file at the same time
.PHONY: update
update:
	poetry update --lock

## Generate a pip-compatible requirements.txt
## From the poetry.lock. Mostly for CI use.
.PHONY: export-requirements
export-requirements: lock
	sha256sum poetry.lock > requirements.txt \
		&& sed -i '1s/^/# /' requirements.txt \
		&& poetry export --format=requirements.txt >>requirements.txt


## Confirm the requirements.txt's source (poetry.lock) is identical to current
## poetry.lock file
check-requirements:
	head -n1 requirements.txt | sed 's/^# //' | sha256sum -c

## Install tools (poetry, pre-commit) via pipx
## Assumes you have pipx installed
# See https://jiby.tech/post/my-python-toolbox/#pipx-for-cli-installs-not-pip
.PHONY: install-tools
install-tools:
	pipx install poetry
	pipx inject poetry poetry-plugin-export
	pipx install pre-commit

## Ensure Poetry will generate virtualenv inside the git repo /.venv/
## rather than in a centralized location. This makes it possible to
## manipulate venv more simply
.PHONY: poetry-venv-local
poetry-venv-local:
	poetry config virtualenvs.in-project true

## Delete the virtualenv to clean dependencies
## Useful when switching to a branch with less dependencies
## Requires the virtualenv to be local (see "poetry-venv-local")
.PHONY: poetry-venv-nuke
poetry-venv-nuke:
	find .venv -delete
