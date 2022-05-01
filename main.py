import requests
import os
import dotenv
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def find_url():
    for id in range(1, 11):
        url = f"https://tululu.org/b{id}/"
        response = requests.get(url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            title = find_tag(response)
            download_txt(title, id)
        except:
            print(f'Книги не найдено! Пропускаем!')
            continue


def find_tag(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text
    title_split = title_text.split("::")
    title = title_split[0].strip(" \xa0 ")
    print(title)
    return title


def download_txt(title, id, folder='books/'):
    url = f"https://tululu.org/txt.php?id={id}/"
    response = requests.get(url)
    response.raise_for_status()
    filename = f"{id}.{title}.txt"
    filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    dotenv.load_dotenv()
    find_url()


if __name__ == "__main__":
    main()