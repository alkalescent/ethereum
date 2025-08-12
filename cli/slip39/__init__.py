import slip39


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self):
        self.mnemo = slip39.recovery.Mnemonic()

    def deconstruct(self, mnemo: str) -> tuple[str, str]:
        """Deconstruct a mnemo into its shares."""
        _, shares = slip39.api.create("LEDGER", 1, {"KEYS": (
            2, 3)}, mnemo, using_bip39=True).groups["KEYS"]
        return shares

    def reconstruct(self, shares: list[str]) -> str:
        """Reconstruct multiple shares into a mnemo."""
        entropy = slip39.recovery.recover(
            shares, using_bip39=True, as_entropy=True)
        mnemo = self.mnemo.to_mnemonic(entropy)
        return mnemo
