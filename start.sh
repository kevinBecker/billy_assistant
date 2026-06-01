#!/bin/bash

sleep 10

SCRIPT_DIR="/home/kjbecker00/billy_motor_ctl"

source $SCRIPT_DIR/.venv/bin/activate

python3 $SCRIPT_DIR/motor_test.py

python3 $SCRIPT_DIR/main.py &
