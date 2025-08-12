import os
import requests
from hdwallet import HDWallet
from hdwallet.symbols import ETH
from hdwallet.cryptocurrencies import EthereumMainnet
from mnemonic import Mnemonic


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

    def _make(self, words: list[str]) -> dict[str, int]:
        """Make a dictionary for the BIP39 words."""
        return {word: index for index, word in enumerate(words)}

    def generate(self, num_words: int) -> list[str]:
        """Generate a random seed of BIP39 words."""
        words = self.mnemo.generate(num_words * 32 // 3)
        return words

    def xor(self, words: str) -> str:
        """XOR a list of BIP39 words to get a single word."""
        if isinstance(words, str):
            words = words.split()
        idx = 0
        for word in words:
            idx ^= self.map[word]
        return self.words[idx]

    def reconstruct(self, mnemos: list[str]) -> str:
        """Reconstruct a seed from its components."""
        entropy = b''.join([self.mnemo.to_entropy(mnemo) for mnemo in mnemos])
        mnemo = self.mnemo.to_mnemonic(entropy)
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 seed after reconstruction.")
        return mnemo

    def deconstruct(self, seed: str) -> list[str]:
        """Deconstruct a seed into its components."""
        # Check if the seed is valid
        if not self.mnemo.check(seed):
            raise ValueError("Invalid BIP39 seed.")
        # Convert the seed to entropy
        entropy = self.mnemo.to_entropy(seed)
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
        return [seed_one, seed_two]

    def eth(self, seed: str) -> HDWallet:
        return HDWallet(
            symbol=ETH,
            cryptocurrency=EthereumMainnet
        ).from_mnemonic(seed).p2pkh_address()


bip39 = BIP39()
# Generate a 24 word mnemonic
seed = bip39.generate(24)
# Check that the reconstruction is correct
assert seed == bip39.reconstruct(bip39.deconstruct(seed))
