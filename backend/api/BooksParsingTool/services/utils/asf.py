from collections import deque
from itertools import chain
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from ..tools import clearFromScripts, get_html_and_render, clearFromSpaces, post_html_and_render

BASE_URL = 'https://kniga-online.com/'


def parseOnePage(url):
    text = get_html_and_render(url)
    soup = BeautifulSoup(text, 'html.parser')
    text_block = list(soup.find('div', class_='full-text').children)
    text_list = clearFromScripts([i for i in text_block if not isinstance(i, NavigableString)])
    return text_list


def searchBooksKnigaOnline(searchQ):
    source = post_html_and_render('https://kniga-online.com/', data={'do': 'search', 'subaction': 'search', 'story': searchQ})
    soup = BeautifulSoup(source, 'html.parser')
    books = soup.find_all('div', class_='short')
    data = []
    for book in books:
        desc = book.find('div', class_='short-desc')
        bookName = desc.find_all('div', class_='sd-line')[1].text.split(':')[1].strip()
        author = desc.find_all('div', class_='sd-line')[2].text.split(':')[1].strip()
        bookCover = BASE_URL + book.find('div', class_='short-img').find('img')['src']
        downloadLink = book.find('a', class_='short-title')['href']
        if bookName not in list(map(lambda x: x['title'], data)):
            data.append({'title': bookName, 'author': author,
                         'source': BASE_URL, 'cover': bookCover, 'downloadUrl': downloadLink})
    return data


def parseBookKnigaOnline(source):
    soup = BeautifulSoup(source, 'html.parser')
    book_name = soup.find('div', class_='finfo').find_all('div', class_='sd-line')[1].find('span').next_sibling.strip()
    author = soup.find('div', class_='finfo').find_all('div', class_='sd-line')[2].find('a').text
    numberOfPages = soup.find('span', class_='navigation').children
    url = soup.find("meta", property="og:url")['content']
    url = url.rsplit('/', maxsplit=1)
    url.insert(1, '/page-{0}-')
    url = ''.join(url)
    lastPageNum = int(deque(numberOfPages, 1)[0].text)  # берет последний элемент в списке
    fulltext = []
    for page_num in range(1, lastPageNum + 1):
        print(f'Parsing {page_num} page')
        fulltext.append(parseOnePage(url.format(page_num)))
    fulltext = list(chain(*fulltext))
    fulltext = ' '.join(clearFromSpaces(fulltext))
    return fulltext, book_name, author
