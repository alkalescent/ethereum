#!/bin/bash

set -eu
cd cli
SITE_PACKAGES=$(uv run python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))")
# uv tool install pyinstaller 
uv run pyinstaller --onefile --name cli --distpath ../dist --add-data="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt:./shamir_mnemonic" __main__.py
# python3 -m PyInstaller --name cli --onefile cli/__main__.py --add-data="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt:./shamir_mnemonic"
cd ..
./dist/cli