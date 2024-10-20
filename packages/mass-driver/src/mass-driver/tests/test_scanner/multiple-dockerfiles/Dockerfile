FROM python:3.11 as builder

# Bring poetry, our package manager
ARG POETRY_VERSION=1.3.2
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copy code in to build a package
COPY . /workdir/
WORKDIR /workdir

RUN poetry build -f wheel

# Start over with just the binary package install
FROM python:3.11-slim as runner

COPY --from=builder /workdir/dist /app

RUN pip install --no-cache-dir /app/*.whl
