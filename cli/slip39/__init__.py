import slip39


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self):
        # self.mnemo = slip39
        pass

    def deconstruct(self, seed: str) -> tuple[str, str]:
        """Deconstruct a seed into its shares."""
        return slip39.api.mnemonics(1, [(2, 3)], seed)  # create or mnemonics

    def reconstruct(self, seed_one: str, seed_two: str) -> str:
        """Reconstruct multiple shares into a seed."""
        return self.mnemo.reconstruct(seed_one, seed_two)
