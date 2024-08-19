# CAPTN

The python scripts in this repository automatically convert images files in a specified folder to .jpeg and generate captions as individual .txt files for each image using eiter the Open AI API with e.g. gpt4o or the Florence2 model downloaded to your machine. Use this script to quickly prepare an image set to be used for FLUX finetuning e.g. with [ai-toolkit](https://github.com/ostris/ai-toolkit).

The images and captions are saved to a new subfolder named "JPEGs"

### Using the Open AI API

Just rename OAI_CONFIG_LIST.example to OAI_CONFIG_LIST, enter your OpenAI API key and run

```
pip install -r requirements.txt
```

and then

```shell
python -m image_captioning
```

you'll be prompted for the folder path and everything else runs automatically.

### Using the Florence2 Model locally

Tested with python 3.10

```
pip install -r requirements_florence.txt
```

and then

```
python -m image_captioning_florence
```

you'll be prompted for the folder path and everything else runs automatically.

