import os
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse, unquote
import requests
from PIL import Image


def check_create_path(to_save_path: Path):
    to_save_path.mkdir(parents=True, exist_ok=True)


def get_filename_extension(image_url: str) -> tuple:
    '''Gets filename and extension from given url'''
    root, extension = os.path.splitext(urlparse(unquote(image_url)).path)
    filename = root.split('/')[-1]
    return filename, extension


def save_image(bytes_image: bytes, to_save_path: Path, image_name="image.png"):
    '''Creates and saves image in specified path from given bytes'''
    with Image.open(BytesIO(bytes_image)) as new_image:
        new_image.save(Path(to_save_path, image_name))


def download_image(image_url: str, to_save_path: Path, payload=None) -> str:
    '''Downloads images and places in specified directory or in folder images
       and returns image name'''
    image_response = requests.get(url=image_url, params=payload)
    image_response.raise_for_status()
    image_name = ''.join(get_filename_extension(image_url=image_url))
    save_image(bytes_image=image_response.content, to_save_path=to_save_path,
               image_name=image_name)
    return image_name
