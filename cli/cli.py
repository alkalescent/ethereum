import typer
import logging
import json
from typing import Annotated
from cli.tools import BIP39, SLIP39
logging.getLogger("slip39").setLevel(logging.ERROR)


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
            raise ValueError("Standard must be either 'SLIP39' or 'BIP39'")


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
        raise ValueError("Mnemonic is required")
    bip_parts = cli.bip39.deconstruct(mnemonic, split)
    if standard.upper() == "BIP39":
        output = [{
            "standard": "BIP39",
            "mnemonic": bip_part
        } for bip_part in bip_parts]
        typer.echo(json.dumps(output))
        raise typer.Exit(code=0)
    else:
        total_shares: list[list[str]] = []
        for part in bip_parts:
            shares = cli.slip39.deconstruct(part, required, total)
            if digits:
                shares = [" ".join(str(cli.slip39.map[word])
                                   for word in share.split()) for share in shares]
            total_shares.append(shares)

        output = {
            "standard": "SLIP39",
            "shares": total_shares,
        }
        typer.echo(json.dumps(output))
        raise typer.Exit(code=0)


@app.command()
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
        raise ValueError("Shares are required")
    if standard.upper() == "SLIP39":
        members = len(shares) // split
        groups = [shares[i:i + members]
                  for i in range(0, len(shares), members)]
        shares = []
        for group in groups:
            if digits:
                group = [" ".join(cli.slip39.words[int(idx)-1]
                                  for idx in member.split()) for member in group]
            shares.append(cli.slip39.reconstruct(group))
    elif digits:
        shares = [" ".join(cli.bip39.words[int(idx)-1]
                           for idx in share.split()) for share in shares]
    reconstructed = cli.bip39.reconstruct(shares)
    output = {
        "standard": "BIP39",
        "mnemonic": reconstructed
    }
    typer.echo(json.dumps(output))
    raise typer.Exit(code=0)


app()


# TODO: use Nuitka to compile this CLI into a standalone executable instead of Pyinstaller for speed
# TODO: standardize output formatting (e.g. JSON)
# TODO: use comma-delimited string for list of str
# TODO: use semi-colon and comma-delimited strings for list of list of str
# TODO: use newline and comma delimited strings for list of list of str file input
# TODO: add JSON input option
