FROM python:3.11 as builder

# Bring poetry, our package manager
ARG POETRY_VERSION=1.8.1
RUN pip install --no-cache-dir \
    poetry==${POETRY_VERSION}

# Copy code in to build a package
COPY . /workdir/
WORKDIR /workdir

RUN poetry build -f wheel

# Start over with just the binary package install
FROM python:3.11-slim as runner

# Bring the wheel file
COPY --from=builder /workdir/dist /app
# And pinned dependencies from lockfile
COPY requirements.txt /app

# Install the prod-requirements (pinned from poetry.lock to SHA256)
# Then the actual code (with all dependencies already met)
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir /app/*.whl

ENTRYPOINT ["mass-driver"]
