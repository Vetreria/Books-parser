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


def get_books(start_id, end_id, get_imgs, get_txt):
    books_tag = {}
    for book_id in tqdm(range(start_id, end_id + 1), desc="Собираем книжки"):
        while True:
            try:
                url = f"https://tululu.org/b{book_id}/"
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                books_tag[book_id] = parse_book_page(
                    response, url)
                if get_imgs:
                    download_image(
                        books_tag[book_id]['Image'], str(book_id))
                if get_txt:
                    download_txt(books_tag[book_id]['Title'], book_id)
                break
            except requests.HTTPError:
                logger.warning('Книга не найдена')
                break
            except requests.ConnectionError:
                logger.warning('Нет связи, повторная попытка через 10 сек.')
                sleep(10)
    return books_tag


def parse_book_page(response, url):
    soup = BeautifulSoup(response.text, 'lxml')
    author_title = soup.select_one('#content h1').text
    title, author = [name.strip() for name in author_title.split('::')]
    book_img = soup.select_one('div.bookimage img')['src']
    img_url = (urljoin(url, book_img))
    genres = [genre.text for genre in soup.select('span.d_book a')]
    comments = [comment.text for comment in soup.select('.texts span')]
    return {
        'Title': title,
        'Author': author,
        'Image': img_url,
        'Genres': genres,
        'Comments': comments
    }


def check_for_redirect(response):
    if response.history:
        logger.warning('Книги нет. Редирект на главную')
        raise requests.HTTPError


def get_file_ext(img_url):
    split_url = urlparse(img_url)
    return os.path.splitext(split_url.path)[-1]


def download_txt(title, book_id, folder='books/'):
    url = f"https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f"{book_id}.{title}.txt"
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(img_url, title, folder='image/'):
    response = requests.get(img_url)
    response.raise_for_status()
    check_for_redirect(response)
    file_ext = get_file_ext(img_url)
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
    start_id, end_id, get_imgs, get_txt = (namespace.start, namespace.end,
                                           namespace.get_imgs, namespace.get_txt)
    books_tag = get_books(start_id, end_id, get_imgs, get_txt)
    logger.warning(books_tag)


if __name__ == "__main__":
    main()
