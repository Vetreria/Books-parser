import requests
import os
import dotenv
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlparse


def get_file_ext(url_img):
    cut = urlparse(url_img)
    return os.path.splitext(cut.path)[-1]


def find_url():
    for id in range(1, 11):
        url = f"https://tululu.org/b{id}/"
        response = requests.get(url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            title, url_img = find_tag(response)
            download_txt(title, id)
            download_image(url_img, title)
        except:
            print(f'Книги не найдено! Пропускаем!')
            continue


def find_tag(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text
    title_split = title_text.split("::")
    title = title_split[0].strip(" \xa0 ")
    book_img_id = soup.find(class_='bookimage').find('img')['src']
    url_img = (urljoin('https://tululu.org/', book_img_id))
    print(title)
    return title, url_img


def download_txt(title, id, folder='books/'):
    url = f"https://tululu.org/txt.php?id={id}/"
    response = requests.get(url)
    response.raise_for_status()
    filename = f"{id}.{title}.txt"
    filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(url_img, title, folder='image/'):
    response = requests.get(url_img)
    response.raise_for_status()
    file_ext = get_file_ext(url_img)
    filepath = os.path.join(folder, sanitize_filename(title) + file_ext)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("image").mkdir(parents=True, exist_ok=True)
    dotenv.load_dotenv()
    find_url()


if __name__ == "__main__":
    main()