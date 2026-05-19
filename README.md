# 🔐 Stego-Messenger

> A Python-based secure messaging system that hides encrypted messages inside images using steganography — making communication invisible to the naked eye.

---

## 📌 What is Steganography?

Steganography is the practice of hiding secret information within ordinary, non-secret data or files. Unlike encryption (which scrambles data), steganography **conceals the existence** of the message itself — making it a powerful tool for secure communication.

---

## ✨ Features

- 🔒 **Message Embedding** — Hides text messages inside PNG/JPG images using LSB (Least Significant Bit) technique
- 🔑 **Encrypted Communication** — Ensures data privacy by embedding encrypted content
- 📤 **Encode** — Input a message + image → outputs a stego image with hidden data
- 📥 **Decode** — Input the stego image → extracts the hidden message
- 🖼️ **Lossless Output** — Stego image looks visually identical to the original

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core language |
| Pillow (PIL) | Image processing |
| LSB Algorithm | Data hiding technique |

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Anjali-byte04/Stego.git
cd Stego
```

### 2. Install dependencies
```bash
pip install pillow
```

### 3. Encode a message into an image
```bash
python add_image.py
```

Follow the prompts to:
- Select your input image
- Type the message you want to hide
- Get your output stego image

### 4. Decode the hidden message
```bash
python stego/decode.py
```

---

## 📁 Project Structure

```
Stego/
│
├── add_image.py          # Encodes message into image
├── stego/                # Core steganography module
├── input_image.png       # Sample input image
└── stego_image.png       # Output image with hidden message
```

---

## 💡 How It Works

1. Each character of the message is converted to its **binary (ASCII)** representation
2. The binary bits are embedded into the **least significant bits** of each pixel's RGB values
3. The change is so small (1 bit out of 8) that the image looks **identical** to the human eye
4. The decoder reverses the process to extract and reconstruct the original message


## 🔭 Future Improvements

- [ ] Add password-based encryption layer (AES)
- [ ] Support for audio/video steganography
- [ ] Build a Streamlit web interface
- [ ] Add capacity checker (max message size per image)

Made by **Anjali Singh** — 2nd Year B.Tech CSE student at IILM University, Gurugram.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/anjali-singh-)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/Anjali-byte04)


