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
    SCRAPIED_BASE = False

    @staticmethod
    def generate_user_agent():
        return random.choice(USER_AGENTS)

    def open_url(self, url):
        url = quote(url, safe = ':/')

        try:
            response = self.scraper.get(url, timeout = 30)
        except:
            logger.warning('error when sending request to "%s".' % url)
            return None

        if response.status_code == 200:
            logger.debug('received response from "%s".' % url)
        else:
            logger.warning('request sent to "%s" returned error code: %u.' % (url, response.status_code))

        time.sleep(10)
        return response.content

    def get_scrapying_url(self):
        try:
            return self.scrapying_queue.get(False)
        except queue.Empty:
            logger.fatal('scrapying queue empty.')
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

        logger.debug('scraper initialized.')

    def scrapy_pending_url(self):
        if not Scraper.SCRAPIED_BASE:
            main_html = self.open_url(BASE_URL)
            if main_html:
                parser = parse.Parser(main_html)
                sites = parser.get_all_urls()
                self.add_unscrapied_urls(sites)
                logger.debug('base url scrapied.')
                Scraper.SCRAPIED_BASE = True

        url = self.get_scrapying_url()
        if not url:
            logger.warning('failed to get url.')
            return None
        elif url in self.scrapied_set:
            logger.debug('url has been scrapied.')
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
            logger.info('scrapied "%s" site with url %s.' % (url_type, url))

            parser = parse.ArtworkParser(html) if url_type == 'view' else parse.Parser(html)

            urls = parser.get_all_urls()
            self.add_unscrapied_urls(urls)

            if url_type == 'view':
                attributes = parser.get_artwork_attributes()

                download_link = parser.get_download_link()
                if download_link and attributes['Category'] == 'Artwork (Digital)':
                    ID = self.get_artwork_id(url)
                    attributes['ID'] = int(ID)

                    filename = util.combine_filename(ID, parser.get_filename_extension(download_link))
                    if self.download_artwork(filename, download_link):
                        self.add_scrapied_url(origin_url)
                        return attributes
            else:
                self.add_scrapied_url(origin_url)

    def scrapy_expired_url(self, url):
        url = parse.ArtworkParser.view_to_full(url)
        html = self.open_url(url)
        if html:
            logger.info('scrapied expired url %s.' % url)
            parser = parse.ArtworkParser(html)

            attributes = parser.get_artwork_attributes()
            return attributes
        else:
            logger.info('failed to scrapy expired url %s.' % url)

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
                logger.info('image "%s" downloaded.' % filename)
                return True
        except EnvironmentError:
            logger.warning('failed to download image "%s"' % filename)
            return False
