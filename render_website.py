import json
import os
import os.path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def render_page():
    count_per_page = 10
    with open("content/category.json", "r", encoding="utf8") as file:
        category_json = file.read()
    category = json.loads(category_json)
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )
    books_in_pages = list(chunked(category, count_per_page))

    for page_num, books_catalog in enumerate(books_in_pages, 1):
        books_catalog = [books_card[book_card] for books_card in books_catalog for book_card in books_card]
        # print(books_catalog)
        row_catalog = chunked(books_catalog, 2)
        template = env.get_template("template.html")
        rendered_page = template.render(
            category=row_catalog)
        with open(f"pages/index{page_num}.html", "w", encoding="utf8") as file:
            file.write(rendered_page)
    

   
def main():
    
    
    dotenv.load_dotenv()
    Path("pages").mkdir(parents=True, exist_ok=True)
    # render_page()
    server = Server()
    server.watch('template.html', render_page)
    server.serve(port=5500, root='.')


if __name__ == "__main__":
    main()