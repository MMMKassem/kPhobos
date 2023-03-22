FROM ubuntu:bionic

SHELL ["/bin/bash", "-c"]

RUN apt-get -y update
RUN apt-get -y install net-tools iputils-ping git xxd nano iproute2

ARG gh_url
RUN git clone $gh_url openairinterface5g

WORKDIR openairinterface5g/
ARG gh_branch
RUN git checkout $gh_branch
RUN source oaienv
WORKDIR cmake_targets/

# Build OAI eNB
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC ./build_oai -I
RUN ./build_oai --UE


# Configure eNB

WORKDIR ran_build/build/
COPY ue.conf .
COPY sim.conf .
COPY oai_ue.sh .
COPY execute_ue.sh .