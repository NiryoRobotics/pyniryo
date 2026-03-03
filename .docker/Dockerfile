ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

COPY dist/*.whl /tmp/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install /tmp/*.whl && rm /tmp/*.whl