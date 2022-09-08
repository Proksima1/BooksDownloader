import io
import json
import os
from io import BytesIO

from .BooksParsingTool import searchBooks, parseBook
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Book, SearchRequest


@shared_task()
def searchBooksTask(searchRequest: str):
    searchRequest = searchRequest.lower().title()
    channel_layer = get_channel_layer()
    try:
        req = SearchRequest.objects.get(searchRequest__iexact=searchRequest)
        books = [{'title': book.bookName, 'author': book.bookAuthor,
                  'source': book.bookLink.split('books')[0], 'cover': book.bookCover,
                  'downloadUrl': book.bookLink} for book in req.books.all()]
    except:
        request = SearchRequest.objects.create(
            searchRequest=searchRequest
        )
        books = searchBooks(searchRequest)
        for book in books:
            b = Book(
                bookName=book['title'],
                bookAuthor=book['author'],
                bookCover=book['cover'],
                bookLink=book['downloadUrl'],
            )
            b.save()
            request.books.add(b)
    message = {'type': 'searchResponse', 'message': books}
    async_to_sync(channel_layer.group_send)(
        'booksGroup', {'type': "send_data", "message": json.dumps(message)}
    )


@shared_task()
def parseBooksTask(bookUrl):
    channel_layer = get_channel_layer()
    book = Book.objects.get(bookLink__exact=bookUrl)
    if not bool(book.book):
        path, fileName = parseBook(bookUrl)
        fileSize = os.path.getsize(path)
        book.bookSize = fileSize
        book.save()
        book.book.save("books/" + fileName, BytesIO(io.open(path, "rb", buffering=5).read()))
    else:
        fileName = book.book.name.split('/')[1]
    message = json.dumps({"type": 'parseResponse',
                          "message": {'urlToBook': f'http://127.0.0.1:8000/api/getBook/{book.id}',
                                      'fileName': fileName}})
    async_to_sync(channel_layer.group_send)(
        "booksGroup", {'type': "send_data",
                       "message": message}
    )
