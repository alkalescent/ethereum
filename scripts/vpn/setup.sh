#!/bin/bash

set -eu

VPN="${VPN:-false}"

if [[ "${VPN}" = "true" ]]
then
    apt-get update && apt-get install -y openvpn ca-certificates
    mkdir -p config
    cd config
    python3 scripts/vpn/download.py
    cd ..
fi
