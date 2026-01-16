#!/bin/bash

set -eu

# Checkpoint sync hosts (ethpandaops - official testnet provider)
# Hoodi: https://checkpoint-sync.hoodi.ethpandaops.io
# Mainnet: https://sync.invis.tools (ethpandaops doesn't run mainnet)

# ethstaker.cc alternatives (may have issues post-Fusaka):
# Hoodi: https://hoodi.beaconstate.ethstaker.cc
# Mainnet: https://beaconstate.ethstaker.cc

# Default deploy env for app code should be prod
DEPLOY_ENV="${DEPLOY_ENV:-prod}"

if [[ "${DEPLOY_ENV}" = "dev" ]]
then
    # Hoodi testnet - ethpandaops is official provider
    NODE_HOST="https://checkpoint-sync.hoodi.ethpandaops.io"
    curl -LO https://github.com/eth-clients/hoodi/raw/main/metadata/genesis.ssz
else
    # Mainnet - use ethstaker.cc (reliable, community maintained)
    NODE_HOST="https://beaconstate.ethstaker.cc"
fi

prysmctl checkpoint-sync download --beacon-node-host="${NODE_HOST}"
