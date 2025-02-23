#!/bin/bash

set -eu

VPN="${VPN:-false}"

if [[ "${VPN}" = "true" ]]
then
    apt-get update && apt-get install -y ca-certificates
    # https://support.nordvpn.com/hc/en-us/articles/20164827795345-Connect-to-NordVPN-using-Linux-Terminal
    # sudo wget https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
    sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
    python3 vpn/download.py
fi
