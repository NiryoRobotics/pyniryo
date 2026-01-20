ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ARG OPENCV_HEADLESS_VERSION

COPY dist/*.tar.gz /tmp/

RUN pip install --no-cache-dir /tmp/*.tar.gz \
    && pip install --no-cache-dir opencv-python-headless==$OPENCV_HEADLESS_VERSION \
    && rm /tmp/*.tar.gz \
