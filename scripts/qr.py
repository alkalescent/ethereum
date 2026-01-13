"""Generate QR codes for crypto addresses in README.

Reads crypto addresses from README.md and generates QR code images
in .github/qr/ directory.
"""

import os
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("Installing qrcode library...")
    os.system('uv pip install "qrcode[pil]"')
    import qrcode


# Crypto addresses
ADDRESSES = {
    "btc": "bc1qwn7ea6s8wqx66hl5rr2supk4kv7qtcxnlqcqfk",
    "eth": "0x7cdB1861AC1B4385521a6e16dF198e7bc43fDE5f",
    "xmr": "463fMSWyDrk9DVQ8QCiAir8TQd4h3aRAiDGA8CKKjknGaip7cnHGmS7bQmxSiS2aYtE9tT31Zf7dSbK1wyVARNgA9pkzVxX",
    "base": "0x7cdB1861AC1B4385521a6e16dF198e7bc43fDE5f",
}


def generate_qr(address: str, output_path: Path) -> None:
    """Generate a QR code for the given address."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"Generated: {output_path}")


def main():
    """Generate QR codes for all configured crypto addresses."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    output_dir = repo_root / ".github" / "qr"
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, address in ADDRESSES.items():
        output_path = output_dir / f"{name}.png"
        generate_qr(address, output_path)

    print(f"\nGenerated {len(ADDRESSES)} QR codes in {output_dir}")


if __name__ == "__main__":
    main()
