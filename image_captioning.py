import os
import openai
import base64
from utils import get_folder_path, convert_images_to_jpeg, write_description_to_file


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
            description = generate_image_description(image_path, config, prompt)
            write_description_to_file(image_path, description, keyword, wreplace)


if __name__ == "__main__":
    main()
