import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlparse
from pprint import pprint



# def get_file_ext(url_img):
#     cut = urlparse(url_img)
#     return os.path.splitext(cut.path)[-1]


def find_book(books_tag):
    for id in range(1, 11):
        url = f"https://tululu.org/b{id}/"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            title, url_img, categorys, comments, author = parse_book_page(response)
            books_tag[id] = {
                'Название': title,
                'Автор': author,
                'Картинка': url_img,
                'Жанр': categorys,
                'Отзывы': comments
            }
        except:
            print(f'Книгa не найденa!')
            continue
    return books_tag
        # title, url_img = find_tag(response)
        # try:
        #     response.raise_for_status()
        #     check_for_redirect(response)
        #     title, url_img = find_tag(response)
        #     # download_txt(title, id)
        #     # download_image(url_img, title)
        # except:
        #     print(f'Книги не найдено! Пропускаем!')
        #     continue



def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text
    title_split = title_text.split("::")
    title = title_split[0].strip(" \xa0 ")
    author = title_split[1].strip(" \xa0 ")
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


# def download_txt(title, id, folder='books/'):
#     url = f"https://tululu.org/txt.php?id={id}/"
#     response = requests.get(url)
#     response.raise_for_status()
#     filename = f"{id}.{title}.txt"
#     filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')
#     with open(filepath, 'wb') as file:
#         file.write(response.content)


# def download_image(url_img, title, folder='image/'):
#     response = requests.get(url_img)
#     response.raise_for_status()
#     file_ext = get_file_ext(url_img)
#     filepath = os.path.join(folder, sanitize_filename(title) + file_ext)
#     with open(filepath, 'wb') as file:
#         file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    books_tag = {}
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("image").mkdir(parents=True, exist_ok=True)
    find_book(books_tag)
    pprint(books_tag)


if __name__ == "__main__":
    main()