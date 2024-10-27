FROM python:3.11-bookworm

# Bring poetry, our package manager, and pre-commit hooks
ARG POETRY_VERSION=1.8.1
ARG PRECOMMIT_VERSION=3.6.2
RUN pip install --no-cache-dir \
    poetry==${POETRY_VERSION} \
    pre-commit==${PRECOMMIT_VERSION}


# We may be in docker, but the package's dependecies we install may clash with
# the poetry/pre-commit dependencies (mostly requests version).
# Set up a venv anyway here:
ENV POETRY_VIRTUALENVS_CREATE=true


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
