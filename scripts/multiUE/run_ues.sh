#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: sudo ./run_ues.sh <Number of UEs> <Traffic Commands (quoted)>"
    echo "[Example] Run two UEs that ping the SPGW"
    echo '    sudo ./run_ues.sh 2 "ping -I oaitun_ue1 172.16.0.1"'
    exit 1
fi

helm install multi-ue .