# Mnemonic CLI Tool

A command-line tool for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards. This tool allows you to split, combine, and convert mnemonic phrases for secure key management.

## Features

- **BIP39 Support**: Generate, validate, and split BIP39 mnemonic phrases
- **SLIP39 Support**: Create Shamir Secret Sharing (SLIP39) shares from mnemonics
- **Flexible Splitting**: Deconstruct 24-word mnemonics into multiple 12-word parts
- **Share Reconstruction**: Reconstruct mnemonics from SLIP39 shares with threshold requirements
- **Digit Mode**: Convert mnemonics to/from numeric format for easier backup

## Installation

### Development Setup

From the CLI directory:
```bash
cd cli
uv sync
```

### Build Binary

From the repository root:
```bash
./scripts/cli.sh
```

This creates a standalone executable at `dist/cli`.

## Usage

The CLI provides two main commands: `deconstruct` and `reconstruct`.

### Deconstruct Command

Split a BIP39 mnemonic into multiple parts or SLIP39 shares.

**From command line:**
```bash
./dist/cli deconstruct --mnemonic "your 24 word mnemonic phrase here..."
```

**From file:**
```bash
./dist/cli deconstruct --filename seed.txt --standard SLIP39
```

**Options:**
- `--mnemonic`: BIP39 mnemonic to deconstruct
- `--standard`: Output format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--filename`: File containing the BIP39 mnemonic (default: `seed.txt`)
- `--split`: Number of BIP39 parts to create (default: `2`)
- `--required`: Required shares for SLIP39 reconstruction (default: `2`)
- `--total`: Total SLIP39 shares to generate (default: `3`)
- `--digits`: Output numeric format instead of words

**Example: Create SLIP39 shares**
```bash
./dist/cli deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard SLIP39 \
  --required 2 \
  --total 3
```

**Example: Split into BIP39 parts**
```bash
./dist/cli deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard BIP39 \
  --split 2
```

### Reconstruct Command

Reconstruct a BIP39 mnemonic from shares or parts.

**From command line:**
```bash
./dist/cli reconstruct --shares "share1" "share2" --standard SLIP39
```

**From file:**
```bash
./dist/cli reconstruct --filename shares.txt --standard SLIP39 --split 2
```

**Options:**
- `--shares`: SLIP39 shares or BIP39 parts to reconstruct
- `--standard`: Input format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--filename`: File containing shares (newline separated, default: `seed.txt`)
- `--split`: Number of share groups for reconstruction (default: `2`)
- `--digits`: Input is in numeric format

**Example: Reconstruct from SLIP39 shares**
```bash
./dist/cli reconstruct \
  --shares "share1" "share2" "share3" "share4" \
  --standard SLIP39 \
  --split 2
```

## File Format

When using `--filename`, the file should contain one mnemonic or share per line:

```
word1 word2 word3 ... word24
```

For SLIP39 reconstruction with `--split 2`, shares should be grouped:
```
share1_group1
share2_group1
share1_group2
share2_group2
```

## Testing

Run the test suite:
```bash
cd cli
uv run pytest test_tools.py -v
```

## Security Notes

⚠️ **Important Security Considerations:**

- Never share your seed phrase or private keys
- Store mnemonic backups securely in multiple physical locations
- SLIP39 shares should be distributed to different secure locations
- Use the digit format for metal plate backups or other durable storage
- Always verify reconstructed mnemonics match the original
- This tool is for educational and personal use only

## Architecture

The CLI consists of three main modules:

- **`tools.py`**: Core BIP39 and SLIP39 implementation
  - `BIP39` class: Mnemonic generation, validation, splitting
  - `SLIP39` class: Shamir Secret Sharing implementation
  
- **`cli.py`**: Command-line interface using Typer
  - `deconstruct`: Split mnemonics into parts/shares
  - `reconstruct`: Rebuild mnemonics from parts/shares

- **`test_tools.py`**: Comprehensive test suite
  - BIP39 generation and roundtrip tests
  - SLIP39 share creation and reconstruction
  - Integration tests for full workflows

## Examples

### Secure Backup Strategy

1. Generate a 24-word BIP39 mnemonic
2. Split it into 2 parts (two 12-word mnemonics)
3. Convert each part to SLIP39 shares (2-of-3)
4. Distribute 6 total shares across secure locations
5. To recover, need 2 shares from each group (4 shares total)

```bash
# Deconstruct
./dist/cli deconstruct \
  --mnemonic "abandon abandon ... art" \
  --standard SLIP39 \
  --required 2 \
  --total 3

# Reconstruct (from file with 4+ shares)
./dist/cli reconstruct \
  --filename backup_shares.txt \
  --standard SLIP39 \
  --split 2
```

## Dependencies

- `hdwallet`: HD wallet generation and derivation
- `mnemonic`: BIP39 mnemonic implementation
- `slip39`: SLIP39 Shamir Secret Sharing
- `typer`: Modern CLI framework
- `pytest`: Testing framework

## License

For personal and educational use.