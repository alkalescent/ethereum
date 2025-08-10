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
    return words


def xor_words(words: list[str]) -> str:
    """XOR a list of BIP39 words to get a single word."""
    map = get_words_map()
    idx = 0
    for word in words:
        idx ^= map[word]
    return get_words()[idx]


# idx = get_words_map()['zoo']
# print('legal idx: ', idx)
# print('legal bin: ', bin(idx))
# print('legal hex: ', hex(idx))
map = get_words_map()
idx1 = map['romance']
idx2 = map['lion']
idx3 = map['vault']
idx = idx1 ^ idx2 ^ idx3
print('idx: ', idx)
print('hex: ', hex(idx))
print('word: ', get_words()[idx])

print('xor: ', xor_words(['romance', 'lion', 'vault']))

seed = generate_seed(12)
print('seed words: ', seed)
print('seed check: ', Mnemonic().check(seed))
print('seed: ', Mnemonic().to_seed(seed))
random_words = " ".join(secrets.choice(get_words()) for _ in range(24))
print('random words: ', random_words)
print('seed check: ', Mnemonic().check(random_words))
# print('seed: ', Mnemonic().to_seed(
#     "".join(secrets.choice(get_words()) for _ in range(24))))
