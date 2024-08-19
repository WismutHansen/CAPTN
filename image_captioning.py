import os
import openai
import base64
from PIL import Image
import shutil

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
    Then, all files are renamed sequentially with a .jpeg extension as 001.jpeg, 002.jpeg, etc.
    """
    jpeg_folder = os.path.join(folder_path, "JPEGs")
    if not os.path.exists(jpeg_folder):
        os.makedirs(jpeg_folder)

    # First, convert non-JPEG images to JPEG and save them in the "JPEGs" folder
    images = [
        f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_FORMATS)
    ]

    for image in images:
        image_path = os.path.join(folder_path, image)
        if image.lower().endswith((".jpeg", ".jpg")):
            # Rename JPEG/JPG images directly to have .jpeg extension and move them to the new folder
            new_image_name = os.path.splitext(image)[0] + ".jpeg"
            new_image_path = os.path.join(jpeg_folder, new_image_name)
            if not os.path.exists(new_image_path):
                os.rename(image_path, new_image_path)
        else:
            # Convert other formats to JPEG
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                new_image_name = os.path.splitext(image)[0] + ".jpeg"
                new_image_path = os.path.join(jpeg_folder, new_image_name)
                img.save(new_image_path, "JPEG")

    # Now, rename all files in the "JPEGs" folder sequentially with a .jpeg extension
    jpeg_images = sorted(os.listdir(jpeg_folder))

    for i, image in enumerate(jpeg_images, start=1):
        old_image_path = os.path.join(jpeg_folder, image)
        new_filename = f"{i:03d}.jpeg"
        new_image_path = os.path.join(jpeg_folder, new_filename)
        shutil.copy(old_image_path, new_image_path)
        print(f"Renamed {old_image_path} to {new_image_path}")

    return jpeg_folder


def encode_image_to_base64(image_path):
    """
    Encodes an image to a base64 string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_image_description(image_path, config):
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
                            "text": "Describe this photo depicting sks man",
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


def write_description_to_file(image_path, description):
    """
    Writes the image description to a text file.
    """
    if description is not None:
        base_name = os.path.splitext(image_path)[0]
        description_file_path = f"{base_name}.txt"
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

    for filename in os.listdir(jpeg_folder):
        if filename.lower().endswith(".jpeg"):
            image_path = os.path.join(jpeg_folder, filename)
            print(f"Processing {image_path}...")
            description = generate_image_description(image_path, config)
            write_description_to_file(image_path, description)


if __name__ == "__main__":
    main()

