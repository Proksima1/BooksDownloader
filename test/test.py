# import httpx
# data = {'do': 'search', 'subaction': 'search', "search_start": 2, "result_from": 20,
#         "full_search": 0, 'story': 'солнечные часы'}
# cl = httpx.Client(http2=True)
#
# client = httpx.Client(http2=True)
# r = client.post("https://kniga-online.com/", data=data)
# if r.status_code == 200:
#     print(r.text)
# import os
#
# newpath = r'media/books'
# if not os.path.exists(newpath):
#     os.makedirs(newpath)

from alphabet_detector import AlphabetDetector
ad = AlphabetDetector()
print(ad.is_cyrillic('хуй'))
# print(translit('sapiense', reversed=True, strict=True))