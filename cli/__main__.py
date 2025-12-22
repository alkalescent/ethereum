import typer
from typing import Annotated
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
def deconstruct(
    mnemonic: Annotated[str, typer.Option(
        help="BIP39 mnemonic to deconstruct")] = "",
    standard: Annotated[str, typer.Option(
        help="Output format: 'BIP39' or 'SLIP39'")] = "SLIP39",
    filename: Annotated[str, typer.Option(
        help="File containing the BIP39 mnemonic"
    )] = "seed.txt",
    split: Annotated[int, typer.Option(
        help="Number of BIP39 parts to which to deconstruct the BIP39 mnemonic (e.g. 2 12-word parts for a 24-word mnemonic)")] = 2,
    required: Annotated[int, typer.Option(
        help="Number of required shares for SLIP39 reconstruction (e.g. 2 of 3)")] = 2,
    total: Annotated[int, typer.Option(
        help="Number of total shares for SLIP39 reconstruction (e.g. 3 of 3)")] = 3,
    digits: Annotated[bool, typer.Option(
        help="Output format: use digits instead of words"
    )] = False,
):
    cli.enforce_standard(standard)
    if not mnemonic:
        mnemonic = cli.get_mnemos(filename)[0]
    if not mnemonic:
        print("Mnemonic is required")
        raise typer.Exit(code=1)
    bip_parts = cli.bip39.deconstruct(mnemonic, split)
    if standard.upper() == "BIP39":
        print("BIP39 Deconstructed:", bip_parts)
        raise typer.Exit(code=0)
    else:
        total_shares = []
        for part in bip_parts:
            shares = cli.slip39.deconstruct(part, required, total)
            if digits:
                assert cli.slip39.wordlist == sorted(cli.slip39.wordlist)
                slip_map = {word: idx+1 for idx, word in enumerate(
                    cli.slip39.wordlist)}
                shares = [" ".join(str(slip_map[word])
                                   for word in share.split()) for share in shares]
            total_shares.append(shares)

        print("SLIP39 Shares:", total_shares)
        raise typer.Exit(code=0)


@app.command()
# TODO: implement digits
def reconstruct(
    shares: Annotated[list[str], typer.Option(
        help="SLIP39 shares to reconstruct")] = [],
    standard: Annotated[str, typer.Option(
        help="Input format: 'BIP39' or 'SLIP39'")] = "SLIP39",
    filename: Annotated[str, typer.Option(
        help="File containing the SLIP39 shares (newline separated)"
    )] = "seed.txt",
    split: Annotated[int, typer.Option(
        help="Number of SLIP39 share groups from which to reconstruct the BIP39 mnemonic(s) (e.g. 2 groups of 20-word shares)"
    )] = 2,
    digits: Annotated[bool, typer.Option(
        help="Input format: use digits instead of words"
    )] = False,
):
    cli.enforce_standard(standard)
    if not shares:
        shares = cli.get_mnemos(filename)
    if not shares:
        print("Shares are required")
        raise typer.Exit(code=1)

    if standard.upper() == "SLIP39":
        members = len(shares) // split
        groups = [shares[i:i + members]
                  for i in range(0, len(shares), members)]

        shares = []
        for group in groups:
            if digits:
                # TODO:
                pass
            shares.append(cli.slip39.reconstruct(group))
    elif digits:
        # TODO:
        pass
    reconstructed = cli.bip39.reconstruct(shares)
    print("BIP39 Reconstructed:", reconstructed)
    raise typer.Exit(code=0)


app()

# TODO: add tests


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
