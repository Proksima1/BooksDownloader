from datetime import datetime
import io
from io import BytesIO

from django.db import models


class Log(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    message = models.TextField()

    def __str__(self):
        return self.message


class SearchRequest(models.Model):
    class Meta:
        verbose_name_plural = 'Search requests'

    timestamp = models.DateTimeField(default=datetime.now)
    hashId = models.IntegerField(db_index=True)
    searchData = models.TextField()

    def __str__(self):
        return str(self.hashId)


class FoundBook(models.Model):
    class Meta:
        verbose_name_plural = 'Found books'

    bookLink = models.TextField()
    bookSize = models.IntegerField()
    book = models.FileField()

    def __str__(self):
        return f"{self.bookLink} - {self.bookSize}"


class BooksToSearch(models.Model):
    searchRequest = models.ForeignKey(SearchRequest, on_delete=models.CASCADE)
    book = models.ForeignKey(FoundBook, on_delete=models.CASCADE)

    def __str__(self):
        print(type(self.searchRequest.hashId))
        return f"<Search hashID:{self.searchRequest.hashId} - BookID:{self.book.id} >"