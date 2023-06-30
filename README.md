# Comics publisher



### How to install

1. Firstly, you have to install python and pip (package-management system) if they haven't been already installed.

2. Create a virtual environment with its own independent set of packages using [virtualenv/venv](https://docs.python.org/3/library/venv.html). It'll help you to isolate the project from the packages located in the base environment.

3. Install all the packages used in this project, in your virtual environment which you've created on the step 2. Use the `requirements.txt` file to install dependencies:
    ```console
    pip install -r requirements.txt
    ```
4. Tokens and other keys:
   1. You need to [create your own group](https://vk.com/groups?tab=admin&w=groups_create) or use an existing one in which you're going to make publications. Paste the group URL [into the search](https://regvk.com/id/) to find out the `group_id` for your group, and then save it.
   2. To post to the group wall, you need a user access token. You can get it by [creating a Standalone application](https://vk.com/editapp?act=create) in VK on the page for developers. After creating press [manage the application](https://vk.com/apps?act=manage), change App status to `Application on and visible to all` and save the `App ID`, it'll come in handy to get token.
   Replace the App_id text in the URL with your `App ID` and browse:
      ```
      https://oauth.vk.com/authorize?client_id=App_id&display=page&scope=photos,groups,wall,offline&response_type=token
      ```
      From the resulting URL, copy and save `access_token`. Resulting URL:
      ```
      https://oauth.vk.com/blank.html#access_token=TOKEN&expires_in=0&user_id=123
      ```

5. Create an `.env` file and locate it in the same directory where your project is. Copy and append your access_token and group_id to `.env` file like this:
    ```
    VK_GROUP_ID=paste_here_your_group_id_from_step_4.1
    VK_ACCESS_TOKEN=paste_here_your_token_from_step_4.2
    ```
6. Remember to add `.env` to your `.gitignore` if you are going to put the project on GIT.


### Examples of running scripts


Before using script `main.py` it is recommended to run it with optional argument `-h` to read the description and explore the features of the program.

Run in your console:
```Console
>>> python3 main.py -h
```

Output:
```Console
usage: main.py [-h] [-p PATH]

The script downloads randomly chosen image of the comic and its funny comment from https://xkcd.com/. The downloaded comic is published on the wall of the group (community) on vk.com. After publication the uploaded photo is
deleted.

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path where the uploaded photo will be saved
```

To post image with message, run in your console:
```Console
>>> python3 main.py
```

Output:
```Console
friendly_questions.png image has been successfully posted.
```

### Project Goals

The code is written for educational purposes.
