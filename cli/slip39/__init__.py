import slip39


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self):
        self.mnemo = slip39.recovery.Mnemonic()

    def deconstruct(self, seed: str) -> tuple[str, str]:
        """Deconstruct a seed into its shares."""
        _, shares = slip39.api.create("LEDGER", 1, {"KEYS": (
            2, 3)}, seed, using_bip39=True).groups["KEYS"]
        return shares

    def reconstruct(self, seed_one: str, seed_two: str) -> str:
        """Reconstruct multiple shares into a seed."""
        shares = [seed_one, seed_two]
        seed = slip39.recovery.recover(
            shares, using_bip39=True, as_entropy=True)
        reconstructed = self.mnemo.to_mnemonic(seed)
        return reconstructed
