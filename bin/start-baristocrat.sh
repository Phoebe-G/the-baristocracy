#!/bin/bash
source ./env
killall smartbar
echo "$BANNER"
sleep 2
nohup python ../src/baristocrat.py &>/dev/null &
