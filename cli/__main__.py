import typer
from cli.tools import BIP39, SLIP39


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def get_mnemos(self, filename: str) -> list[str]:
        """Get the mnemos from a file."""
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]

    def enforce_standard(self, standard: str):
        if standard.upper() not in ["SLIP39", "BIP39"]:
            print("Standard must be either 'SLIP39' or 'BIP39'")
            raise typer.Exit(code=1)


app = typer.Typer()
cli = CLI()


@app.command()
def deconstruct(mnemonic: str = "", standard: str = "slip39", filename: str = "seed.txt"):
    cli.enforce_standard(standard)
    if not mnemonic:
        mnemonic = cli.get_mnemos(filename)[0]
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


@app.command()
def reconstruct(mnemonic: str = "", standard: str = "slip39", filename: str = "seed.txt"):
    cli.enforce_standard(standard)


app()


def main():
    cli = CLI()
    mnemo = cli.get_mnemos("seed.txt")[0]
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
