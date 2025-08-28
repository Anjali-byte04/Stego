import streamlit as st
import numpy as np

import boto3
import io
import base64
import qrcode # type: ignore
from PIL import Image, ImageChops

# ============ AWS CONFIG ============
AWS_REGION = "us-east-1"
S3_BUCKET = "hackathon-stego"   # put your bucket here
s3 = boto3.client("s3")

# --------- Utility: Upload to S3 and return presigned URL ---------
def upload_to_s3(file_bytes, filename, content_type="image/png"):
    s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=file_bytes, ContentType=content_type)
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": filename},
        ExpiresIn=3600  # 1 hour
    )
    return url

# --------- Simple XOR Stego ----------
def encode_message(img, message, password=""):
    data = "".join([format(ord(c), "08b") for c in message])
    n_bits = len(data)
    flat = img.flatten()
    if n_bits > len(flat):
        raise ValueError("Message too long!")
    for i in range(n_bits):
        flat[i] = (flat[i] & ~1) | int(data[i])
    return flat.reshape(img.shape)

def decode_message(img, password=""):
    flat = img.flatten()
    bits = [str(flat[i] & 1) for i in range(len(flat))]
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        char = chr(int("".join(byte), 2))
        if char == "\0": break
        chars.append(char)
    return "".join(chars)

# --------- QR Code Generation ----------
def generate_qr_with_message(message):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(message)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return np.array(img_qr)

# --------- Difference Heatmap ----------
def generate_diff_heatmap(cover, stego):
    diff = ImageChops.difference(Image.fromarray(cover), Image.fromarray(stego))
    return diff

# ============ Streamlit UI ============
st.set_page_config(page_title="Stego AWS Hackathon", page_icon="🔐", layout="wide")
st.title("🔐 Stego Messenger with AWS + QR + Heatmap")

mode = st.sidebar.radio("Choose Mode", ["Hide Message", "Extract Message", "QR Mode"])

# ---------------- Hide -----------------
if mode == "Hide Message":
    st.header("📝 Hide a Secret in an Image")
    uploaded_file = st.file_uploader("Upload a cover image", type=["png", "jpg", "jpeg"])
    secret = st.text_area("Enter your secret message")
    
    if uploaded_file and secret:
        cover_img = np.array(Image.open(uploaded_file).convert("RGB"))
        stego_img = encode_message(cover_img.copy(), secret)
        
        col1, col2 = st.columns(2)
        with col1: st.image(cover_img, caption="Original Cover", use_container_width=True)
        with col2: st.image(stego_img, caption="Stego Image", use_container_width=True)

        # Heatmap
        diff = generate_diff_heatmap(cover_img, stego_img)
        st.image(diff, caption="Difference Heatmap (almost invisible!)", use_container_width=True)

        # Save & Upload
        stego_pil = Image.fromarray(stego_img)
        buf = io.BytesIO()
        stego_pil.save(buf, format="PNG")
        buf.seek(0)
        
        url = upload_to_s3(buf.getvalue(), "stego_image.png")
        st.success("✅ Message hidden successfully!")
        st.write("🔗 Share this link to extract message:")
        st.code(url)

# ---------------- Extract -----------------
elif mode == "Extract Message":
    st.header("📂 Extract Secret Message")
    img_url = st.text_input("Paste S3 image URL here")
    
    if img_url:
        response = s3.get_object(Bucket=S3_BUCKET, Key=img_url.split("/")[-1])
        img_bytes = response["Body"].read()
        stego_img = np.array(Image.open(io.BytesIO(img_bytes)))
        
        hidden = decode_message(stego_img)
        st.success(f"🔑 Hidden Message: {hidden}")

# ---------------- QR Mode -----------------
elif mode == "QR Mode":
    st.header("📱 QR Code Stego Mode")
    msg = st.text_input("Enter secret message for QR")
    if msg:
        qr_img = generate_qr_with_message(msg)
        st.image(qr_img, caption="QR with Hidden Message")
        
        # Save & Upload
        qr_pil = Image.fromarray(qr_img)
        buf = io.BytesIO()
        qr_pil.save(buf, format="PNG")
        buf.seek(0)
        url = upload_to_s3(buf.getvalue(), "qr_secret.png")
        st.success("✅ QR Code generated and uploaded")
        st.write("🔗 Share this QR code link:")
        st.code(url)
