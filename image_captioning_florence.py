import os
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
import pillow_avif

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


# Workaround to skip flash-attn import
def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    """Workaround for FlashAttention"""
    if os.path.basename(filename) != "modeling_florence2.py":
        return get_imports(filename)
    imports = get_imports(filename)
    imports.remove("flash_attn")
    return imports


device = "cuda:0" if torch.cuda.is_available() else "cpu"

torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Use patch to override the get_imports function when loading the model
with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
    model = (
        AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-large-ft", trust_remote_code=True
        )
        .to(device)
        .eval()
    )
    processor = AutoProcessor.from_pretrained(
        "microsoft/Florence-2-large-ft", trust_remote_code=True
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
        os.rename(old_image_path, new_image_path)
        print(f"Renamed {old_image_path} to {new_image_path}")

    return jpeg_folder


def generate_image_description(image_path, task_prompt, text_input=None):
    """
    Generates a description for the image using the Florence 2 model.
    """
    try:
        image = Image.open(image_path)

        if text_input is None:
            prompt = task_prompt
        else:
            prompt = task_prompt + text_input

        inputs = processor(text=prompt, images=image, return_tensors="pt").to(
            device, torch_dtype
        )
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
        )
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        return generated_text
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
            file.write(description)
        print(f"Description written to {description_file_path}")


def main():
    """
    Processes each image in the folder, converts them to JPEG, generates a description, and writes the description to a file.
    """

    folder_path = get_folder_path()
    jpeg_folder = convert_images_to_jpeg(folder_path)
    print(f"Converted images are saved in {jpeg_folder}.")

    task_prompt = "<MORE_DETAILED_CAPTION>"
    text_input = input(
        "Enter additional information regarding the subjects in the images (optional): "
    )

    if text_input == "":
        text_input = None

    for filename in os.listdir(jpeg_folder):
        if filename.lower().endswith(".jpeg"):
            image_path = os.path.join(jpeg_folder, filename)
            print(f"Processing {image_path}...")

            description = generate_image_description(
                image_path, task_prompt, text_input
            )
            write_description_to_file(image_path, description)


if __name__ == "__main__":
    main()
