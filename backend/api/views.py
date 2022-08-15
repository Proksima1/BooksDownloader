from datetime import datetime

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .models import *
# from .BooksParsingTool import recognizeSite
from .serializers import BooksToSearchSerializer
# from .tasks import test

# Create your views here.


@api_view(["GET"])
def startParse(request):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(hash(n))
    # ser = BooksToSearchSerializer(b, many=True)
    return Response("hello")


def getBook(request, id: int):
    bookM = FoundBook.objects.get(pk=id)
    return HttpResponse(bookM.book, content_type="application/xml")
