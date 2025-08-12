from hdwallet import HDWallet
from hdwallet.symbols import ETH
from bip39 import BIP39


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()

    def get_seed(self, filename: str) -> bytes:
        """Get the seed from a file."""
        with open(filename, "r") as f:
            return f.read()

    # def generate_mnemonic(self, num_words: int) -> str:
    #     """Generate a BIP39 mnemonic with the specified number of words."""
    #     return self.bip39.generate(num_words)

    # def validate_mnemonic(self, mnemonic: str) -> bool:
    #     """Validate a given BIP39 mnemonic."""
    #     return self.bip39.validate(mnemonic)

    # def reconstruct_mnemonic(self, seed_one: str, seed_two: str) -> str:
    #     """Reconstruct a BIP39 mnemonic from two parts."""
    #     return self.bip39.reconstruct(seed_one, seed_two)


cli = CLI()
seed = cli.get_seed("seed.txt")
print("Mnemonic:", seed)
eth = cli.bip39.eth(seed)
print("Eth Addr:", eth)
deconstructed = cli.bip39.deconstruct(seed)
print("Deconstructed:", deconstructed)
