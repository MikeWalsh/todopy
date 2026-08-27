# this is the base image
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder


ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
# set up environment variables, applies now and for the container
# precompile for release,
# something about being more resilient across filesystem?, because of the cache below..
# fix python patch release

# set a persistent base directory
WORKDIR /app

# this is a cache for dependencies, stops code changes reinstalling everything
# cache is available during this session, but not to final image
# bind is available, but ???
# having --locked means it compares uv.lock to pyproject.toml??
# -no-install-project keep project out of caching layer
# --no-dev skip ruff etc
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# after dependencies copy in the project dir
COPY . /app

# sync the cache but with the project this time
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# start a new stage
FROM python:3.14-slim-bookworm

# create unprivileged user with static uid, don't run container as root
RUN useradd --create-home --uid 1000 app
WORKDIR /app

# pull in the stuff from the previous stage, assign ownership to new user
COPY --from=builder --chown=app:app /app /app

# prefer venv copies
ENV PATH="/app/.venv/bin:$PATH"
# things after this run as app user
USER app
# Some kind of unnecessary documentation command??
EXPOSE 8000

# run the app
# apparently this array form makes uvicorn pid 1 instead of wrapping in sh
# so uvicorn gets messages
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
