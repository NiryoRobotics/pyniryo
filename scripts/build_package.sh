#!/usr/bin/env bash

# Setup build system dependencies
python3 -m pip install --upgrade build

# Build and upload the package
python3 -m build
