from pathlib import Path
import argparse
import os
import random
import requests
from vk_api_tools import check_create_path, download_image
from dotenv import load_dotenv


def publish_photo(photo_path: Path, access_token: str,
                  group_id: int, message: str, version=5.81):
    '''Gets the address for uploading files, uploads it to the server,
    saves the photo to the group album and publishes the post in the group'''

    def get_server_url(access_token: str, group_id: int,
                       version: float) -> str | dict:
        '''Gets server's url address for uploading file'''
        payload = {
            'access_token': access_token,
            'group_id': group_id,
            'v': version,
        }
        server_response = requests.get(
            url='https://api.vk.com/method/photos.getWallUploadServer/',
            params=payload)
        server_response = server_response.json()
        if server_response.get('error'):
            return server_response
        server_url = server_response.get('response').get('upload_url')
        return server_url

    def upload_to_server(photo_path: Path, server_url: str) -> list | None:
        '''Uploads the file to the server and returns list with
           server, photo and hash'''
        with open(file=photo_path, mode='rb') as image:
            files = {'photo': image}
            upload_response = requests.post(url=server_url, files=files)
            upload_response.raise_for_status()
            upload_response_values = list(upload_response.json().values())
            if not upload_response_values[1]:
                return print("File wasn't uploaded")
            return upload_response_values

    def save_photo_to_album(access_token: str, group_id: int, version: float,
                            server: int, photo: str, hash: str) -> str:
        '''Saves uploaded photo to album and returns attachments message'''
        data = {
            'access_token': access_token,
            'group_id': group_id,
            'v': version,
            'server': server,
            'photo': photo,
            'hash': hash,
        }
        photo_response = requests.post(
            url='https://api.vk.com/method/photos.saveWallPhoto/', data=data)
        photo_response.raise_for_status()
        photo_response = photo_response.json().get('response')[0]
        owner_id = photo_response.get('owner_id')
        media_id = photo_response.get('id')
        return f'photo{owner_id}_{media_id}'

    def publish_in_group(access_token: str, version: float,
                         attachments: str, message: str):
        '''Publishes uploaded photo and its comment on the wall of the group'''
        payload = {
            'access_token': access_token,
            'v': version,
            'owner_id': f'-{group_id}',
            'from_group': 1,
            'attachments': attachments,
            'message': message,
        }
        publish_response = requests.get(
            url='https://api.vk.com/method/wall.post/', params=payload)
        publish_response.raise_for_status()

    server_response = get_server_url(access_token, group_id, version)
    try:
        server_response.get('error')
        return server_response
    except AttributeError:
        server, photo, hash = upload_to_server(photo_path,
                                               server_url=server_response)
    attachments = save_photo_to_album(access_token, group_id, version,
                                      server, photo, hash)
    return publish_in_group(access_token, version, attachments, message)


def get_count_of_comics() -> int:
    '''Function returns number of existing comics on the current date'''
    curent_comics_response = requests.get('https://xkcd.com/info.0.json')
    curent_comics_response.raise_for_status()
    comics_number = curent_comics_response.json().get('num')
    return comics_number


def get_random_comics(comics_number) -> tuple:
    '''Selects a random comics based on the number of existing comics
       and returns url of the comics image and its comment.'''
    random_comics_number = random.randrange(1, comics_number + 1)
    comics_response = requests.get(
        f"https://xkcd.com/{random_comics_number}/info.0.json")
    comics_response.raise_for_status()
    comics_response = comics_response.json()
    image_url = comics_response.get('img')
    comics_comment = comics_response.get('alt')
    return image_url, comics_comment


def main():
    '''Main function'''
    os.chdir(os.path.dirname(__file__))
    load_dotenv()
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
    parser = argparse.ArgumentParser(
        description='''The script downloads randomly chosen image of the comic
                       and its funny comment from https://xkcd.com/.
                       The downloaded comic is published on the wall of the
                       group (community) on vk.com.
                       After publication the uploaded photo is deleted.'''
    )
    parser.add_argument("-p", "--path", type=Path, default="images",
                        help="path where the uploaded photo will be saved")
    args = parser.parse_args()
    check_create_path(args.path)
    try:
        image_url, comics_comment = get_random_comics(get_count_of_comics())
    except Exception as err:
        return print(err)
    image_name = download_image(image_url=image_url, to_save_path=args.path)
    photo_path = Path(args.path, image_name)
    try:
        publish_photo(photo_path=photo_path, access_token=vk_access_token,
                      group_id=vk_group_id, message=comics_comment)
    except Exception as err:
        print(err)
    os.remove(photo_path)
    return print(f"{image_name} image has been successfully posted.")


if __name__ == "__main__":
    main()
