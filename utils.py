import os
from PIL import Image
import shutil
import re

SUPPORTED_FORMATS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".bmp",
    ".tiff",
    ".gif",
    ".eps",
    ".ico",
    ".icns",
    ".pcx",
    ".ppm",
    ".sgi",
    ".tga",
    ".tiff",
    ".pdf",
    ".jfif",
    ".jp2",
    ".jpx",
)


def get_folder_path():
    while True:
        folder_path = input("Enter a local filepath to a folder containing images: ")
        if not os.path.exists(folder_path):
            print("The specified path does not exist. Please enter a valid path.")
            continue
        if not os.path.isdir(folder_path):
            print(
                "The specified path is not a directory. Please enter a valid directory path."
            )
            continue
        images = [
            f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_FORMATS)
        ]
        if not images:
            print(
                "No images found in the specified directory. Please ensure the directory contains at least one image file."
            )
            continue
        break
    return folder_path


def convert_images_to_jpeg(folder_path):
    """
    Converts all non-JPEG images in a folder to JPEG format and saves them in a subfolder named "JPEGs".
    Then, all files are copied sequentially with a .jpeg extension as 001.jpeg, 002.jpeg, etc.
    """
    jpeg_folder = os.path.join(folder_path, "JPEGs")
    if not os.path.exists(jpeg_folder):
        os.makedirs(jpeg_folder)

    # Supported formats
    images = [
        f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_FORMATS)
    ]

    # Counter for sequential naming
    for i, image in enumerate(sorted(images), start=1):
        image_path = os.path.join(folder_path, image)
        new_filename = f"{i:03d}.jpeg"
        new_image_path = os.path.join(jpeg_folder, new_filename)

        if image.lower().endswith((".jpeg", ".jpg")):
            # Copy and rename JPEG/JPG images
            shutil.copy(image_path, new_image_path)
        else:
            # Convert other formats to JPEG and rename
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.save(new_image_path, "JPEG")

        print(f"Copied and renamed {image_path} to {new_image_path}")

    return jpeg_folder


def write_description_to_file(image_path, description, keyword=None, wreplace=None):
    """
    Writes the image description to a text file.
    """
    if description is not None:
        base_name = os.path.splitext(image_path)[0]
        description_file_path = f"{base_name}.txt"

        if keyword is not None and wreplace is not None:
            description = re.sub(wreplace, keyword, description, flags=re.IGNORECASE)
        elif keyword is not None and wreplace is None:
            description = keyword + ", " + description

        with open(description_file_path, "w", encoding="utf-8") as file:
            file.write(str(description))
        print(f"Description written to {description_file_path}")
