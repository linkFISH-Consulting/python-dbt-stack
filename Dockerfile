# Example Docker file how to create a minimal Docker Container to run dbt

FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS base

# If another base image is needed, add uv from their official distroless image
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV HOSTNAME="lf-dbt"

# for mssql odbc driver apt install
ENV ACCEPT_EULA=Y

# Setup a non-root user
RUN groupadd --system --gid 999 lf_admin \
    && useradd --system --gid 999 --uid 999 --create-home lf_admin

# -------------------------------- UV Settings ------------------------------- #

# see https://github.com/astral-sh/uv-docker-example
# and https://docs.astral.sh/uv/guides/integration/docker/

# Disable Python downloads, because we want to use the system interpreter
ENV UV_PYTHON_DOWNLOADS=0

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# -------------------------------- MSSQL ODBC -------------------------------- #

RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=type=cache,target=/var/cache/apt,type=cache \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    wget \
    curl

# Add Microsoft repository for ODBC Driver 18 for SQL Server (dbt-sqlserver)
# Using the new approach since apt-key was depricated
RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=type=cache,target=/var/cache/apt,type=cache \
    mkdir -p /etc/apt/keyrings && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=type=cache,target=/var/cache/apt,type=cache \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    msodbcsql18

# ---------------------------- Python Dependencies --------------------------- #

# Git is needed for `dbt deps`
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Either get our python project from the host, or from git
COPY . /app
# RUN apt-get update && apt-get install -y git
# RUN git clone https://github.com/your-repo/project.git /app

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# In contrast to the uv example, we do not have a project - we only want to get
# our dependencies in.
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER lf_admin
