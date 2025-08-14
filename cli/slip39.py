import slip39 as s


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self):
        self.mnemo = s.recovery.Mnemonic()

    def deconstruct(self, mnemo: str) -> tuple[str, str]:
        """Deconstruct a mnemo into its shares."""
        _, shares = s.api.create("LEDGER", 1, {"KEYS": (
            2, 3)}, mnemo, using_bip39=True).groups["KEYS"]
        return shares

    def reconstruct(self, shares: list[str]) -> str:
        """Reconstruct multiple shares into a mnemo."""
        entropy = s.recovery.recover(
            shares, using_bip39=True, as_entropy=True)
        mnemo = self.mnemo.to_mnemonic(entropy)
        return mnemo


slip39 = SLIP39()
# Generate a 24 word mnemonic
mnemo = slip39.mnemo.generate(256)
# Check that the reconstruction is correct
assert mnemo == slip39.reconstruct(slip39.deconstruct(mnemo))
