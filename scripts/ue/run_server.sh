#!/bin/bash

cd /local/repository/scripts/ue/files
python3 -m http.server 8000 --bind 10.10.0.1
#python3 -m uploadserver 8000 --bind 10.10.0.1