#!/bin/bash

if [ -f /local/repository/core-setup-complete ]; then
    echo "Core setup already ran; not running again"
    exit 0
fi

# Move to repository folder
cd /local/repository

# Install srsEPC
sudo apt -y update
sudo add-apt-repository -y ppa:softwareradiosystems/srsran
sudo apt -y update
sudo apt-get install srsran -y

# Configure the network
sudo srsepc_if_masq.sh eno1

touch /local/repository/core-ready
touch /local/repository/srsepc-setup-complete