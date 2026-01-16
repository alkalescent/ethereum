#!/bin/bash

set -eu

# Hoodi hosts
# https://hoodi.beaconstate.ethstaker.cc

# Mainnet hosts
# https://beaconstate.ethstaker.cc

# Default deploy env for app code should be prod
DEPLOY_ENV="${DEPLOY_ENV:-prod}"

if [[ "${DEPLOY_ENV}" = "dev" ]]
then
    NODE_HOST="https://hoodi.beaconstate.ethstaker.cc"
    curl -LO https://github.com/eth-clients/hoodi/raw/main/metadata/genesis.ssz
else
    NODE_HOST="https://beaconstate.ethstaker.cc"
fi

prysmctl checkpoint-sync download --beacon-node-host="${NODE_HOST}"
