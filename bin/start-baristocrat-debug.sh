#!/bin/bash
source ./env
killall smartbar &
echo "$BANNER"
sleep 2
python ../src/baristocrat.py
