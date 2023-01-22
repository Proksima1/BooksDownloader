from django.urls import re_path
from .consumers import WSSearch
ws_urlpattern = [
    re_path('ws/search', WSSearch.as_asgi()),
]