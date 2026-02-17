# Image Encryption Tool

A simple image encryption tool that uses **pixel manipulation** to encrypt and decrypt images. It supports:

- **XOR cipher**: Each pixel byte (R, G, B, A) is XORed with a key stream derived from your password.
- **Pixel shuffling**: Pixel positions can be shuffled with a password-based seed so the encrypted image looks like noise.

Encryption is **symmetric**: use the same password to decrypt.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Encrypt an image

```bash
python image_encrypt.py encrypt input.png encrypted.png -p "YourSecretPassword"
```

Encrypted output is saved as PNG. With the default options, both XOR and shuffle are applied.

To encrypt using only XOR (no shuffling):

```bash
python image_encrypt.py encrypt input.png encrypted.png -p "YourSecretPassword" --no-shuffle
```

### Decrypt an image

```bash
python image_encrypt.py decrypt encrypted.png decrypted.png -p "YourSecretPassword"
```

If the image was encrypted with `--no-shuffle`, decrypt with:

```bash
python image_encrypt.py decrypt encrypted.png decrypted.png -p "YourSecretPassword" --no-shuffle
```

## How it works

1. **Key stream**: Your password is hashed with SHA-256 and extended to a byte stream as long as the image data.
2. **XOR**: Every byte of the image (each R, G, B, A value) is XORed with the corresponding key byte. XOR is reversible: applying it again with the same key restores the original.
3. **Shuffle** (optional): A permutation of pixel positions is generated from a seed derived from the password. Encrypt shuffles positions; decrypt applies the inverse permutation.

Input images are converted to RGBA for processing; output is always PNG so no data is lost.

## Programmatic use

```python
from image_encrypt import encrypt_image, decrypt_image

encrypt_image("photo.png", "photo_encrypted.png", "MyPassword")
decrypt_image("photo_encrypted.png", "photo_restored.png", "MyPassword")
```

🎯 Purpose

Created for educational demonstration of basic cryptographic techniques applied to digital images.

⚠ Ethical Disclaimer

For academic and authorized use only.
