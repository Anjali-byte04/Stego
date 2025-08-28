from PIL import Image

def hide_message(input_image_path, secret_message, output_image_path):
    img = Image.open(input_image_path)
    encoded = img.copy()
    width, height = img.size
    index = 0

    # Add a delimiter to know when to stop
    binary_message = ''.join(format(ord(i), '08b') for i in secret_message) + "1111111111111110"

    for row in range(height):
        for col in range(width):
            if index < len(binary_message):
                pixel = list(img.getpixel((col, row)))
                # Modify LSB of red channel
                pixel[0] = pixel[0] & ~1 | int(binary_message[index])
                encoded.putpixel((col, row), tuple(pixel))
                index += 1

    encoded.save(output_image_path)
    print(f"✅ Message hidden successfully inside {output_image_path}")

def extract_message(stego_image_path):
    img = Image.open(stego_image_path)
    binary_data = ""
    for row in range(img.height):
        for col in range(img.width):
            pixel = list(img.getpixel((col, row)))
            binary_data += str(pixel[0] & 1)

    # Split into 8-bit chunks
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]

    decoded = ""
    for byte in all_bytes:
        char = chr(int(byte, 2))
        if decoded.endswith("þ"):  # "1111111111111110" marker
            break
        decoded += char

    # Remove the marker at the end
    return decoded.replace("þ", "")

