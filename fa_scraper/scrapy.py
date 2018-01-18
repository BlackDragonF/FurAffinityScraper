from urllib import request
from urllib import error

# from bs4 import BeautifulSoup
from fa_scraper import parse

import logging
logger = logging.getLogger('default')

# import re

import queue

class Scraper(object):
    BASE_URL = 'https://www.furaffinity.net'

    def open_url(self, url):
        try:
            response = request.urlopen(url)
        except HTTPError as error:
            logger.warn('request sent to %s returned %u.' % (url, error.code))
        except URLError as error:
            logger.warn('request sent to %s failed: %s.' % (url, error.reason))

        logger.debug('receive response from \'%s\'' % url)
        return response

    # def expand_urls(self, bs):
    #
    #     for artwork in artworks:
    #         self.scrapying_queue.put(artwork["href"])

    def __init__(self):
        self.scrapied_set = set()
        self.scrapying_queue = queue.Queue()

        artwork_sites = parse.parse_artwork_site(request.urlopen(Scraper.BASE_URL))["artwork_sites"]
        for artwork_site in artwork_sites:
            self.scrapying_queue.put(artwork_site["href"])




    def next_arkwork(self):
        try:
            url = self.scrapying_queue.get()
        except Empty:
            pass

        image_id = url.replace('/view/', '').replace('/', '')
        url = Scraper.BASE_URL+ url.replace('view', 'full')
        result = parse.parse_artwork_site(request.urlopen(url))

        print(result["download_link"])
        image_data = request.urlopen(result["download_link"]).read()
        with open(image_id, 'wb') as image:
            image.write(image_data)

        artwork_sites = result["artwork_sites"]
        for artwork_site in artwork_sites:
            self.scrapying_queue.put(artwork_site)
