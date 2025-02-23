#!/bin/bash

set -eu
source config.env

docker build \
    -t ethereum \
    --network=host \
    --secret id=NORDVPN,env=NORDVPN \
    --build-arg DEPLOY_ENV=prod \
    --build-arg ARCH=amd64 \
    --build-arg \
    VPN=true \
    .
