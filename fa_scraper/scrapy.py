from urllib import request
from urllib import error

from fa_scraper import parse

import logging
logger = logging.getLogger('default')

import queue

import time

class Scraper(object):
    BASE_URL = 'https://www.furaffinity.net'

    def open_url(self, url):
        try:
            response = request.urlopen(url, timeout = 10)
        except error.HTTPError as e:
            logger.warn('request sent to %s returned %u.' % (url, e.code))
        except error.URLError as e:
            logger.warn('request sent to %s failed: %s.' % (url, e.reason))

        logger.debug('receive response from \'%s\'' % url)
        return response

    def __init__(self):
        self.scrapied_set = set()
        self.scrapying_queue = queue.Queue()

        main_html = self.open_url(Scraper.BASE_URL)
        time.sleep(1)
        if main_html:
            artwork_info = parse.get_artwork_info(main_html)
            if "artwork_sites" in artwork_info:
                for artwork_site in artwork_info["artwork_sites"]:
                    self.scrapying_queue.put(artwork_site)

        logger.debug("scraper instance initialized.")



    def next_arkwork(self):
        try:
            url = self.scrapying_queue.get()
        except Empty:
            pass

        image_id = url.replace('/view/', '').replace('/', '')
        url = Scraper.BASE_URL+ url.replace('view', 'full')
        result = parse.get_artwork_info(self.open_url(url))

        print(result)
        image_data = self.open_url(result["download_link"]).read()
        time.sleep(1)
        with open(image_id, 'wb') as image:
            image.write(image_data)

        artwork_sites = result["artwork_sites"]
        for artwork_site in artwork_sites:
            self.scrapying_queue.put(artwork_site)
