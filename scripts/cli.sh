#!/bin/bash

set -eu
cd cli
SITE_PACKAGES=$(uv run python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))")
uv run pyinstaller --onefile --name cli --distpath ../dist __main__.py
echo "User site-packages directory: $SITE_PACKAGES"

# python3 -m PyInstaller --name cli --onefile cli/__main__.py --add-data="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt:./shamir_mnemonic"