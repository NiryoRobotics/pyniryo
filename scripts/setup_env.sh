#!/usr/bin/env bash

create_venv() {
  rm -rf venv
  if [ $(which virtualenv) ]; then
      virtualenv venv || exit 1
  else
      python3 -m venv venv || exit 1
  fi
}

source venv/bin/activate 2&> /dev/null || create_venv

# Install the dependencies for the docs
echo "Installing the dependencies for the docs"
pip install -r docs/requirements.txt > /dev/null

if [[ $1 -ne "--docs-only" ]]; then
    # Install main dependencies
    echo "Installing the main dependencies"
    pip install -r requirements.txt > /dev/null
fi

echo "Environment setup complete"
