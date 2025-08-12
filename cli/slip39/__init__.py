import slip39


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self):
        # self.mnemo = slip39

    def generate(self, num_words: int) -> list[str]:
        """Generate a random SLIP39 seed of words."""
        return self.mnemo.generate(num_words)

    def deconstruct(self, seed: str) -> tuple[str, str]:
        """Deconstruct a seed into its components."""
        if not self.mnemo.check(seed):
            raise ValueError("Invalid SLIP39 seed.")
        return self.mnemo.deconstruct(seed)

    def reconstruct(self, seed_one: str, seed_two: str) -> str:
        """Reconstruct the original SLIP39 seed from two parts."""
        return self.mnemo.reconstruct(seed_one, seed_two)
