from urllib import request
from urllib import error
from urllib.parse import quote

from fa_scraper import parse

import logging
logger = logging.getLogger('default')

import queue

import time

class Scraper(object):
    BASE_URL = 'https://www.furaffinity.net'

    def open_url(self, url):
        url = quote(url, safe=":/")
        try:
            response = request.urlopen(url, timeout = 10)
        except error.HTTPError as e:
            logger.warning('request sent to %s returned %u.' % (url, e.code))
        except error.URLError as e:
            logger.warning('request sent to %s failed: %s.' % (url, e.reason))

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
            logger.warning("scrapying queue empty.")
            exit(-1)

        image_id = url.replace('/', '').replace('view', '')
        if url in self.scrapied_set:
            logger.debug("image has been scrapied.")
            return

        full_url = Scraper.BASE_URL+ url.replace('view', 'full')
        html = self.open_url(full_url)
        time.sleep(1)
        info = parse.get_artwork_info(html)
        logger.debug("parsed info from artwork site.")

        if "download_link" in info:
            response = self.open_url(info["download_link"])
            time.sleep(1)
            data = response.read()
            with open(image_id, 'wb') as image:
                image.write(data)
                logger.debug("image downloaded.")

        if "artwork_sites" in info:
            for artwork_site in info["artwork_sites"]:
                if not artwork_site in self.scrapied_set:
                    self.scrapying_queue.put(artwork_site)
                else:
                    logger.debug("new site has been scrapied.")

        self.scrapied_set.add(url)
