#!/bin/bash

# Exit on error
set -e

# Print Python version
python --version

# Install minimal dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Replace main.py with deployment version
cp main_deploy.py main.py

# Use deployment data file if main one doesn't exist
if [ ! -f "motor_data.json" ]; then
  echo "Using deployment data file"
  cp motor_data_deploy.json motor_data.json
fi

# Create empty QR folder for static file serving
mkdir -p qr_codes
