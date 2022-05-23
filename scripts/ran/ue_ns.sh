#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: ./ue_ns.sh <UE MSIN>"
    exit 1
fi

cd ../
source oaienv
cd cmake_targets/ran_build/build/

# Generate MSIN based on the ID
MSIN=$(printf "%010d" $1)

# Configure SIM card
cp /local/repository/config/ran/sim.conf /local/repository/config/ran/tmp_sim.conf # Create a copy of the configuration file
sed -i "s/CUSTOM_MSIN/$MSIN/g" /local/repository/config/ran/tmp_sim.conf # Add the MSIN
../../../targets/bin/conf2uedata -c /local/repository/config/ran/tmp_sim.conf -o . # Compile 
../../../targets/bin/usim -g -c /local/repository/config/ran/tmp_sim.conf -o . # Compile
../../../targets/bin/nvram -g -c /local/repository/config/ran/tmp_sim.conf -o . # Compile
rm /local/repository/config/ran/tmp_sim.conf # Remove SIM config file copy

num="$(($1+1))"
./lte-uesoftmodem -O /local/repository/config/ran/ue_$1.conf --L2-emul 5 --nokrnmod 1 --node-number $num --log_config.global_log_options level,nocolor,time,thread_id | tee /local/repository/ue_$1.log 2>&1