FROM python:3.11-bullseye

# This file a copy of our root-level Dockerfile, for lazyness. Note that
# hadolint (Dockerifle linter), configured in .pre-commit-config.yaml, is still
# applying to the current file.

# Bring poetry, our package manager, and pre-commit hooks
ARG POETRY_VERSION=1.3.2
ARG PRECOMMIT_VERSION=3.0.4
RUN pip install --no-cache-dir \
    poetry==${POETRY_VERSION} \
    pre-commit==${PRECOMMIT_VERSION}

# Already in docker, no venv needed
ENV POETRY_VIRTUALENVS_CREATE=false


# Workaround critical-level CVEs in Python image
# By forcing just security update (no featureful updates, as part of apt conf)
# Also install make while we're at it, but ignore pinning version warning
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y make \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /workdir
WORKDIR /workdir

# Install the local package dependencies (dev-mode)
RUN poetry install
