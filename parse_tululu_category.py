import argparse
import os
import logging
import json
from pathlib import Path
from urllib.parse import urljoin


import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from main import check_for_redirect, get_book


logger = logging.getLogger("logger")


def parse_category_page(soup):
    book_tags = soup.select('.bookimage')
    book_links = [book_tag.select_one('a')['href']
                  for book_tag in book_tags]
    return book_links


def join_url(book_links, url):
    links = [urljoin(url, book_link) for book_link in book_links]
    return links


def save_json(books_tag, json_path, folder):
    filename = f'{json_path}.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(books_tag, file, ensure_ascii=False)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Ввод диапазона страниц каталога книг')
    parser.add_argument('--start_page', nargs='?', default=1,
                        help='С какой страницы парсить', type=int)
    parser.add_argument('--end_page', nargs='?',  default=9999,
                        help='По какую страницу парсить', type=int)
    parser.add_argument('-i', '--get_imgs', action='store_true',
                        default=False, help='Cкачивать обложки книг')
    parser.add_argument('-t', '--get_txt', action='store_true',
                        default=False, help='Cкачивать текст книг')
    parser.add_argument('-j', '--json_path', default='category',
                        help='Указать свой путь к *.json файлу с результатами')
    parser.add_argument('-d', '--dest_folder', default='content/',
                        help='Путь к каталогу с результатами парсинга: картинкам, книгами, json')
    return parser


def main():
    fh = logging.FileHandler("log.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")
    fh.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(fh)
    category_url = "https://tululu.org/l55/"
    parser = create_parser()
    namespace = parser.parse_args()
    Path(namespace.dest_folder).mkdir(parents=True, exist_ok=True)
    start_page = namespace.start_page
    stop_page = namespace.end_page

    links = []
    for page in tqdm(range(start_page, stop_page)):
        try:
            url = f"{category_url}/{page}"
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            links.extend(join_url(parse_category_page(soup), url))
        except requests.HTTPError:
            logger.warning('Нет странички')

    books_tag = [get_book(book_url, namespace.get_imgs, namespace.get_txt,
                          namespace.dest_folder) for book_url in tqdm(links)]
    save_json(books_tag, namespace.json_path, namespace.dest_folder)


if __name__ == "__main__":
    main()
