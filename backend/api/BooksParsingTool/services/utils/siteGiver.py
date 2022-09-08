from typing import List, Dict
from .knigaOnline import KnigaOnlineParser


class Sites:
    def __init__(self):
        self.collection = [{'domain': '4italka.ru', 'class': None},
                           {'domain': 'kniga-online.com', 'class': KnigaOnlineParser}]

    def availableSites(self):
        return [site for site in self.collection if site['class'] is not None]

    def checkForAvailability(self, url) -> bool:
        return self.recognizeSite(url) in self.availableSites()

    def __getitem__(self, domain) -> Dict:
        return list(filter(lambda x: x['domain'] == domain, self.collection))[0]

    def recognizeSite(self, url: str) -> Dict:
        siteDomain = url.split('//')[1].split('/')[0]
        site = self[siteDomain]
        return site


if __name__ == '__main__':
    s = Sites()
    site = 'https://4italka.ru/123231.html'
    print(s.checkForAvailability(site))
