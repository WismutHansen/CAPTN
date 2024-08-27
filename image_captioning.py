import os
import openai
import base64
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


def load_config(config_file_path):
    """
    Loads configuration from a specified file path.
    """
    config = {}
    with open(config_file_path, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            config[key] = value
    return config


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


def encode_image_to_base64(image_path):
    """
    Encodes an image to a base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_image_description(image_path, config, prompt):
    """
    Generates a description for the image using the OpenAI API or a local vision model depending on the configuration.
    """
    base64_image = encode_image_to_base64(image_path)
    try:
        # Initialize the OpenAI client with configurations
        client = openai.OpenAI(api_key=config["api_key"])

        completion = client.chat.completions.create(
            model="gpt-4o",  # Replace with your actual model
            messages=[
                {
                    "role": "system",
                    "content": "This is a chat between a user and an assistant. The assistant is helping the user to describe an image.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=1000,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None


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




def main():
    """
    Processes each image in the folder, converts them to JPEG, generates a description, and writes the description to a file.
    """
    config_file_path = "OAI_CONFIG_LIST"  # Path to your configuration file
    config = load_config(config_file_path)

    folder_path = get_folder_path()
    jpeg_folder = convert_images_to_jpeg(folder_path)
    print(f"Converted images are saved in {jpeg_folder}.")

    prompt = input(
        "Please provide an image prompt, or leave empty for default prompt: "
    )
    if prompt == "":
        prompt = "Provide a detailed description of the image"
    keyword = input("Please provide a keyword to be added to the description (optional): ")
    if keyword!= "":
        wreplace = input("Please provide a word to be replaced with the keyword (optional): ")
        if wreplace == "":
            wreplace = None
    else
       keyword = None
       wreplace = None

    for filename in os.listdir(jpeg_folder):
        if filename.lower().endswith(".jpeg"):
            image_path = os.path.join(jpeg_folder, filename)
            print(f"Processing {image_path}...")
            description = generate_image_description(image_path, config, prompt)
            write_description_to_file(image_path, description)


if __name__ == "__main__":
    main()

