#!/bin/bash

set -eu
source ~/.bashrc
SITE_PACKAGES=$(python3 -c "import site; print(site.USER_SITE)")
python3 -m PyInstaller --name cli --onefile cli/__main__.py --add-data="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt:./shamir_mnemonic"