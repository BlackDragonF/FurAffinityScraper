from urllib import request
from urllib import error
from urllib.parse import quote

from fa_scraper import parse

from fa_scraper import util

import logging
logger = logging.getLogger('default')

import queue

import time

class Scraper(object):

    BASE_URL = 'https://www.furaffinity.net'
    URL_TYPES = ['view', 'gallery', 'favorites', 'user']

    @staticmethod
    def open_url(url):
        url = quote(url, safe=':/')
        try:
            response = request.urlopen(url, timeout = 10)
            time.sleep(1)
            logger.debug('received response from "%s"' % url)
            return response
        except error.HTTPError as e:
            logger.warning('request sent to %s returned %u.' % (url, e.code))
        except error.URLError as e:
            logger.warning('request sent to %s failed: %s.' % (url, e.reason))

    def get_scrapying_url(self):
        try:
            return self.scrapying_queue.get()
        except Empty:
            logger.warning('scrapying queue empty.')

    def add_unscrapied_urls(self, sites):
        site_count = 0
        for site in sites:
            if not site in self.scrapied_set:
                self.scrapying_queue.put(site)
                site_count = site_count + 1
        logger.info('added %d sites to unscrapied queue.' % site_count)

    def add_scrapied_url(self, url):
        self.scrapied_set.add(url)

    def __init__(self):
        self.scrapied_set = set()
        self.scrapying_queue = queue.Queue()

        main_html = Scraper.open_url(Scraper.BASE_URL)
        if main_html:
            parser = parse.Parser(main_html)
            sites = parser.get_page_links()
            self.add_unscrapied_urls(sites)

        logger.debug('scraper initialized.')

    def scrapy_pending_url(self):
        url = self.get_scrapying_url()
        origin_url = url

        url_type = util.get_url_type(url, Scraper.URL_TYPES)
        if url_type == 'view':
            url = util.get_fullview_url(url)
        elif url_type == 'unknown':
            logger.info('skipped unknown url %s' % url)
            return

        html = Scraper.open_url(Scraper.BASE_URL + url)
        if html:
            logger.debug('scrapied site with url type: %s' % url_type)
            if url_type == 'view':
                parser = parse.ArtworkParser(html)
                download_link = parser.get_download_link()
                if download_link:
                    filename = util.combine_filename(parser.get_artwork_id(url), parser.get_filename_extension(download_link))
                    Scraper.download_artwork(filename, download_link)
            else:
                parser = parse.Parser(html)

            sites = parser.get_page_links()
            self.add_unscrapied_urls(sites)
            self.add_scrapied_url(origin_url)


    @staticmethod
    def download_artwork(filename, download_link):
        response = Scraper.open_url(download_link)
        data = response.read()
        with open('images/' + filename, 'wb') as image:
            image.write(data)
            logger.debug('image downloaded.')








    # def next_arkwork(self):
    #     try:
    #         url = self.scrapying_queue.get()
    #     except Empty:
    #         logger.warning('scrapying queue empty.')
    #         exit(-1)
    #
    #     image_id = url.replace('/', '').replace('view', '')
    #     if url in self.scrapied_set:
    #         logger.debug('image has been scrapied.')
    #         return
    #
    #     full_url = Scraper.BASE_URL+ url.replace('view', 'full')
    #     html = self.open_url(full_url)
    #     info = parse.get_artwork_info(html)
    #     logger.debug('parsed info from artwork site.')
    #
    #     if 'download_link' in info:
    #         response = self.open_url(info['download_link'])
    #         data = response.read()
    #         with open(image_id, 'wb') as image:
    #             image.write(data)
    #             logger.debug('image downloaded.')
    #
    #     if 'artwork_sites' in info:
    #         for artwork_site in info['artwork_sites']:
    #             if not artwork_site in self.scrapied_set:
    #                 self.scrapying_queue.put(artwork_site)
    #             else:
    #                 logger.debug('new site has been scrapied.')
    #
    #     self.scrapied_set.add(url)
