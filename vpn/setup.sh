#!/bin/bash

set -eu

VPN="${VPN:-false}"

if [[ "${VPN}" = "true" ]]
then
    apt-get update && apt-get install -y ca-certificates
    yes | sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
    echo NordVPN installed
    # /etc/init.d/nordvpn start
    # echo NordVPN service started
    # nordvpn login --token "${NORDVPN}"
    # echo Logged into NordVPN
fi
