ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ARG OPENCV_HEADLESS_VERSION=4.12.0.88

# Use a cache mount for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install opencv-python-headless==$OPENCV_HEADLESS_VERSION

COPY dist/*.whl /tmp/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install /tmp/*.whl && rm /tmp/*.whl