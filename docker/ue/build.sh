#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: sudo ./build.sh <GitHub URL> <GitHub Branch>"
    exit 1
fi

docker build \
    --build-arg gh_url=$1 \
    --build-arg gh_branch=$2 \
    -t andrewferguson/phobos-ue:latest .
