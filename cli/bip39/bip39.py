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

    def download_words(self) -> None:
        """Download the BIP39 words file."""
        url = "https://raw.githubusercontent.com/bitcoin/bips/refs/heads/master/bip-0039/english.txt"
        response = requests.get(url)
        if response.ok:
            with open(self.FILE, "w") as file:
                file.write(response.content.decode())

    def check_words(self) -> bool:
        """Check if the words are present."""
        with open(self.FILE, "r") as file:
            words = file.read().splitlines()
            return len(words) == 2048 and all(len(word) > 0 for word in words)

    def ensure_words(self) -> None:
        """Ensure the words are present, downloading it if necessary."""
        if not (os.path.exists(self.FILE) and self.check_words()):
            self.download_words()
            if not self.check_words():
                raise RuntimeError(
                    "Failed to download or validate the BIP39 words.")

    def get_words(self) -> list[str]:
        """Get the BIP39 words."""
        self.ensure_words()
        with open(self.FILE, "r") as file:
            return file.read().splitlines()

    def generate(self, num_words: int) -> str:
        """Generate a mnemonic with the specified number of words."""
        return self.mnemo.generate(num_words)

    def check(self, mnemonic: str) -> bool:
        """Check if the mnemonic is valid."""
        return self.mnemo.check(mnemonic)

    def to_entropy(self, mnemonic: str) -> bytes:
        """Convert a mnemonic to its entropy."""
        return self.mnemo.to_entropy(mnemonic)


def get_words_map() -> dict[str, int]:
    """Get a dictionary for the BIP39 words."""
    words = get_words()
    return {word: index for index, word in enumerate(words)}


def generate_seed(num_words) -> list[str]:
    """Generate a random seed of BIP39 words."""
    mnemo = Mnemonic()
    words = mnemo.generate(num_words * 32 // 3)
    return words.split()


def xor_words(words: list[str]) -> str:
    """XOR a list of BIP39 words to get a single word."""
    map = get_words_map()
    idx = 0
    for word in words:
        idx ^= map[word]
    return get_words()[idx]


# Generate a 24 word mnemonic (Seed MASTER)
long_mnemonic = generate_seed(24)
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
