from urllib import request
from urllib import error

from bs4 import BeautifulSoup

import re

import logging

class Scraper(object):
    __BASE_URL = "https://www.furaffinity.net"
    
    def __open_url(self, url):
        try:
            response = request.urlopen(url)
        except HTTPError as error:
            self.__logger.warn("request sent to %s returned %u " % (url, error.code))
        except URLError as error:
            self.__logger.warn("request sent to %s failed: %s" % (url, error.reason))

        return response

    def __init__(self):
        self.__logger = logging.getLogger("default")
        self.__bs = BeautifulSoup(self.__open_url(Scraper.__BASE_URL), "html.parser")
        self.__artworks_iter = iter(self.__bs.findAll("a", href=re.compile("^(/view/)")))

    def next_arkwork(self):
        try:
            artwork_url = next(self.__artworks_iter)["href"]
        except StopIteration:
            pass
        print(artwork_url)
        artwork_url.replace('view', 'full')
        bs = BeautifulSoup(self.__open_url(Scraper.__BASE_URL + artwork_url), "html.parser")
        image = bs.find("img", {"id": "submissionImg"})
        print(image["src"])
