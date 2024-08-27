#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: sudo ./proxy_setup.sh <GitHub Token>"
    exit 1
fi

if [ -f /local/repository/proxy-setup-complete ]; then
    echo "Proxy setup already ran; not running again"
    exit 0
fi

# Install dependencies
sudo apt -y update
sudo apt -y install libsctp-dev

# Move to repository folder
cd /local/repository

# Clone proxy
git clone https://ujjwalpawar:$1@github.com/ujjwalpawar/proxy.git
cd proxy/

# Compile proxy
make

# Install byobu
sudo apt install byobu

# 
filename=/local/repository/config/ran/enb_ips.conf
> $filename
for ((i=1;i<=$1;i++)); do
    printf "192.168.1.%d\n" $(($i+1)) >> $filename
done

touch /local/repository/proxy-setup-complete
