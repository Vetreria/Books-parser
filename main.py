from pprint import pprint
from urllib.parse import urljoin
from urllib.parse import urlparse
from pathlib import Path
import argparse
import os


import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


def get_book(books_tag, start_end):
    start_id, end_id = start_end
    for id in tqdm(range(start_id, end_id + 1), desc="Собираем книжки"):
        try:
            url = f"https://tululu.org/b{id}/"
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            books_tag[id] = parse_book_page(
                response)  
        except:
            continue
    return books_tag


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split("::")[0].strip(" \xa0 ")
    author = soup.find('h1').text.split("::")[1].strip(" \xa0 ")
    book_img_id = soup.find(class_='bookimage').find('img')['src']
    url_img = (urljoin('https://tululu.org/', book_img_id))
    genres = [genre.text for genre in soup.select('span.d_book a')]
    comments = [comment.text for comment in soup.select('.texts span')]
    return {
                'Название': title,
                'Автор': author,
                'Картинка': url_img,
                'Жанр': genres,
                'Отзывы': comments
            }


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_file_ext(url_img):
    cut = urlparse(url_img)
    return os.path.splitext(cut.path)[-1]


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


def create_parser():
    parser = argparse.ArgumentParser(description='Ввод диапазона ID книг')
    parser.add_argument('start', nargs='?', default=1,
                        help='С какого ID парсить', type=int)
    parser.add_argument('end', nargs='?',  default=11,
                        help='По какой ID парсить', type=int)
    parser.add_argument('-i', '--get_imgs', action='store_true', default=False, help='Cкачивать обложки книг')
    parser.add_argument('-t', '--get_txt', action='store_true', default=False, help='Cкачивать текст книг')
    return parser


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("image").mkdir(parents=True, exist_ok=True)
    parser = create_parser()
    namespace = parser.parse_args()
    start_end = (namespace.start, namespace.end)
    books_tag = {}
    get_book(books_tag, start_end)
    pprint(books_tag)
    if namespace.get_imgs:
        for id in tqdm(books_tag.keys(), desc="Скачиваем обложки"):
            download_image(books_tag[id]['Картинка'], books_tag[id]['Название'])
    if namespace.get_txt:
        for id in tqdm(books_tag.keys(), desc="Скачиваем книжки"):
            download_txt(books_tag[id]['Название'], id)



if __name__ == "__main__":
    main()
