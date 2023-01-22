import hashlib
import os
import random
import string
from typing import List, Callable

import httpx
from transliterate import translit
from bs4.element import PageElement
from requests_html import HTMLSession
import base64
import re


def get_html(url: str, data=None):
    client = httpx.Client(http2=True)
    r = client.get(url, params=data)
    if r.status_code == 200:
        return r.text
    return None


def post_html(url: str, data=None):
    client = httpx.Client(http2=True)
    r = client.post(url, data=data)
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
