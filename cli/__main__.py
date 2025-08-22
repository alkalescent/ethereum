import typer
from cli.tools import BIP39, SLIP39


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def get_mnemo(self, filename: str) -> bytes:
        """Get the mnemo from a file."""
        with open(filename, "r") as f:
            return f.read()


cli = CLI()
mnemo = cli.get_mnemo("seed.txt")
print("Mnemonic:", mnemo)
addr = cli.bip39.eth(mnemo)
print("Eth Addr:", addr)
bip_one, bip_two = cli.bip39.deconstruct(mnemo)
print("Deconstructed:", bip_one, bip_two)
slip_one = cli.slip39.deconstruct(bip_one)
print("SLIP39 Shares:", slip_one)
bip_one_reconstructed = cli.slip39.reconstruct(slip_one)
print("Reconstructed BIP39:", bip_one_reconstructed)
slip_two = cli.slip39.deconstruct(bip_two)
print("SLIP39 Shares:", slip_two)
bip_two_reconstructed = cli.slip39.reconstruct(slip_two)
print("Reconstructed BIP39:", bip_two_reconstructed)
mnemo_reconstructed = cli.bip39.reconstruct(
    [bip_one_reconstructed, bip_two_reconstructed])
print("Reconstructed Mnemonic:", mnemo_reconstructed)
print("Match:", mnemo == mnemo_reconstructed)

# python3 -m PyInstaller --name cli --onefile --paths cli cli/__main__.py
# python3 -m PyInstaller --name cli --onefile cli/__main__.py --add-data="/Users/suchak/Library/Python/3.9/lib/python/site-packages/shamir_mnemonic/wordlist.txt:./shamir_mnemonic"
# ./dist/cli
