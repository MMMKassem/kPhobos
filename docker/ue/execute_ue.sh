#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: ./execute_ue.sh <Data Plane command (quoted)>"
    exit 1
fi

# Export UE ID based on Hostname
export UE_ID=$((${HOSTNAME##*-} + 1))

# Run OAI UE
./oai_ue.sh $UE_ID &

# Loop until the oaitun_ue1 iface is created
while true; do
    ip route | grep "oaitun_ue1"
    if [ $? -eq 0 ]; then
        sleep 1  # network not yet up
    else
        break   # network up
    fi
done
sleep 1

# Execute the traffic command
$1