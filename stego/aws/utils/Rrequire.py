import streamlit as st
from PIL import Image
import numpy as np
import io, base64, boto3

# ---------------- AWS CONFIG ----------------
AWS_ACCESS_KEY = "YOUR_ACCESS_KEY"
AWS_SECRET_KEY = "YOUR_SECRET_KEY"
BUCKET_NAME = "YOUR_BUCKET_NAME"

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="ap-south-1"  # change region if needed
)

# ---------------- HELPER FUNCTIONS ----------------
def encode_text_in_image(image, text):
    img = image.convert("RGB")
    arr = np.array(img)

    binary = ''.join(format(ord(c), '08b') for c in text) + "1111111111111110"
    h, w, _ = arr.shape
    total_pixels = h * w

    if len(binary) > total_pixels * 3:
        raise ValueError("Message too large to hide in this image.")

    flat = arr.flatten()
    for i in range(len(binary)):
        flat[i] = (flat[i] & ~1) | int(binary[i])

    new_arr = flat.reshape(arr.shape)
    return Image.fromarray(new_arr.astype(np.uint8))


def decode_text_from_image(image):
    arr = np.array(image)
    flat = arr.flatten()
    bits = [str(flat[i] & 1) for i in range(len(flat))]

    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        char = chr(int(''.join(byte), 2))
        if char == "þ":  # our stopping marker
            break
        chars.append(char)
    return ''.join(chars)


def upload_to_s3(file_bytes, filename):
    s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=file_bytes)
    return filename


def generate_presigned_url(filename, expiry=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': filename},
        ExpiresIn=expiry
    )

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Hackathon Steganography Tool", page_icon="🕵️‍♂️", layout="wide")

st.title("🕵️ Hackathon Steganography Tool (AWS + Python 3.13)")
tab1, tab2 = st.tabs(["Hide Message/File", "Extract Message/File"])

# ---------------- TAB 1: HIDE ----------------
with tab1:
    st.header("Hide your secret message or file in an image")

    cover_file = st.file_uploader("Upload Cover Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    secret_text = st.text_area("Enter Secret Message (optional)")
    secret_file = st.file_uploader("Or upload a file to hide", type=["txt", "pdf", "zip"])

    if st.button("Hide & Upload to AWS"):
        if cover_file:
            cover_img = Image.open(cover_file)

            if secret_text:
                # Hide text
                stego_img = encode_text_in_image(cover_img, secret_text)
                buf = io.BytesIO()
                stego_img.save(buf, format="PNG")
                buf.seek(0)

                upload_to_s3(buf.getvalue(), "stego_image.png")
                url = generate_presigned_url("stego_image.png")

                st.image(stego_img, caption="Stego Image", use_container_width=True)
                st.download_button("⬇️ Download Stego Image", buf.getvalue(), "stego_image.png")
                st.success("✅ Stego image stored in AWS S3!")

            elif secret_file:
                # Hide file
                file_bytes = secret_file.read()
                encoded_text = base64.b64encode(file_bytes).decode()
                stego_img = encode_text_in_image(cover_img, encoded_text)
                buf = io.BytesIO()
                stego_img.save(buf, format="PNG")
                buf.seek(0)

                upload_to_s3(buf.getvalue(), "stego_file_image.png")
                url = generate_presigned_url("stego_file_image.png")

                st.image(stego_img, caption="Stego Image", use_container_width=True)
                st.download_button("⬇️ Download Stego Image", buf.getvalue(), "stego_file_image.png")
                st.success("✅ Stego file image stored in AWS S3!")

            else:
                st.error("⚠️ Please enter a message or upload a file to hide.")

# ---------------- TAB 2: EXTRACT ----------------
with tab2:
    st.header("Extract hidden message or file from stego image")

    stego_file = st.file_uploader("Upload Stego Image (PNG)", type=["png"])

    if st.button("Extract"):
        if stego_file:
            stego_img = Image.open(stego_file)
            extracted_text = decode_text_from_image(stego_img)

            try:
                # Try decoding as file
                file_bytes = base64.b64decode(extracted_text)
                st.success("✅ Extracted a hidden file!")
                st.download_button("⬇️ Download Extracted File", file_bytes, "extracted_file.txt")
            except Exception:
                # Otherwise show as text
                st.success("✅ Extracted hidden message:")
                st.code(extracted_text)




