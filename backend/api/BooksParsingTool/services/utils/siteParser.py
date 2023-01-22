import os
from abc import ABC, abstractmethod
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .tools import generateBookName, convert_to_fb2


class Parser(ABC):
    def __init__(self):
        self.BASE_URL = ''

    @abstractmethod
    def search(self, searchRequest: str) -> List:
        raise NotImplementedError

    @abstractmethod
    def parse(self, url: str) -> List:
        raise NotImplementedError

    @abstractmethod
    def getPage(self, searchRequest: str, nowPage: int) -> List:
        raise NotImplementedError

    def writeFile(self, bookData: tuple) -> Tuple:
        """
            :param bookData: pagesList, BookName, Author
            :return: Tuple
        """
        text_list, book_name, author = bookData
        path = 'media/books'
        filename = generateBookName(book_name, author)
        pathToFileH = os.path.join(path, filename)
        with open(f'{pathToFileH}.html', 'w+', encoding='utf-8') as writer:
            writer.write(
                f'<!doctype html>\n<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport"'
                f' content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, '
                f'minimum-scale=1.0"> '
                f'<meta http-equiv="X-UA-Compatible" content="ie=edge"><title>{book_name}</title></head><body>')
            writer.write(text_list)
            writer.write('</body></html>')
        pathToFile = convert_to_fb2(pathToFileH, author)
        return pathToFile, filename + '.fb2'
