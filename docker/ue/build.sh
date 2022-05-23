#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "USE: sudo ./build.sh <GitHub Token>"
    exit 1
fi

docker build --build-arg token=$1 -t j0lama/oaiue:latest .