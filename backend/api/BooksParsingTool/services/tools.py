import hashlib
import os
import random
import string
from typing import List, Callable
from transliterate import translit
from bs4.element import PageElement
from requests_html import HTMLSession
import base64
import re


def get_html_and_render(url: str, render=False, data=None):
    session = HTMLSession()
    r = session.get(url, data=data)
    if render:
        r.html.render(timeout=20)
    if r.status_code == 200:
        return r.text
    return None


def post_html_and_render(url: str, render=False, data=None):
    session = HTMLSession()
    r = session.post(url, data=data)
    if render:
        r.html.render(timeout=20)
    if r.status_code == 200:
        return r.text
    return None


def clearFromScripts(l: List[PageElement]) -> list:
    l = [i for i in l if i.name != 'script']
    return l


def clearFromSpaces(text_list: list) -> list:
    cleared_list = [value for value in text_list if value not in ['\n', ' ']]
    cleared_list = list(map(str, cleared_list))
    return cleared_list


def generateBookName(bookName, author):
    res = ''.join((random.choice(string.ascii_letters)) for _ in range(100))
    book = f'{translit(bookName, reversed=True)}_{translit(author, reversed=True)}_{hashlib.md5(res.encode("utf - 8")).hexdigest()}'
    book = re.sub(r'[^\w\s]', '', book)  # Очистка от знаков препинания
    return book.replace(' ', '_')


def convert_to_fb2(filename: str, author: str):
    dir = os.path.abspath(__file__).rsplit('\\', maxsplit=1)[0]
    path = os.path.join(dir, 'h2fb2.py')
    os.system(f'python {path} "{filename}.html" -a "{author}"')
    return filename + '.fb2'


def writeBookInFile(source: str, parseFunc: Callable):
    text_list, book_name, author = parseFunc(source)
    path = 'media/books'
    filename = generateBookName(book_name, author)
    pathToFile = os.path.join(path, filename)
    with open(f'{pathToFile}.html', 'w+', encoding='utf-8') as writer:
        writer.write(
            f'<!doctype html>\n<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport"'
            f' content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">'
            f'<meta http-equiv="X-UA-Compatible" content="ie=edge"><title>{book_name}</title></head><body>')
        writer.write(text_list)
        writer.write('</body></html>')
    filePath = convert_to_fb2(pathToFile, author)
    return filePath, filename + '.fb2'
