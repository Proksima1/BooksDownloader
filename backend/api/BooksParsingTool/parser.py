from itertools import chain
from typing import List, Dict
from .services import *


def parseBook(url: str):
    """route - download/search"""
    siteGiver = Sites()
    if siteGiver.checkForAvailability(url):
        site = siteGiver.recognizeSite(url)
        parser = site['class']()
        print(f'Starting to parse {url}')
        data = parser.parse(url)
        return data
    return None


def searchBooks(searchQ: str) -> List[Dict]:
    availableSites = Sites().availableSites()
    books = []
    for site in availableSites:
        parser = site['class']()
        books.append(parser.search(searchQ))
    books = list(chain(*books))
    return books


if __name__ == '__main__':
    pass
    # recognizeSite(
    #     'https://kniga-online.com/books/fantastika-i-fjentezi/litrpg/295218-stars-unbound-si-kin-aleks.html')
