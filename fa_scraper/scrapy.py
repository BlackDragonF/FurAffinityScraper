from urllib import request
from urllib import error
from urllib.parse import quote

from fa_scraper import parse
from fa_scraper import util
from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

import queue

import time

import random

import json

class Scraper(object):
    @staticmethod
    def generate_user_agent():
        return random.choice(USER_AGENTS)

    @staticmethod
    def open_url(url):
        url = quote(url, safe=':/')
        try:
            r = request.Request(url)
            r.add_header('User-Agent', Scraper.generate_user_agent())
            response = request.urlopen(r, timeout = 10)
            logger.debug('received response from "%s"' % url)
            return response
        except error.HTTPError as e:
            logger.warning('request sent to %s returned %u.' % (url, e.code))
        except error.URLError as e:
            logger.warning('request sent to %s failed: %s.' % (url, e.reason))
        finally:
            time.sleep(10)

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

        main_html = Scraper.open_url(BASE_URL)
        if main_html:
            parser = parse.Parser(main_html)
            sites = parser.get_page_links()
            self.add_unscrapied_urls(sites)

        logger.debug('scraper initialized.')

    def scrapy_pending_url(self):
        url = self.get_scrapying_url()
        if not url or url in self.scrapied_set:
            return
        origin_url = url

        url_type = parse.Parser.get_url_type(url, URL_TYPES)
        if url_type == 'view':
            url = parse.ArtworkParser.get_fullview_url(url)
        elif url_type == 'unknown':
            logger.info('skipped unknown url %s' % url)
            return

        html = Scraper.open_url(BASE_URL + url)
        if html:
            logger.debug('scrapied site with url type: %s' % url_type)
            if url_type == 'view':
                parser = parse.ArtworkParser(html)
                attributes = parser.get_artwork_attributes()
                download_link = parser.get_download_link()
                print(json.dumps(attributes, indent = 1))
                # if download_link:
                #     filename = util.combine_filename(parser.get_artwork_id(url), parser.get_filename_extension(download_link))
                #     Scraper.download_artwork(filename, download_link)
            else:
                parser = parse.Parser(html)

            sites = parser.get_page_links()
            self.add_unscrapied_urls(sites)
            self.add_scrapied_url(origin_url)

    @staticmethod
    def get_artwork_id(url):
        return url.replace('/', '').replace('full', '')

    @staticmethod
    def download_artwork(filename, download_link):
        response = Scraper.open_url(download_link)
        data = response.read()
        with open('images/' + filename, 'wb') as image:
            image.write(data)
            logger.debug('image %s downloaded.' % filename)
