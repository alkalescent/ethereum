from .bip39 import BIP39
from .slip39 import SLIP39


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

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
bip_one, bip_two = cli.bip39.deconstruct(seed)
print("Deconstructed:", bip_one, bip_two)
slip_one = cli.slip39.deconstruct(bip_one)
print("SLIP39 Shares:", slip_one)
bip_one_reconstructed = cli.slip39.reconstruct(slip_one[0], slip_one[1])
print("Reconstructed BIP39:", bip_one_reconstructed)
slip_two = cli.slip39.deconstruct(bip_two)
print("SLIP39 Shares:", slip_two)
bip_two_reconstructed = cli.slip39.reconstruct(slip_two[0], slip_two[1])
print("Reconstructed BIP39:", bip_two_reconstructed)
seed_reconstructed = cli.bip39.reconstruct(
    bip_one_reconstructed, bip_two_reconstructed)
print("Reconstructed Mnemonic:", seed_reconstructed)
print("Match:", seed == seed_reconstructed)
