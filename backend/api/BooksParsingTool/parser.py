from itertools import chain
from typing import List, Dict

from .services import *


def parseBook(url: str):
    """route - download/search"""
    siteGiver = Sites()
    if siteGiver.checkForAvailabilityToDownload(url):
        site = siteGiver.recognizeSite(url)
        shouldRender = site['settings']['shouldRender']
        text = get_html_and_render(url, render=shouldRender)
        print(f'Starting to parse {url}')
        data = writeBookInFile(text, parseFunc=site['routing']['download'])
        return data
    return None


def searchBooks(searchQ) -> List[Dict]:
    availableSites = Sites().availableForSearch()
    books = []
    for site in availableSites:
        searchF = site['routing']['search']
        books.append(searchF(searchQ))
    books = list(chain(*books))
    return books


if __name__ == '__main__':
    pass
    # recognizeSite(
    #     'https://kniga-online.com/books/fantastika-i-fjentezi/litrpg/295218-stars-unbound-si-kin-aleks.html')
