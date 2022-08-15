from typing import List, Dict
from .sites import *


class Sites:
    def __init__(self):
        self.collection = [{'domain': '4italka.ru', 'routing': {'download': parseBook4italka,
                                                                'search': None},
                            'settings': {'shouldRender': False}},
                           {'domain': 'kniga-online.com', 'routing': {'download': parseBookKnigaOnline,
                                                                      'search': searchBooksKnigaOnline},
                            'settings': {'shouldRender': False}}]

    def availableForSearch(self) -> List[Dict]:
        availableSites = [site for site in self.collection if site['routing']['search'] is not None]
        return availableSites

    def availableForDownload(self) -> List[Dict]:
        availableSites = [site for site in self.collection if site['routing']['download'] is not None]
        return availableSites

    def checkForAvailabilityToDownload(self, url) -> bool:
        return self.recognizeSite(url) in self.availableForDownload()

    def __getitem__(self, domain) -> Dict:
        return list(filter(lambda x: x['domain'] == domain, self.collection))[0]

    def recognizeSite(self, url: str) -> Dict:
        siteDomain = url.split('//')[1].split('/')[0]
        site = self[siteDomain]
        return site


if __name__ == '__main__':
    s = Sites()
    site = 'https://4italka.ru/123231.html'
    print(s.checkForAvailabilityToDownload(site))
