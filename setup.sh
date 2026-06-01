#!/bin/bash

##################################
# Only run from this directory
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
cd "$SCRIPT_DIR"


##################################
# Python installs
# lgpio only works if installed system-wide. Wipe old .venv first to prevent issues
deactivate
rm -rf .venv
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install websockets adafruit-circuitpython-motorkit adafruit-circuitpython-busdevice

##################################
# Enable I2C
sudo raspi-config nonint do_i2c 0
sudo modprobe i2c-dev
