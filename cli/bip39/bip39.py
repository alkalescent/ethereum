import os
import secrets
import requests
from mnemonic import Mnemonic
# def get_seed(filename: str) -> bytes:
#     """Get the seed from a file."""
#     with open(filename, "rb") as f:
#         return f.read()


DIR = os.path.dirname(os.path.abspath(__file__))


def download_wordlist() -> None:
    """Download the BIP39 wordlist files."""
    url = "https://raw.githubusercontent.com/bitcoin/bips/refs/heads/master/bip-0039/english.txt"
    response = requests.get(url)
    if response.ok:
        with open(os.path.join(DIR, "wordlist.txt"), "w") as file:
            file.write(response.content.decode())


def check_wordlist() -> bool:
    """Check if the wordlist is present."""
    with open(os.path.join(DIR, "wordlist.txt"), "r") as file:
        words = file.read().splitlines()
        return len(words) == 2048 and all(len(word) > 0 for word in words)


def ensure_wordlist() -> None:
    """Ensure the wordlist is present, downloading it if necessary."""
    if not os.path.exists(os.path.join(DIR, "wordlist.txt")) or not check_wordlist():
        download_wordlist()
        if not check_wordlist():
            raise RuntimeError(
                "Failed to download or validate the BIP39 wordlist.")


def get_wordlist() -> list[str]:
    """Get the BIP39 wordlist."""
    ensure_wordlist()
    with open(os.path.join(DIR, "wordlist.txt"), "r") as file:
        return file.read().splitlines()


def get_wordlist_lookup() -> dict[str, int]:
    """Get a lookup dictionary for the BIP39 wordlist."""
    words = get_wordlist()
    return {word: index for index, word in enumerate(words)}


def generate_seed(num_words) -> list[str]:
    """Generate a random seed of BIP39 words."""
    ensure_wordlist()
    words = get_wordlist()
    return [secrets.choice(words) for _ in range(num_words)]


# idx = get_wordlist_lookup()['zoo']
# print('legal idx: ', idx)
# print('legal bin: ', bin(idx))
# print('legal hex: ', hex(idx))
lookup = get_wordlist_lookup()
idx1 = lookup['romance']
idx2 = lookup['lion']
idx3 = lookup['vault']
idx = idx1 ^ idx2 ^ idx3
print('idx: ', idx)
print('hex: ', hex(idx))
print('word: ', get_wordlist()[idx])
