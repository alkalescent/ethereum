import pytest
from cli.tools import BIP39, SLIP39


class TestBIP39:
    """Test BIP39 mnemonic generation and validation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.bip39 = BIP39()

    def test_generate_12_words(self):
        """Test generating a 12-word mnemonic."""
        mnemo = self.bip39.generate(12)
        words = mnemo.split()
        assert len(words) == 12
        assert self.bip39.mnemo.check(mnemo)

    def test_generate_24_words(self):
        """Test generating a 24-word mnemonic."""
        mnemo = self.bip39.generate(24)
        words = mnemo.split()
        assert len(words) == 24
        assert self.bip39.mnemo.check(mnemo)

    def test_deconstruct_reconstruct_24_words(self):
        """Test deconstructing and reconstructing a 24-word mnemonic."""
        mnemo = self.bip39.generate(24)
        parts = self.bip39.deconstruct(mnemo, split=2)

        assert len(parts) == 2
        assert all(self.bip39.mnemo.check(part) for part in parts)

        reconstructed = self.bip39.reconstruct(parts)
        assert reconstructed == mnemo

    def test_deconstruct_requires_valid_entropy_size(self):
        """Test that 12-word mnemonic cannot be split into 2 parts (8-byte entropy is invalid)."""
        mnemo = self.bip39.generate(12)
        # 12-word mnemonic has 16 bytes of entropy, splitting gives 8 bytes each
        # which is not a valid BIP39 entropy size (must be 16, 20, 24, 28, or 32)
        with pytest.raises(ValueError):
            self.bip39.deconstruct(mnemo, split=2)

    def test_invalid_mnemonic_deconstruct(self):
        """Test that invalid mnemonic raises error on deconstruct."""
        invalid_mnemo = "invalid mnemonic phrase here test fail bad"
        with pytest.raises(ValueError, match="Invalid BIP39 mnemo"):
            self.bip39.deconstruct(invalid_mnemo)

    def test_wordlist_properties(self):
        """Test BIP39 wordlist has correct properties."""
        assert len(self.bip39.words) == 2048
        assert self.bip39.words == sorted(self.bip39.words)
        assert len(self.bip39.map) == 2048

    def test_generate_consistent_output(self):
        """Test that generate produces valid mnemonics consistently."""
        for _ in range(3):
            mnemo = self.bip39.generate(24)
            assert self.bip39.mnemo.check(mnemo)
            assert len(mnemo.split()) == 24


class TestSLIP39:
    """Test SLIP39 mnemonic generation and validation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.slip39 = SLIP39()

    def test_generate_24_words(self):
        """Test generating a 24-word mnemonic."""
        mnemo = self.slip39.generate(24)
        words = mnemo.split()
        assert len(words) == 24

    def test_deconstruct_reconstruct_24_words(self):
        """Test deconstructing and reconstructing a 24-word mnemonic."""
        mnemo = self.slip39.generate(24)
        shares = self.slip39.deconstruct(mnemo, required=2, total=3)

        assert len(shares) == 3

        # Should be able to reconstruct with any 2 shares
        reconstructed = self.slip39.reconstruct(shares[:2])
        assert reconstructed == mnemo

    def test_reconstruct_different_share_combinations(self):
        """Test reconstruction with different share combinations."""
        mnemo = self.slip39.generate(24)
        shares = self.slip39.deconstruct(mnemo, required=2, total=3)

        # Test all possible 2-share combinations
        assert self.slip39.reconstruct(shares[:2]) == mnemo
        assert self.slip39.reconstruct(shares[1:]) == mnemo
        assert self.slip39.reconstruct([shares[0], shares[2]]) == mnemo

    def test_wordlist_properties(self):
        """Test SLIP39 wordlist has correct properties."""
        assert len(self.slip39.words) == 1024
        assert self.slip39.words == sorted(self.slip39.words)
        assert len(self.slip39.map) == 1024


class TestIntegration:
    """Integration tests for the complete workflow."""

    def setup_method(self):
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def test_full_workflow_24_word(self):
        """Test the complete workflow from main function with 24-word mnemonic."""
        # Generate initial mnemonic
        mnemo = self.bip39.generate(24)

        # Deconstruct into 2 BIP39 parts
        bip_one, bip_two = self.bip39.deconstruct(mnemo, split=2)
        assert self.bip39.mnemo.check(bip_one)
        assert self.bip39.mnemo.check(bip_two)

        # Convert first BIP39 part to SLIP39 shares
        slip_one = self.slip39.deconstruct(bip_one, required=2, total=3)
        assert len(slip_one) == 3

        # Reconstruct first BIP39 part
        bip_one_reconstructed = self.slip39.reconstruct(slip_one[:2])
        assert bip_one_reconstructed == bip_one

        # Convert second BIP39 part to SLIP39 shares
        slip_two = self.slip39.deconstruct(bip_two, required=2, total=3)
        assert len(slip_two) == 3

        # Reconstruct second BIP39 part
        bip_two_reconstructed = self.slip39.reconstruct(slip_two[:2])
        assert bip_two_reconstructed == bip_two

        # Reconstruct full mnemonic
        mnemo_reconstructed = self.bip39.reconstruct(
            [bip_one_reconstructed, bip_two_reconstructed])
        assert mnemo_reconstructed == mnemo

    def test_full_workflow_12_word_direct(self):
        """Test SLIP39 workflow with 12-word mnemonic (no BIP39 splitting)."""
        # Generate initial mnemonic
        mnemo = self.bip39.generate(12)

        # Cannot deconstruct 12-word BIP39 into 2 parts (entropy too small)
        # Instead, test SLIP39 directly on the 12-word mnemonic
        shares = self.slip39.deconstruct(mnemo, required=2, total=3)

        # Reconstruct from shares
        mnemo_reconstructed = self.slip39.reconstruct(shares[:2])
        assert mnemo_reconstructed == mnemo

    def test_multiple_iterations(self):
        """Test multiple iterations to ensure consistency."""
        for _ in range(5):
            mnemo = self.bip39.generate(24)
            parts = self.bip39.deconstruct(mnemo, split=2)
            reconstructed = self.bip39.reconstruct(parts)
            assert reconstructed == mnemo

    def test_slip39_multiple_iterations(self):
        """Test SLIP39 multiple iterations to ensure consistency."""
        for _ in range(5):
            mnemo = self.slip39.generate(24)
            shares = self.slip39.deconstruct(mnemo, required=2, total=3)
            reconstructed = self.slip39.reconstruct(shares[:2])
            assert reconstructed == mnemo
