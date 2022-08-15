import io
import json
import os
import time
from io import BytesIO

from .BooksParsingTool import searchBooks, parseBook
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import FoundBook


@shared_task()
def searchBooksTask(searchRequest):
    channel_layer = get_channel_layer()
    books = searchBooks(searchRequest)
    message = {'type': 'searchResponse', 'message': books}
    async_to_sync(channel_layer.group_send)(
        'booksGroup', {'type': "send_data", "message": json.dumps(message)}
    )


@shared_task()
def parseBooksTask(bookUrl):
    channel_layer = get_channel_layer()
    path, fileName = parseBook(bookUrl)
    fileSize = os.path.getsize(path)
    book = FoundBook(
        bookLink=bookUrl,
        bookSize=fileSize,
    )
    book.save()
    book.book.save("books/" + fileName, BytesIO(io.open(path, "rb", buffering=5).read()))
    message = json.dumps({"type": 'parseResponse',
                          "message": {'urlToBook': f'http://127.0.0.1:8000/api/getBook/{book.id}',
                                      'fileName': fileName}})
    async_to_sync(channel_layer.group_send)(
        "booksGroup", {'type': "send_data",
                       "message": message}
    )
