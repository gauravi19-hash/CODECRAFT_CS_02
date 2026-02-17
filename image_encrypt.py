"""
Image encryption/decryption using pixel manipulation.
Uses XOR on pixel values and optional position shuffling, keyed by a password.
"""

import hashlib
import random
from pathlib import Path

from PIL import Image


def _key_stream(key: str, length: int) -> bytes:
    """Generate a deterministic byte stream from the password for XOR."""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    stream = bytearray()
    while len(stream) < length:
        stream.extend(hashlib.sha256(h + stream[-32:] if len(stream) >= 32 else h).digest())
    return bytes(stream[:length])


def _shuffle_indices(n: int, seed: int) -> list[int]:
    """Return a permutation of range(n) using seed for reproducibility."""
    rng = random.Random(seed)
    indices = list(range(n))
    rng.shuffle(indices)
    return indices


def _unshuffle_indices(shuffled: list[int]) -> list[int]:
    """Inverse permutation: where did position i come from?"""
    inverse = [0] * len(shuffled)
    for i, j in enumerate(shuffled):
        inverse[j] = i
    return inverse


def _pixels_to_bytes(pixels: list, channels: int) -> bytearray:
    """Flatten list of (r,g,b) or (r,g,b,a) into bytearray."""
    out = bytearray()
    for p in pixels:
        for c in range(channels):
            out.append(p[c] if c < len(p) else 255)
    return out


def _bytes_to_pixels(data: bytearray, channels: int) -> list:
    """Convert bytearray back to list of pixel tuples."""
    pixels = []
    for i in range(0, len(data), channels):
        pixels.append(tuple(data[i : i + channels]))
    return pixels


def encrypt_image(input_path: str, output_path: str, password: str, shuffle: bool = True) -> None:
    """
    Encrypt an image: XOR pixel bytes with key stream and optionally shuffle pixel order.
    """
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    img = Image.open(path).convert("RGBA")
    width, height = img.size
    pixels = list(img.getdata())
    channels = 4  # RGBA
    flat = _pixels_to_bytes(pixels, channels)
    n = len(flat)

    # XOR with key stream
    key_bytes = _key_stream(password, n)
    for i in range(n):
        flat[i] ^= key_bytes[i]

    if shuffle:
        seed = int(hashlib.sha256(password.encode("utf-8")).hexdigest()[:16], 16)
        indices = _shuffle_indices(n, seed)
        shuffled = bytearray(n)
        for i, j in enumerate(indices):
            shuffled[j] = flat[i]
        flat = shuffled

    # Rebuild image from modified pixels
    pixels = _bytes_to_pixels(flat, channels)
    out_img = Image.new("RGBA", (width, height))
    out_img.putdata(pixels)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path, "PNG")
    print(f"Encrypted image saved to: {out_path}")


def decrypt_image(input_path: str, output_path: str, password: str, was_shuffled: bool = True) -> None:
    """
    Decrypt an image: unshuffle (if used) then XOR with the same key stream.
    """
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    img = Image.open(path).convert("RGBA")
    width, height = img.size
    pixels = list(img.getdata())
    channels = 4
    flat = _pixels_to_bytes(pixels, channels)
    n = len(flat)

    if was_shuffled:
        seed = int(hashlib.sha256(password.encode("utf-8")).hexdigest()[:16], 16)
        indices = _shuffle_indices(n, seed)
        inverse = _unshuffle_indices(indices)
        unshuffled = bytearray(n)
        for i in range(n):
            unshuffled[inverse[i]] = flat[i]
        flat = unshuffled

    key_bytes = _key_stream(password, n)
    for i in range(n):
        flat[i] ^= key_bytes[i]

    pixels = _bytes_to_pixels(flat, channels)
    out_img = Image.new("RGBA", (width, height))
    out_img.putdata(pixels)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path, "PNG")
    print(f"Decrypted image saved to: {out_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt images using pixel manipulation (XOR + optional shuffle)."
    )
    sub = parser.add_subparsers(dest="command", required=True, help="encrypt or decrypt")

    enc = sub.add_parser("encrypt", help="Encrypt an image")
    enc.add_argument("input", help="Path to input image")
    enc.add_argument("output", help="Path for encrypted output (PNG)")
    enc.add_argument("-p", "--password", required=True, help="Password for encryption")
    enc.add_argument("--no-shuffle", action="store_true", help="Only XOR pixels (no position shuffle)")

    dec = sub.add_parser("decrypt", help="Decrypt an image")
    dec.add_argument("input", help="Path to encrypted image")
    dec.add_argument("output", help="Path for decrypted output (PNG)")
    dec.add_argument("-p", "--password", required=True, help="Password used during encryption")
    dec.add_argument("--no-shuffle", action="store_true", help="Image was encrypted without shuffle")

    args = parser.parse_args()
    try:
        if args.command == "encrypt":
            encrypt_image(args.input, args.output, args.password, shuffle=not args.no_shuffle)
        else:
            decrypt_image(args.input, args.output, args.password, was_shuffled=not args.no_shuffle)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
