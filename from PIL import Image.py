from PIL import Image
import random

def xor_pixels(img, key):
    pixels = img.load()
    width, height = img.size
    
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                r ^ key,
                g ^ key,
                b ^ key
            )
    return img

def swap_pixels(img, key):
    pixels = img.load()
    width, height = img.size
    
    random.seed(key)
    for _ in range(10000):  # number of swaps
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(0, width - 1)
        y2 = random.randint(0, height - 1)
        
        temp = pixels[x1, y1]
        pixels[x1, y1] = pixels[x2, y2]
        pixels[x2, y2] = temp
        
    return img

def encrypt_image(input_path, output_path, key):
    img = Image.open(input_path).convert("RGB")
    
    img = xor_pixels(img, key)
    img = swap_pixels(img, key)
    
    img.save(output_path)
    print("Encryption complete!")

def decrypt_image(input_path, output_path, key):
    img = Image.open(input_path).convert("RGB")
    
    img = swap_pixels(img, key)  # reverse swaps (same seed/key)
    img = xor_pixels(img, key)   # XOR again reverses
    
    img.save(output_path)
    print("Decryption complete!")

# ---- Main Program ----
if __name__ == "__main__":
    choice = input("Encrypt or Decrypt (e/d): ").lower()
    input_path = input("Enter image path: ")
    output_path = input("Enter output path: ")
    key = int(input("Enter numeric key (0-255): "))
    
    if choice == 'e':
        encrypt_image(input_path, output_path, key)
    elif choice == 'd':
        decrypt_image(input_path, output_path, key)
    else:
        print("Invalid choice!")
