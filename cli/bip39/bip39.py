import os
import secrets
import requests
from mnemonic import Mnemonic
# def get_seed(filename: str) -> bytes:
#     """Get the seed from a file."""
#     with open(filename, "rb") as f:
#         return f.read()


DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = "words.txt"
FILE = os.path.join(DIR, FILENAME)


def download_words() -> None:
    """Download the BIP39 words file."""
    url = "https://raw.githubusercontent.com/bitcoin/bips/refs/heads/master/bip-0039/english.txt"
    response = requests.get(url)
    if response.ok:
        with open(FILE, "w") as file:
            file.write(response.content.decode())


def check_words() -> bool:
    """Check if the words is present."""
    with open(FILE, "r") as file:
        words = file.read().splitlines()
        return len(words) == 2048 and all(len(word) > 0 for word in words)


def ensure_words() -> None:
    """Ensure the words is present, downloading it if necessary."""
    if not os.path.exists(FILE) or not check_words():
        download_words()
        if not check_words():
            raise RuntimeError(
                "Failed to download or validate the BIP39 words.")


def get_words() -> list[str]:
    """Get the BIP39 words."""
    ensure_words()
    with open(FILE, "r") as file:
        return file.read().splitlines()


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
# Check if the mnemonic is valid
mnemo = Mnemonic()
is_valid = mnemo.check(long_mnemonic_str)
print("Is the mnemonic valid?", is_valid)

# Generate a 12 word mnemonic (Seed A)
short_mnemonic = generate_seed(12)
short_mnemonic_str = " ".join(short_mnemonic)
print("Generated 12-word mnemonic:", short_mnemonic_str)
# Check if the mnemonic is valid
is_valid = mnemo.check(short_mnemonic_str)
print("Is the mnemonic valid?", is_valid)

# XOR a new short mnemonic (Seed B)
# len of long mnemonic
master_mnemonic = long_mnemonic[-len(short_mnemonic):]
master_mnemonic_str = " ".join(master_mnemonic)
print("Master mnemonic for XOR:", master_mnemonic_str)

# Check if the master mnemonic is valid
is_valid = mnemo.check(master_mnemonic_str)
print("Is the master mnemonic valid?", is_valid)

xor_result = []
for idx, word in enumerate(master_mnemonic):
    xor_result.append(xor_words([word, short_mnemonic[idx]]))

xor_result_str = " ".join(xor_result)
print("XOR result:", xor_result_str)

# Check if the XOR result is valid
is_valid = mnemo.check(xor_result_str)
print("Is the XOR result valid?", is_valid)
# On average, the XOR result will be invalid.
# However, there exists a short mnemonic that can be XORed with the master mnemonic to produce a valid mnemonic.


# # idx = get_words_map()['zoo']
# # print('legal idx: ', idx)
# # print('legal bin: ', bin(idx))
# # print('legal hex: ', hex(idx))
# map = get_words_map()
# idx1 = map['romance']
# idx2 = map['lion']
# idx3 = map['vault']
# idx = idx1 ^ idx2 ^ idx3
# print('idx: ', idx)
# print('hex: ', hex(idx))
# print('word: ', get_words()[idx])

# print('xor: ', xor_words(['romance', 'lion', 'vault']))

# seed = generate_seed(12)
# print('seed words: ', seed)
# print('seed check: ', Mnemonic().check(seed))
# print('seed: ', Mnemonic().to_seed(seed))
# random_words = " ".join(secrets.choice(get_words()) for _ in range(24))
# print('random words: ', random_words)
# print('seed check: ', Mnemonic().check(random_words))
# # print('seed: ', Mnemonic().to_seed(
# #     "".join(secrets.choice(get_words()) for _ in range(24))))
