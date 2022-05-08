import argparse
import logging
import os
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm

logger = logging.getLogger("logger")


def get_books(start_end_img_txt):
    books_tag = {}
    start_id, end_id, get_imgs, get_txt = start_end_img_txt
    for id in tqdm(range(start_id, end_id + 1), desc="Собираем книжки"):
        while True:
            try:
                url = f"https://tululu.org/b{id}/"
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                books_tag[id] = parse_book_page(
                    response, get_imgs, get_txt, id)
                break
            except requests.HTTPError:
                logger.warning('Книга не найдена')
                break
            except requests.ConnectionError:
                logger.warning('Нет связи, повторная попытка через 10 сек.')
                sleep(10)
    return books_tag


def parse_book_page(response, get_imgs, get_txt, id):
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split("::")[0].strip(" \xa0 ")
    author = soup.find('h1').text.split("::")[1].strip(" \xa0 ")
    book_img_id = soup.find(class_='bookimage').find('img')['src']
    url_img = (urljoin('https://tululu.org/', book_img_id))
    genres = [genre.text for genre in soup.select('span.d_book a')]
    comments = [comment.text for comment in soup.select('.texts span')]
    if get_imgs:
        download_image(url_img, title)
    if get_txt:
        download_txt(title, id)
    return {
        'Title': title,
        'Author': author,
        'Image': url_img,
        'Genres': genres,
        'Comments': comments
    }


def check_for_redirect(response):
    if response.history:
        logger.warning('Книги нет. Редирект на главную')
        raise requests.HTTPError


def get_file_ext(url_img):
    cut = urlparse(url_img)
    return os.path.splitext(cut.path)[-1]


def download_txt(title, id, folder='books/'):
    url = f"https://tululu.org/txt.php"
    params = {'id':id}
    response = requests.get(url, params=params)
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


def create_parser():
    parser = argparse.ArgumentParser(description='Ввод диапазона ID книг')
    parser.add_argument('start', nargs='?', default=1,
                        help='С какого ID парсить', type=int)
    parser.add_argument('end', nargs='?',  default=11,
                        help='По какой ID парсить', type=int)
    parser.add_argument('-i', '--get_imgs', action='store_true',
                        default=False, help='Cкачивать обложки книг')
    parser.add_argument('-t', '--get_txt', action='store_true',
                        default=False, help='Cкачивать текст книг')
    return parser


def main():
    fh = logging.FileHandler("log.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")
    fh.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(fh)

    Path("books").mkdir(parents=True, exist_ok=True)
    Path("image").mkdir(parents=True, exist_ok=True)

    parser = create_parser()
    namespace = parser.parse_args()
    start_end_img_txt = (namespace.start, namespace.end, namespace.get_imgs, namespace.get_txt)
    
    books_tag = get_books(start_end_img_txt)
    logger.warning(books_tag)


if __name__ == "__main__":
    main()
