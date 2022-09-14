#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "USE: sudo ./run_ues.sh <Number of UEs> <Traffic Commands (quoted)>"
    echo "[Example] Run two UEs that ping the SPGW"
    echo '    sudo ./run_ues.sh 2 "ping -I oaitun_ue1 172.16.0.1"'
    exit 1
fi

helm install \
    --set-string num_ues=$1 \
    --set-string ue_command="$2" \
    multi-ue .