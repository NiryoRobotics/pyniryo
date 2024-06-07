#!/usr/bin/env bash

# Create the venv
if [ $(which virtualenv) ]; then
    virtualenv venv
else
    python3 -m venv venv
fi
source venv/bin/activate

# Install the dependencies for the docs
pip install -r docs/requirements.txt

if [[ $1 -ne "--docs-only" ]]; then
    # Install main dependencies
    pip install -r requirements.txt
fi

