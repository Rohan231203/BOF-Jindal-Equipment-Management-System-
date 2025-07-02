#!/bin/bash

# Exit on error
set -e

# Install packages with pip using binary wheels
pip install --upgrade pip
pip install --only-binary=:all: pillow==9.0.1
pip install --only-binary=:all: pandas==1.3.5
pip install -r requirements.txt
