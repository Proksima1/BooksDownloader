import io
import json
import os
from io import BytesIO
from enum import Enum

import celery
import django

from .BooksParsingTool import searchBooks, parseBook, getPageBooks
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Book, SearchRequest
from .logs import log, LogLevels


@shared_task()
def searchBooksTask(searchRequest: str):
    searchRequest = searchRequest.lower().title().strip()
    channel_layer = get_channel_layer()
    try:
        req = SearchRequest.objects.get(searchRequest__iexact=searchRequest).books
        booksCount = req.count()
        books = [{'title': book.bookName, 'author': book.bookAuthor,
                  'source': book.bookLink.split('books')[0], 'cover': book.bookCover,
                  'downloadUrl': book.bookLink} for book in req.all()[0:10]]
        log(f'Got data from db, request: "{searchRequest}"', LogLevels.info)
    except:
        log(f'Request "{searchRequest}" not found, parsing from site...', LogLevels.warning)
        try:
            request = SearchRequest.objects.create(
                searchRequest=searchRequest
            )
        except django.db.utils.OperationalError:
            request = SearchRequest.objects.get(searchRequest__iexact=searchRequest)
        booksCount, books = searchBooks(searchRequest)
        numPages = booksCount // 20 + 1

        doubles = []
        outputBooks = []
        for i in books:
            if i['title'] not in doubles:
                outputBooks.append(i)
                doubles.append(i['title'])
        books = outputBooks[0:10]
        booksCount = len(books)
        for book in books:
            b = Book(
                bookName=book['title'],
                bookAuthor=book['author'],
                bookCover=book['cover'],
                bookLink=book['downloadUrl'],
            )
            log(f'Saving book "{book["title"]}" to db', LogLevels.info)
            try:
                b.save()
                request.books.add(b)
            except django.db.utils.IntegrityError as e:
                log(f"{book['title']} is in db {e}", LogLevels.info)
        if numPages > 1:
            log(f'Starting to parse all pages from the request {searchRequest}', LogLevels.info)
            getAllBooksByRequest.delay(searchRequest, 2, numPages)
        request.save()
    message = {'type': 'searchResponse', 'message': (booksCount, books)}
    async_to_sync(channel_layer.group_send)(
        'booksGroup', {'type': "send_data", "message": json.dumps(message)}
    )


@shared_task()
def getPageTask(message):
    channel_layer = get_channel_layer()
    searchReq, startCountBooks = message
    searchReq = searchReq.lower().title().strip()
    try:
        books = SearchRequest.objects.get(searchRequest__iexact=searchReq).books
    except SearchRequest.DoesNotExist:
        booksCount = 0
        books = []
    else:
        booksCount = books.count()
        books = [{'title': book.bookName, 'author': book.bookAuthor,
                  'source': book.bookLink.split('books')[0], 'cover': book.bookCover,
                  'downloadUrl': book.bookLink} for book in books.all()]
        books = books[startCountBooks:startCountBooks + 10]
    message = {'type': 'getNewPage', 'message': (booksCount, books)}
    async_to_sync(channel_layer.group_send)(
        'booksGroup', {'type': "send_data", "message": json.dumps(message)}
    )


@shared_task()
def getAllBooksByRequest(searchRequest: str, nowPage: int, numPages: int):
    books = getPageBooks(searchRequest, nowPage)
    request = SearchRequest.objects.get(searchRequest__iexact=searchRequest)
    for book in books:
        b = Book(
            bookName=book['title'],
            bookAuthor=book['author'],
            bookCover=book['cover'],
            bookLink=book['downloadUrl'],
        )
        log(f'Saving book "{book["title"]}" to db', LogLevels.info)
        try:
            b.save()
            request.books.add(b)
        except django.db.utils.IntegrityError:
            print(f"{book['title']} is in db")

    request.save()
    if nowPage < numPages:
        getAllBooksByRequest.delay(searchRequest, nowPage + 1, numPages)


@shared_task()
def parseBooksTask(bookUrl):
    channel_layer = get_channel_layer()
    book = Book.objects.get(bookLink__exact=bookUrl)
    if not bool(book.book):
        log(f'Parsing book "{bookUrl}" to file', LogLevels.info)
        path, fileName = parseBook(bookUrl)
        fileSize = os.path.getsize(path)
        book.bookSize = fileSize
        book.save()
        book.book.save("books/" + fileName, BytesIO(io.open(path, "rb", buffering=5).read()))
        log(f'Saved book')
    else:
        fileName = book.book.name.split('/')[1]
    message = json.dumps({"type": 'parseResponse',
                          "message": {'urlToBook': f'http://127.0.0.1:8000/api/getBook/{book.id}',
                                      'fileName': fileName}})
    async_to_sync(channel_layer.group_send)(
        "booksGroup", {'type': "send_data",
                       "message": message}
    )
