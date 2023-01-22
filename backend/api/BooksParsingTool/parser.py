from itertools import chain
from typing import List, Dict, Tuple
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


def getPageBooks(searchQ: str, nowPage: int):
    availableSites = Sites().availableSites()
    site = availableSites[0]
    parser = site['class']()
    books = parser.getPage(searchQ, nowPage)
    return books
    # print(books)


def searchBooks(searchQ: str) -> Tuple[int, List[Dict]]:
    availableSites = Sites().availableSites()
    books = []
    allBooks = 0
    for site in availableSites:
        parser = site['class']()
        numBooks, b = parser.search(searchQ)
        allBooks += numBooks
        books.append(b)
    books = list(chain(*books))
    return allBooks, books


if __name__ == '__main__':
    pass
    # recognizeSite(
    #     'https://kniga-online.com/books/fantastika-i-fjentezi/litrpg/295218-stars-unbound-si-kin-aleks.html')
