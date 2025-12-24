#!/bin/bash

set -eu
cd cli
uv run python3 -m nuitka \
  --onefile \
  --output-filename=cli \
  --output-dir=../dist \
  --include-data-files="$(uv run python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))")/shamir_mnemonic/wordlist.txt=./shamir_mnemonic/wordlist.txt" \
  --remove-output \
  --assume-yes-for-downloads \
  cli.py