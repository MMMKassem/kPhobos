#!/bin/bash

if [ ! -f /local/repository/core-ready ]; then
    echo "The Core setup has not finished. Please wait"
    exit 0
fi

if [ -f /local/repository/open5gs-setup-complete ]; then
    echo "Running Open5GS..."
    sudo /local/repository/open5gs/build/tests/app/epc -c /local/repository/config/core/config.yaml
    exit 0
fi

if [ -f /local/repository/srsepc-setup-complete ]; then
    echo "Running srsEPC..."
    cd /local/repository/config/core/
    sudo srsepc epc.conf
    exit 0
fi