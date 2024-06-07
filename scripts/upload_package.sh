#!/usr/bin/env bash

PYPI_PROJECT_NAME=https://upload.pypi.org/legacy/

python3 -m pip install --upgrade twine
python3 -m twine upload -u $1 -p $2 --repository-url $PYPI_PROJECT_NAME dist/*