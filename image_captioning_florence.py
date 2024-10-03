import os
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from utils import get_folder_path, convert_images_to_jpeg, write_description_to_file

device = "cuda:0" if torch.cuda.is_available() else "cpu"

torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Use patch to override the get_imports function when loading the model
# with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
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


def generate_image_description(image_path, task_prompt):
    """
    Generates a description for the image using the Florence 2 model.
    """
    try:
        image = Image.open(image_path)

        inputs = processor(text=task_prompt, images=image, return_tensors="pt").to(
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


def main():
    """
    Processes each image in the folder, converts them to JPEG, generates a description, and writes the description to a file.
    """

    folder_path = get_folder_path()
    jpeg_folder = convert_images_to_jpeg(folder_path)
    print(f"Converted images are saved in {jpeg_folder}.")

    task_prompt = "<MORE_DETAILED_CAPTION>"

    keyword = input(
        "Please provide a keyword to be added to the description (optional): "
    )
    if keyword != "":
        wreplace = input(
            "Please provide a word to be replaced with the keyword (optional): "
        )
        if wreplace == "":
            wreplace = None
    else:
        keyword = None
        wreplace = None
    for filename in os.listdir(jpeg_folder):
        if filename.lower().endswith(".jpeg"):
            image_path = os.path.join(jpeg_folder, filename)
            print(f"Processing {image_path}...")

            description = generate_image_description(
                image_path,
                task_prompt,
            )
            write_description_to_file(image_path, description, keyword, wreplace)


if __name__ == "__main__":
    main()
