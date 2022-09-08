from datetime import datetime

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .models import *


def getBook(request, id: int):
    bookM = Book.objects.get(pk=id)
    return HttpResponse(bookM.book, content_type="application/xml")
