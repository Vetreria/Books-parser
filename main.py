import requests
import dotenv
from pathlib import Path
from urllib.parse import urlparse
import re


def save_image(file_link, filename):
    response = requests.get(file_link)
    response.raise_for_status()
    with open(filename, "wb") as file:
        file.write(response.content)


def make_id():
    for id in range(1, 10):
        get_file(id)


def get_file(id):
    url = f"https://tululu.org/txt.php?id={id}"
    response = requests.get(url)
    response.raise_for_status()
    filename = get_filename_from_cd(response.headers.get('content-disposition'))
    if filename:
        filename = filename[1:-1]
    else:
        filename =f"{id}.txt"
    with open(f"books\{filename}", 'wb') as file:
        file.write(response.content)


def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    dotenv.load_dotenv()
    make_id()



if __name__ == "__main__":
    main()