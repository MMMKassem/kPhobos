#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: sudo ./ue_run.sh <UE MSIN>"
    exit 1
fi

if [ ! -f /local/repository/ue-setup-complete ]; then
    echo "The UE setup has not finished. Please wait"
    exit 0
fi

cd /local/repository/openairinterface5g/cmake_targets/

####### Network isolation #######
# Create namespace
sudo ip netns add ue$1

# Creating veth pair
sudo ip link add veth_gw_$1 type veth peer name veth$1

# Move the veth iface to the namespace
sudo ip link set veth$1 netns ue$1

# Assigning IPs to the veth devices
sudo ip addr add 1.1.$1.1/24 dev veth_gw_$1 # Gateway interface
sudo ip netns exec ue$1 ip addr add 1.1.$1.2/24 dev veth$1 # Namespace interface

# Bring interfaces up
sudo ip link set veth_gw_$1 up
sudo ip netns exec ue$1 ip link set veth$1 up

# Enable IPv4 packet forwarding
sudo sysctl -w net.ipv4.ip_forward=1

FRONTHAUL_IFACE=$(ip route list 192.168.2.3/24 | awk '{print $3}') # Get fronthaul network interface
# Create a NAT for the namespace
sudo iptables -t nat -A POSTROUTING -s 1.1.$1.0/24 -o $FRONTHAUL_IFACE -j MASQUERADE

# Add packet forwaring rules
sudo iptables -A FORWARD -o $FRONTHAUL_IFACE -i veth_gw_$1 -j ACCEPT
sudo iptables -A FORWARD -i $FRONTHAUL_IFACE -o veth_gw_$1 -j ACCEPT

# Add default gateway to the namespace
sudo ip netns exec ue$1 ip route add default via 1.1.$1.1


# Configure UE configuration file (IP and iface name)
cp /local/repository/config/ran/ue.conf /local/repository/config/ran/ue_$1.conf
sed -i "s/FRONTHAUL_IFACE/veth$1/g" /local/repository/config/ran/ue_$1.conf
sed -i "s/VETH_IP/1.1.$1.2/g" /local/repository/config/ran/ue_$1.conf

# Run UE inside namespace
cp /local/repository/scripts/ran/ue_ns.sh /local/repository/openairinterface5g/cmake_targets/
sudo ip netns exec ue$1 ./ue_ns.sh $1