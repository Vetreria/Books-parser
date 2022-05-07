import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlparse
from pprint import pprint
import argparse


def find_book(books_tag, start_id, end_id):
    for id in range(start_id, end_id + 1):
        try:
            url = f"https://tululu.org/b{id}/"
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            title, url_img, categorys, comments, author = parse_book_page(
                response)
            books_tag[id] = {
                'Название': title,
                'Автор': author,
                'Картинка': url_img,
                'Жанр': categorys,
                'Отзывы': comments
            }
        except:
            print(f'Книгa {id} не найденa!')
            continue
    return books_tag


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split("::")[0].strip(" \xa0 ")
    author = soup.find('h1').text.split("::")[1].strip(" \xa0 ")
    book_img_id = soup.find(class_='bookimage').find('img')['src']
    url_img = (urljoin('https://tululu.org/', book_img_id))
    categorys = []
    comments = []
    try:
        for comment in soup.select('.texts span'):
            comments.append(comment.text)
        for category in soup.select('span.d_book a'):
            categorys.append(category.text)
    except:
        print("Комментариев нет")
    return title, url_img, categorys, comments, author


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def create_parser():
    parser = argparse.ArgumentParser(description='Ввод диапазона ID книг')
    parser.add_argument('start', nargs='?', default=1,
                        help='С какого ID парсить', type=int)
    parser.add_argument('end', nargs='?',  default=11,
                        help='По какой ID парсить', type=int)
    return parser


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    start_id, end_id = namespace.start, namespace.end
    books_tag = {}
    find_book(books_tag, start_id, end_id)
    pprint(books_tag)


if __name__ == "__main__":
    main()
