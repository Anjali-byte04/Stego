import os
import shutil
import requests

# Path to demo_images
DEMO_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "stego", "demo_images")
COVER_IMAGE_PATH = os.path.join(DEMO_IMAGES_DIR, "cover.png")

def add_local_image(source_path):
    """Copy a local image into demo_images as cover.png"""
    if not os.path.exists(source_path):
        print("❌ Source image not found!")
        return
    os.makedirs(DEMO_IMAGES_DIR, exist_ok=True)
    shutil.copy(source_path, COVER_IMAGE_PATH)
    print(f"✅ Local image copied to {COVER_IMAGE_PATH}")

def add_online_image(url):
    """Download an image from the internet into demo_images as cover.png"""
    os.makedirs(DEMO_IMAGES_DIR, exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(COVER_IMAGE_PATH, "wb") as f:
            f.write(response.content)
        print(f"✅ Image downloaded from {url} to {COVER_IMAGE_PATH}")
    else:
        print("❌ Failed to download image")

if __name__ == "__main__":
    # Example usage:
    # Copy from local system
    add_local_image("C:/Users/Pranjali Singh/Downloads/steg1.jpg")

    # OR Download from the internet
    # add_online_image("https://picsum.photos/300/300")
