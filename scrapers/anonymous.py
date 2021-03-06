from functools import reduce
from typing import Iterable, Optional, Set
import operator
import re
from bs4 import BeautifulSoup
from utils import log, soup_from_url, Recipe, URL, Source


MAIN_PAGE_URL = "https://veg.anonymous.org.il/cat12.html"
CATEGORY_PATTERN = re.compile("cat[0-9]+.html")
BASE = "https://veg.anonymous.org.il/"


def fetch_recipes() -> Iterable[Recipe]:
    index = soup_from_url(MAIN_PAGE_URL)

    for link in get_categories_links(index):
        link = (BASE + link) if "https" not in link else link
        log("category: " + link)
        page = soup_from_url(link)
        yield from recipes_in_category(page)


def get_categories_links(main_page: BeautifulSoup) -> Set[URL]:
    def all_links():
        for tag in main_page.find_all(href=CATEGORY_PATTERN):
            yield tag.attrs["href"]

    # converting to set to mitigate duplicates
    return set(all_links())


def recipes_in_category(category_page: BeautifulSoup) -> Iterable[Recipe]:
    for item in category_page.find_all(class_="subcategoryItem"):
        a_tag = item.find("a")

        yield parse_recipe(url=a_tag.attrs["href"],
                           title=a_tag.text.strip())


def parse_recipe(url: URL, title: str) -> Recipe:
    log("recipe: " + url)
    page = soup_from_url(BASE + url)

    def ingredients_gen():
        for ing in page.find_all(class_="ingredient"):
            yield ing.text

    # concatenate the ingredients into one string
    ingredients = reduce(operator.add, ingredients_gen(), "")

    thumbnail_url = find_recipe_thumbnail(page)

    return Recipe(
        title=title,
        url=url,
        ingredients=ingredients,
        thumbnail=thumbnail_url if thumbnail_url is not None else "",
        source=Source.ANONYMOUS)


def find_recipe_thumbnail(recipe_page: BeautifulSoup) -> Optional[URL]:
    image_div = recipe_page.find(class_="recipe_image")
    if image_div:
        return image_div.find("img").attrs["src"]
    return None
