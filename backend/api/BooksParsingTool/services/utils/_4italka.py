from bs4 import BeautifulSoup
import sys
# sys.path.append("..")
from ..tools import clearFromSpaces


def parseBook4italka(source):
    soup = BeautifulSoup(source, 'html.parser')
    book_name = soup.find('div', class_='book-cover-text').find('h1').text
    author = soup.find_all('div', class_='m-v-5')[1].find('a').text
    author = ' '.join(author.split()[::2]) if len(author.split()) > 2 else author
    book = soup.find('div', class_='text-content').children
    text_list = ' '.join(clearFromSpaces([i for i in book]))
    return text_list, book_name, author