import os
import requests
from mnemonic import Mnemonic
# def get_seed(filename: str) -> bytes:
#     """Get the seed from a file."""
#     with open(filename, "rb") as f:
#         return f.read()


class BIP39:
    """BIP39 class to handle mnemonic generation and validation."""

    def __init__(self):
        DIR = os.path.dirname(os.path.abspath(__file__))
        FILENAME = "words.txt"
        FILE = os.path.join(DIR, FILENAME)
        self.FILE = FILE
        self.mnemo = Mnemonic()
        self.words = self._get()
        self.map = self._make(self.words)

    def _download(self) -> None:
        """Download the BIP39 words file."""
        url = "https://raw.githubusercontent.com/bitcoin/bips/refs/heads/master/bip-0039/english.txt"
        response = requests.get(url)
        if response.ok:
            with open(self.FILE, "w") as file:
                file.write(response.content.decode())

    def _check(self) -> bool:
        """Check if the words are present."""
        with open(self.FILE, "r") as file:
            words = file.read().splitlines()
            return len(words) == 2048 and all(len(word) > 0 for word in words)

    def _ensure(self) -> None:
        """Ensure the words are present, downloading it if necessary."""
        if not (os.path.exists(self.FILE) and self._check()):
            self._download()
            if not self._check():
                raise RuntimeError(
                    "Failed to download or validate the BIP39 words.")

    def _get(self) -> list[str]:
        """Get the BIP39 words."""
        self._ensure()
        with open(self.FILE, "r") as file:
            return file.read().splitlines()

    def _make(self, words) -> dict[str, int]:
        """Make a dictionary for the BIP39 words."""
        return {word: index for index, word in enumerate(words)}

    def generate(self, num_words) -> list[str]:
        """Generate a random seed of BIP39 words."""
        words = self.mnemo.generate(num_words * 32 // 3)
        return words.split()

    def xor(self, words: list[str]) -> str:
        """XOR a list of BIP39 words to get a single word."""
        idx = 0
        for word in words:
            idx ^= self.map[word]
        return self.words[idx]

    def reconstruct() -> None:
        pass

    def deconstruct(self, seed) -> None:
        """Deconstruct a seed into its components."""
        seed_str = " ".join(seed)
        # Check if the seed is valid
        if not self.mnemo.check(seed_str):
            raise ValueError("Invalid BIP39 seed.")
        # Convert the seed to entropy
        entropy = self.mnemo.to_entropy(seed_str)
        # Split the entropy into two parts
        half = len(entropy) // 2
        one = entropy[:half]
        two = entropy[half:]
        # Convert each part back to a mnemonic
        seed_one = self.mnemo.to_mnemonic(one)
        seed_two = self.mnemo.to_mnemonic(two)
        # Check if the mnemonics are valid
        if not (self.mnemo.check(seed_one) and self.mnemo.check(seed_two)):
            raise ValueError("Invalid BIP39 mnemonics after deconstruction.")
        return seed_one, seed_two

    # def check(self, mnemonic: str) -> bool:
    #     """Check if the mnemonic is valid."""
    #     return self.mnemo.check(mnemonic)

    # def to_entropy(self, mnemonic: str) -> bytes:
    #     """Convert a mnemonic to its entropy."""
    #     return self.mnemo.to_entropy(mnemonic)


bip39 = BIP39()
# Generate a 24 word mnemonic (Seed MASTER)
long_mnemonic = bip39.generate(24)
long_mnemonic_str = " ".join(long_mnemonic)
print("Generated 24-word mnemonic:", long_mnemonic_str)
# # Check if the mnemonic is valid
mnemo = Mnemonic()
# is_valid = mnemo.check(long_mnemonic_str)
# print("Is the mnemonic valid?", is_valid)

# # Generate a 12 word mnemonic (Seed A)
# short_mnemonic = generate_seed(12)
# short_mnemonic_str = " ".join(short_mnemonic)
# print("Generated 12-word mnemonic:", short_mnemonic_str)
# # Check if the mnemonic is valid
# is_valid = mnemo.check(short_mnemonic_str)
# print("Is the mnemonic valid?", is_valid)

# # XOR a new short mnemonic (Seed B)
# # len of long mnemonic
# master_mnemonic = long_mnemonic[-len(short_mnemonic):]
# master_mnemonic_str = " ".join(master_mnemonic)
# print("Master mnemonic for XOR:", master_mnemonic_str)

# # Check if the master mnemonic is valid
# is_valid = mnemo.check(master_mnemonic_str)
# print("Is the master mnemonic valid?", is_valid)

# xor_result = []
# for idx, word in enumerate(master_mnemonic):
#     xor_result.append(xor_words([word, short_mnemonic[idx]]))

# xor_result_str = " ".join(xor_result)
# print("XOR result:", xor_result_str)

# # Check if the XOR result is valid
# is_valid = mnemo.check(xor_result_str)
# print("Is the XOR result valid?", is_valid)
# # On average, the XOR result will be invalid.
# # However, there exists a short mnemonic that can be XORed with the master mnemonic to produce a valid mnemonic.

# Convert the 24-word seed to its 256-bit (32-byte) entropy
long_entropy = mnemo.to_entropy(long_mnemonic_str)

# Split the 32-byte entropy into two 16-byte (128-bit) halves
entropy_part_1 = long_entropy[:16]
entropy_part_2 = long_entropy[16:]

# Convert each 128-bit entropy half into a new, valid 12-word seed phrase
seed_part_1 = mnemo.to_mnemonic(entropy_part_1)
seed_part_2 = mnemo.to_mnemonic(entropy_part_2)

# Print the two 12-word seed phrases
print("Seed Part 1 (12 words):", seed_part_1)
print("Seed Part 2 (12 words):", seed_part_2)

# Check if the two 12-word seed phrases are valid
is_valid_part_1 = mnemo.check(seed_part_1)
is_valid_part_2 = mnemo.check(seed_part_2)
print("Is Seed Part 1 valid?", is_valid_part_1)
print("Is Seed Part 2 valid?", is_valid_part_2)

# Convert the two 12-word parts back to their entropy
recovered_entropy_1 = mnemo.to_entropy(seed_part_1)
recovered_entropy_2 = mnemo.to_entropy(seed_part_2)

# Concatenate (join) the two entropy halves
reconstructed_master_entropy = recovered_entropy_1 + recovered_entropy_2

# Convert the full 256-bit entropy back to the master seed phrase
reconstructed_master_seed = mnemo.to_mnemonic(reconstructed_master_entropy)
print("Reconstructed Master Seed (24 words):", reconstructed_master_seed)

# Check if the reconstructed master seed is valid
is_reconstructed_valid = mnemo.check(reconstructed_master_seed)
print("Is the reconstructed master seed valid?", is_reconstructed_valid)
