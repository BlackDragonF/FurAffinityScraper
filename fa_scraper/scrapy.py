from urllib.parse import quote

import requests
import cfscrape

from fa_scraper import parse
from fa_scraper import util
from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

import collections

import time

class Scraper(object):
    SCRAPIED_BASE = False # lazy load technical, flag to indicate whether base url has been scrapied

    def open_url(self, url):
        """
        Open url and return response content.

        Args:
            self - instance of class Scraper
            url - url that to be opened

        Returns:
            content - the content of HTTP Response
        """

        # use quote to deal with arabic/... url, safe ':/' is needed
        url = quote(url, safe = ':/')

        try:
            # timeout is necessary here
            response = self.scraper.get(url, timeout = 30)
        except:
            # catch all Exceptions here
            logger.warning('error when sending request to "%s".' % url)
            return None

        # checks response's status code
        if response.status_code == 200:
            logger.debug('received response from "%s".' % url)
        else:
            logger.warning('request sent to "%s" returned error code: %u.' % (url, response.status_code))

        # add sleep here to avoid ddos to website
        time.sleep(self.scrapy_interval)

        return response.content

    def get_scrapying_url(self):
        # get next url to be scrapied from instance's scrapying queue
        try:
            return self.scrapying_queue.popleft()
        except IndexError:
            # if scrapying queue is empty, then program should exit directly
            logger.fatal('scrapying queue empty.')
            exit(-1)

    def add_unscrapied_urls(self, urls):
        # add urls to instance's scrapying queue
        url_count = 0
        for url in urls:
            # check if url has been scrapied here
            if not url in self.scrapied_set:
                self.scrapying_queue.append(url)
                url_count = url_count + 1
        logger.info('added %d urls to unscrapied queue.' % url_count)

    def add_scrapied_url(self, url):
        # wrapper that add url to instance's scrapied set
        self.scrapied_set.add(url)

    def __init__(self, scrapy_interval):
        # initialize scrapied set and scrapying queue
        self.scrapied_set = set()
        self.scrapying_queue = collections.deque()

        # set sleep interval between two requests
        self.scrapy_interval = scrapy_interval
        logger.info('set scrapy interval to %d' % scrapy_interval)

        # use cfscrape to avoid block from cloudflare
        self.scraper = cfscrape.create_scraper()

        logger.debug('scraper initialized.')

    def scrapy_pending_url(self):
        """
        Retrieve next scrapying url from queue and scrapy it.

        Args:
            self - instance of class Scraper

        Returns:
            attributes - attributes dictionary of current artwork, None if scrapied
        url isn't of type view or error occurs
        """
        # lazy load technical, scrapy base url if hasn't
        if not Scraper.SCRAPIED_BASE:
            main_html = self.open_url(BASE_URL)
            if main_html:
                parser = parse.Parser(main_html)
                sites = parser.get_all_urls()
                self.add_unscrapied_urls(sites)
                logger.debug('base url scrapied.')
                Scraper.SCRAPIED_BASE = True

        # get next srcapying url
        url = self.get_scrapying_url()
        if not url:
            logger.warning('failed to get url.')
            return None
        elif url in self.scrapied_set:
            logger.debug('url has been scrapied.')
            return None
        origin_url = url # backup origin url

        # get url type, skip this round if unknown
        url_type = parse.Parser.get_url_type(url)
        if url_type == 'unknown':
            logger.info('skipped unknown url "%s".' % url)
            return None

        # convert url if url type is view(for downloading image)
        if url_type == 'view':
            url = parse.ArtworkParser.view_to_full(url)

        html = self.open_url(BASE_URL + url)
        if html:
            logger.info('scrapied "%s" site with url %s.' % (url_type, url))

            # initalize parser according to url type
            parser = parse.ArtworkParser(html) if url_type == 'view' else parse.Parser(html)

            # retrieve urls and add them to instance's scrapying queue
            urls = parser.get_all_urls()
            self.add_unscrapied_urls(urls)

            if url_type == 'view':
                # for view, parse attributes and then try to download image
                attributes = parser.get_artwork_attributes()

                download_link = parser.get_download_link()
                # TODO: filter will be added here
                if download_link and attributes['Category'] in SCRAPIED_CATEGORIES:
                    # set ID
                    ID = self.get_artwork_id(url)
                    attributes['ID'] = int(ID)

                    filename = util.combine_filename(ID, parser.get_filename_extension(download_link))
                    if self.download_artwork(filename, download_link):
                        # download succeed
                        # add origin url to instance's scrapied set and returns attributes
                        self.add_scrapied_url(origin_url)
                        return attributes
            else:
                # add origin url to instance's scrapied set
                self.add_scrapied_url(origin_url)

    def scrapy_expired_url(self, url):
        """
        Scrapy expired artwork url.

        Args:
            self - instance of class Scraper
            url - expired url needs update

        Returns:
            attributes - updated attributes of given artwork url, None if error
        occurs
        """
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
        # get artwork id(string) from url
        return url.replace('/', '').replace('full', '')

    def download_artwork(self, filename, download_link):
        """
        Download artwork given download link and save it as filename

        Args:
            self - instance of class Scraper
            filename - filename of the artwork
            download_link - download link of the artwork

        Returns:
            True if download process succeeds
            False if download process fails
        """
        data = self.open_url(download_link)
        if not data:
            # response is empty
            logger.warning('failed to download image "%s".' % filename)
            return False
        try:
            # saves content to file
            with open('images/' + filename, 'wb') as image:
                image.write(data)
                logger.info('image "%s" downloaded.' % filename)
                return True
        except EnvironmentError:
            # occurs error when saving image
            logger.warning('error when saving image "%s".' % filename)
            return False
