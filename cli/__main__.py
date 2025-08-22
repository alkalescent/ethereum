import typer
from cli.tools import BIP39, SLIP39


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def get_mnemo(self, filename: str) -> bytes:
        """Get the mnemo from a file."""
        with open(filename, "r") as f:
            return f.read()


app = typer.Typer()
cli = CLI()


@app.command()
def deconstruct(
        _: str, mnemonic: str = "", standard: str = "slip39", filename: str = "seed.txt"):
    if standard.upper() not in ["SLIP39", "BIP39"]:
        print("Standard must be either 'SLIP39' or 'BIP39'")
        raise typer.Exit(code=1)
    if not mnemonic:
        mnemonic = cli.get_mnemo(filename)
    if not mnemonic:
        print("Mnemonic is required")
        raise typer.Exit(code=1)
    bip_one, bip_two = cli.bip39.deconstruct(mnemonic)
    if standard.upper() == "BIP39":
        print("BIP39 Deconstructed:", bip_one, bip_two)
        raise typer.Exit(code=0)
    else:
        slip_one = cli.slip39.deconstruct(bip_one)
        slip_two = cli.slip39.deconstruct(bip_two)
        print("SLIP39 Shares:", slip_one, slip_two)
        raise typer.Exit(code=0)


app()


def main():
    cli = CLI()
    mnemo = cli.get_mnemo("seed.txt")
    print("Mnemonic:", mnemo)
    addr = cli.bip39.eth(mnemo)
    print("Eth Addr:", addr)
    bip_one, bip_two = cli.bip39.deconstruct(mnemo)
    print("Deconstructed:", bip_one, bip_two)
    slip_one = cli.slip39.deconstruct(bip_one)
    print("SLIP39 Shares:", slip_one)
    bip_one_reconstructed = cli.slip39.reconstruct(slip_one)
    print("Reconstructed BIP39:", bip_one_reconstructed)
    slip_two = cli.slip39.deconstruct(bip_two)
    print("SLIP39 Shares:", slip_two)
    bip_two_reconstructed = cli.slip39.reconstruct(slip_two)
    print("Reconstructed BIP39:", bip_two_reconstructed)
    mnemo_reconstructed = cli.bip39.reconstruct(
        [bip_one_reconstructed, bip_two_reconstructed])
    print("Reconstructed Mnemonic:", mnemo_reconstructed)
    print("Match:", mnemo == mnemo_reconstructed)


# typer.run(main)
