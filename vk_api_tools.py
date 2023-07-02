import os
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests


def get_filename_extension(image_url: str) -> tuple:
    '''Gets filename and extension from given url'''
    root, extension = os.path.splitext(urlparse(unquote(image_url)).path)
    filename = root.split('/')[-1]
    return filename, extension


def download_image(image_url: str, to_save_path: Path, payload=None) -> str:
    '''Downloads images and saves in specified directory or in folder images
       and returns image name'''
    image_response = requests.get(url=image_url, params=payload)
    image_response.raise_for_status()
    image_name = ''.join(get_filename_extension(image_url=image_url))
    with open(Path(to_save_path, image_name), 'wb') as new_image:
        new_image.write(image_response.content)
    return image_name
