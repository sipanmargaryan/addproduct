#!/usr/bin/env bash
# Extract python packages from virtual environment
cp -r  "`pipenv --venv`/lib/python3.6/site-packages" /host