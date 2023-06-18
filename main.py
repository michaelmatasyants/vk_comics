from pathlib import Path
import argparse
import os
import random
import requests
import vk_api_tools
from dotenv import load_dotenv

os.chdir(os.path.dirname(__file__))


def publish_photo(photo_path: Path, acess_token: str,
                  group_id: int, message: str) -> dict:
    '''Gets the address for uploading photo, uploads it to the server,
    saves the photo to the group album and publishes the post in the group'''
    params = {
        'access_token': acess_token,
        'group_id': group_id,
        'v': 5.81,
    }

    def get_server_url(params: dict) -> tuple | dict:
        '''Gets server's url address for uploading photo'''
        server_response = vk_api_tools.get_response(
            url='https://api.vk.com/method/photos.getWallUploadServer/',
            payload=params).json()
        if server_response.get('error'):
            return server_response
        server_url = server_response.get('response').get('upload_url')
        return server_url

    def upload_to_server(photo_path: Path, params: dict, server_url: str
                         ) -> dict | None:
        '''Uploads the file to the server and returns updated params
           with adding server, photo and hash'''
        with open(file=photo_path, mode='rb') as image:
            files = {'photo': image}
            upload_response = requests.post(url=server_url, files=files)
            upload_response.raise_for_status()
            keys = ['server', 'photo', 'hash']
            values = list(upload_response.json().values())
            if not values[1]:
                return print("File wasn't uploaded")
            for key, value in dict(zip(keys, values)).items():
                params[key] = value
            return params

    def save_photo_to_album(params: dict, message: str, from_group=1) -> dict:
        '''Saves uploaded photo to album and returns updated params
           with adding owner_id, from_group, attachments and message'''
        photo_response = requests.post(
            url='https://api.vk.com/method/photos.saveWallPhoto/', data=params)
        photo_response.raise_for_status()
        dict_response = photo_response.json().get('response')[0]
        owner_id = -(dict_response.get('owner_id'))
        media_id = dict_response.get('id')
        keys = ['owner_id', 'from_group', 'attachments', 'message']
        values = [owner_id, from_group, f'photo{owner_id}_{media_id}', message]
        for key, value in dict(zip(keys, values)).items():
            params[key] = value
        return params

    def publish_in_group(params: dict):
        '''Publishes uploaded photo and its comment on the wall of the group'''
        publish_response = vk_api_tools.get_response(
            url='https://api.vk.com/method/wall.post/', payload=params)
        return publish_response.json()

    server_response = get_server_url(params=params)
    try:
        server_response.get('error')
        return server_response
    except AttributeError:
        new_params = upload_to_server(photo_path=photo_path, params=params,
                                      server_url=server_response)
        return publish_in_group(params=save_photo_to_album(params=new_params,
                                                           message=message))


def get_count_of_comics() -> int:
    '''Function returns number of existing comics on the current date'''
    curent_comics_response = vk_api_tools.get_response(
        url='https://xkcd.com/info.0.json')
    comics_number = curent_comics_response.json().get('num')
    return comics_number


def get_random_comics(comics_number) -> tuple:
    '''Selects a random comics based on the number of existing comics
       and returns url of the comics image and its comment.'''
    random_comics_number = random.randrange(1, comics_number + 1)
    comics_response = vk_api_tools.get_response(
        url=f"https://xkcd.com/{random_comics_number}/info.0.json").json()
    image_url = comics_response.get('img')
    comics_comment = comics_response.get('alt')
    return image_url, comics_comment


def main():
    '''Main function'''
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
    vk_api_tools.check_create_path(args.path)
    image_url, comics_comment = get_random_comics(get_count_of_comics())
    image_name = vk_api_tools.download_image(image_url=image_url,
                                             to_save_path=args.path)
    photo_path = Path(args.path, image_name)
    try:
        print(publish_photo(photo_path=photo_path, acess_token=vk_access_token,
                            group_id=vk_group_id, message=comics_comment))
    except Exception as err:
        print(err)
    os.remove(photo_path)


if __name__ == "__main__":
    main()
