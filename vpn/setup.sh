#!/bin/bash

set -eu

VPN="${VPN:-false}"

if [[ "${VPN}" = "true" ]]
then
    apt-get update && apt-get install -y ca-certificates
    # sudo wget https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
    sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
    python3 vpn/download.py
fi
