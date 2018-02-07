from urllib import request
from urllib import error
from urllib.parse import quote

import requests
import cfscrape

from fa_scraper import parse
from fa_scraper import util
from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

import queue

import time

class Scraper(object):
    @staticmethod
    def generate_user_agent():
        return random.choice(USER_AGENTS)

    def open_url(self, url):
        url = quote(url, safe = ':/')
        response = self.scraper.get(url)
        if response.status_code == 200:
            logger.debug('received response from "%s".' % url)
        else:
            logger.warning('request sent to "%s" return %u.' % (url, response.status_code))

        time.sleep(10)
        return response.content

        # url = quote(url, safe=':/')
        # try:
        #     r = request.Request(url)
        #     r.add_header('User-Agent', Scraper.generate_user_agent())
        #     response = request.urlopen(r, timeout = 10)
        #     logger.debug('received response from "%s"' % url)
        #     return response
        # except error.HTTPError as e:
        #     logger.warning('request sent to %s returned %u.' % (url, e.code))
        # except error.URLError as e:
        #     logger.warning('request sent to %s failed: %s.' % (url, e.reason))
        # finally:
        #     time.sleep(10)

    def get_scrapying_url(self):
        try:
            return self.scrapying_queue.get(False)
        except queue.Empty:
            logger.error('scrapying queue empty.')
            exit(-1)

    def add_unscrapied_urls(self, urls):
        url_count = 0
        for url in urls:
            if not url in self.scrapied_set:
                self.scrapying_queue.put(url)
                url_count = url_count + 1
        logger.info('added %d urls to unscrapied queue.' % url_count)

    def add_scrapied_url(self, url):
        self.scrapied_set.add(url)

    def __init__(self):
        self.scrapied_set = set()
        self.scrapying_queue = queue.Queue()

        self.scraper = cfscrape.create_scraper()

        main_html = self.open_url(BASE_URL)
        if main_html:
            parser = parse.Parser(main_html)
            sites = parser.get_all_urls()
            self.add_unscrapied_urls(sites)

        logger.debug('scraper initialized.')

    def scrapy_pending_url(self):
        url = self.get_scrapying_url()
        if not url or url in self.scrapied_set:
            logger.debug('failed to get url/url has been scrapied.')
            return None
        origin_url = url

        url_type = parse.Parser.get_url_type(url)
        if url_type == 'unknown':
            logger.info('skipped unknown url "%s".' % url)
            return None

        if url_type == 'view':
            url = parse.ArtworkParser.view_to_full(url)
        html = self.open_url(BASE_URL + url)
        if html:
            logger.debug('scrapied site with url type: %s.' % url_type)

            parser = parse.ArtworkParser(html) if url_type == 'view' else parse.Parser(html)

            urls = parser.get_all_urls()
            self.add_unscrapied_urls(urls)
            self.add_scrapied_url(origin_url)

            if url_type == 'view':
                attributes = parser.get_artwork_attributes()

                download_link = parser.get_download_link()
                if download_link and attributes['Category'] == 'Artwork (Digital)':
                    ID = self.get_artwork_id(url)

                    filename = util.combine_filename(ID, parser.get_filename_extension(download_link))
                    self.download_artwork(filename, download_link)

                    attributes['ID'] = int(ID)
                    return attributes

    @staticmethod
    def get_artwork_id(url):
        return url.replace('/', '').replace('full', '')

    def download_artwork(self, filename, download_link):
        data = self.open_url(download_link)
        if not data:
            return False
        try:
            with open('images/' + filename, 'wb') as image:
                image.write(data)
                logger.debug('image "%s" downloaded.' % filename)
                return True
        except EnvironmentError:
            logger.warning('failed to download image "%s"' % filename)
            return False
