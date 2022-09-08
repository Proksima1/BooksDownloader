import os
import time


from .siteParser import *
from collections import deque
from itertools import chain
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from .tools import clearFromScripts, get_html_and_render, post_html_and_render, clearFromSpaces


class KnigaOnlineParser(Parser):
    def __init__(self):
        super(KnigaOnlineParser, self).__init__()
        self.BASE_URL = 'https://kniga-online.com/'
        self.shouldRender = False

    def search(self, searchRequest: str) -> List:
        source = post_html_and_render(self.BASE_URL,
                                      data={'do': 'search', 'subaction': 'search', 'story': searchRequest})
        soup = BeautifulSoup(source, 'html.parser')
        books = soup.find_all('div', class_='short')
        data = []
        for book in books:
            desc = book.find('div', class_='short-desc')
            bookName = desc.find_all('div', class_='sd-line')[1].text.split(':')[1].strip()
            author = desc.find_all('div', class_='sd-line')[2].text.split(':')[1].strip()
            bookCover = self.BASE_URL + book.find('div', class_='short-img').find('img')['src']
            downloadLink = book.find('a', class_='short-title')['href']
            if bookName not in list(map(lambda x: x['title'], data)):
                data.append({'title': bookName, 'author': author,
                             'source': self.BASE_URL, 'cover': bookCover, 'downloadUrl': downloadLink})
        return data

    def parse(self, url: str) -> Tuple:
        return self.writeFile(self._parse(url))

    def _parse(self, url: str) -> Tuple:
        source = post_html_and_render(url)
        soup = BeautifulSoup(source, 'html.parser')
        book_name = soup.find('div', class_='finfo').find_all('div', class_='sd-line')[1].find(
            'span').next_sibling.strip()
        author = soup.find('div', class_='finfo').find_all('div', class_='sd-line')[2].find('a').text
        numberOfPages = soup.find('span', class_='navigation').children
        url = soup.find("meta", property="og:url")['content']
        url = url.rsplit('/', maxsplit=1)
        url.insert(1, '/page-{0}-')
        url = ''.join(url)
        lastPageNum = int(deque(numberOfPages, 1)[0].text)  # берет последний элемент в списке
        fulltext = []
        links = [(u - 1, url.format(u)) for u in range(1, lastPageNum + 1)]
        with ThreadPoolExecutor(max_workers=10) as executor:
            processes = [executor.submit(self._parseOnePage, link) for link in links]
        for future in as_completed(processes):
            fulltext.append(future.result())
        fulltext = list(map(lambda x: x[1], sorted(fulltext, key=lambda x: x[0])))
        fulltext = list(chain(*fulltext))
        fulltext = ' '.join(clearFromSpaces(fulltext))
        return fulltext, book_name, author

    def _parseOnePage(self, data):
        pageNum, url = data
        print(f'Parsing {pageNum} page')
        text = get_html_and_render(url)
        soup = BeautifulSoup(text, 'html.parser')
        text_block = list(soup.find('div', class_='full-text').children)
        text_list = clearFromScripts([i for i in text_block if not isinstance(i, NavigableString)])
        return pageNum, text_list
