#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "USE: ./oai_ue.sh <UE ID (starting at 1)> <Proxy IP> <Handover CSV File>"
    exit 1
fi

UE_ID=$1
PROXY_IP=$2
HANDOVER_CSV_FILE=$3

cd ../../../
source oaienv
cd cmake_targets/ran_build/build/

# Modify the configuration file
UE_IP_ADDR=$(ifconfig eth0 | grep 'inet ' | awk '{ print $2 }')
sed -i "s/ue_addr/$UE_IP_ADDR/g" ue.conf
sed -i "s/proxy_addr/$PROXY_IP/g" ue.conf

cp sim.conf tmp_sim.conf
sed -i "s/CUSTOM_MSIN/$(printf "%010d" $1)/g" tmp_sim.conf # Add the MSIN
../../../targets/bin/conf2uedata -c tmp_sim.conf -o . # Compile SIM
../../../targets/bin/usim -g -c tmp_sim.conf -o .
../../../targets/bin/nvram -g -c tmp_sim.conf -o .
rm tmp_sim.conf

num="$(($UE_ID-1))"
./lte-uesoftmodem -O ue.conf --L2-emul 5 --nokrnmod 1 --num-ues 1 --node-number 1 --num-enbs 1 --log_config.global_log_options level,nocolor,time,thread_id --log_config.global_log_level error $num $HANDOVER_CSV_FILE | tee ~/$folder/UE.log 2>&1