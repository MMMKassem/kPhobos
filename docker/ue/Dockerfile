FROM ubuntu:bionic

SHELL ["/bin/bash", "-c"]

RUN apt-get -y update
RUN apt-get -y install net-tools iputils-ping git xxd nano

ARG token
RUN git clone https://j0lama:$token@github.com/j0lama/openairinterface5g.git

WORKDIR openairinterface5g/
RUN source oaienv
WORKDIR cmake_targets/

# Build OAI eNB
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC ./build_oai -I
RUN ./build_oai --UE


# Configure eNB

WORKDIR ran_build/build/
COPY ue.conf .
COPY sim.conf .
COPY run_ue.sh .