ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

COPY dist/*.tar.gz /tmp/

RUN pip install --no-cache-dir /tmp/*.tar.gz
