import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

import dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape



def render_page():
    with open("content/category.json", "r", encoding="utf8") as file:
        category_json = file.read()
    category = json.loads(category_json)
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )
    # print (category)
    template = env.get_template("template.html")
    rendered_page = template.render(
        category=category)
    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)
    

    # env = Environment(
    #     loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    # )
    # winery_age = "Уже {0} с вами".format(get_years(start_year))
    # template = env.get_template("template.html")
    # rendered_page = template.render(
    #     winery_age=winery_age, goods_cards=get_goods(excel_path)
    # )

    # with open("index.html", "w", encoding="utf8") as file:
    #     file.write(rendered_page)





def main():
    render_page()
    dotenv.load_dotenv()
    # excel_path = os.getenv("EXCEL_PATH")
    # start_year = os.getenv("START_YEAR")
    # render_page(excel_path, start_year)
    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()