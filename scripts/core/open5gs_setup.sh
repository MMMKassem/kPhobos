#!/bin/bash

# Move to repository folder
cd /local/repository

# Install Mongo
curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

sudo apt-get update

sudo apt-get install mongodb-org -y

mongod --version

sudo systemctl start mongod

sudo systemctl enable mongod

sudo systemctl status mongod

# Install dependencies
sudo apt -y install python3-pip python3-setuptools python3-wheel ninja-build build-essential flex bison git libsctp-dev libgnutls28-dev libgcrypt-dev libssl-dev libidn11-dev libmongoc-dev libbson-dev libyaml-dev libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev libnghttp2-dev libtins-dev libtalloc-dev meson

# Clone Open5GS
git clone https://github.com/open5gs/open5gs

# Compile Open5GS
cd open5gs
git checkout 85f150c
meson build --prefix=`pwd`/install
ninja -C build

# Configure TUN device
sudo ./misc/netconf.sh

# Configure IP Tables (Only IPv4)
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE

# Add Users
for i in $(seq -f "%010g" 1 500)
do
	/local/repository/open5gs/misc/db/open5gs-dbctl add 20893$i 00001111222233334444555566667777 88889999AAAABBBBCCCCDDDDEEEEFFFF
done

# Install byobu
sudo apt install byobu 
touch /local/repository/core-ready
touch /local/repository/open5gs-setup-complete
