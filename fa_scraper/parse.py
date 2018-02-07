from bs4 import BeautifulSoup

import re

from fa_scraper import util
from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

from functools import reduce

class Parser(object):
    URL_REGEX_TABLE = {}

    @classmethod
    def generate_url_regex_table(cls):
        url_regex_table = {}

        for url_type in URL_TYPES:
            url_regex_table[url_type] = re.compile('^(/' + url_type + '/)')

        url_regex_table['user'] = re.compile('^(/user/)(?!history/)')

        logger.debug('url regex table(stores compiled regexes for url '
                     'match) generated.')
        cls.URL_REGEX_TABLE = url_regex_table

    @staticmethod
    def get_url_type(url):
        for url_type in URL_TYPES:
            sub_url = '/' + url_type + '/'
            if url.find(sub_url) != -1:
                return url_type

        logger.warning('unknown url type from url: %s.' % url)
        return 'unknown'

    def __init__(self, html):
        if not Parser.URL_REGEX_TABLE:
            Parser.generate_url_regexes()

        self.bs = BeautifulSoup(html, "html.parser")
        logger.debug('parser initialized.')

    def get_all_urls(self):
        urls = []
        url_count = 0

        for url_type in URL_TYPES:
            temp_urls = self.bs.findAll('a', href = Parser.URL_REGEX_TABLE[url_type])
            if temp_urls:
                temp_urls = list(map(lambda tag: tag.get('href'), temp_urls))
                url_count = url_count + len(temp_urls)
                urls = urls + temp_urls

        logger.info("retrieved %u urls." % url_count)

        return urls


class ArtworkParser(Parser):
    ARTWORK_ATTRIBUTES = ['Category', 'Theme', 'Species', 'Gender', 'Favorites',
                          'Comments', 'Views', 'Resolution', 'Keywords', 'Author',
                          'Name']
    INT_ATTRIBUTES = set(['Views', 'Comments', 'Favorites'])

    REGEX_TABLE = {}
    TAG_TABLE = {}

    FILENAME_EXTENSION_REGEX = re.compile('.*\.(.+)')

    @classmethod
    def generate_regex_table(cls):
        regex_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            regex_table[attribute] = re.compile('<b>' + attribute + ':</b>\s*(.+?)\s*<br/>')

        regex_table.update({'Keywords'  : re.compile('<a href=".*">(.+?)</a>'),
                            'Author'    : re.compile('<a href=".*">(.+)</a>'),
                            'Name'      : re.compile('<b>(.+)</b>')})

        logger.debug('artwork parser\'s regex table(stores compiled regexes for '
                     'extract artwork attribute) generated.')
        cls.REGEX_TABLE = regex_table

    @classmethod
    def generage_tag_table(cls):
        tag_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            tag_table[attribute] = 'stats_tag'

        tag_table.update({'Name'        : 'cat_tag',
                          'Author'      : 'cat_tag',
                          'Keywords'    : 'keywords_tag'})

        logger.debug('artwork parser\'s tag table(stores tag name each attibute '
                     'uses) generated.')
        cls.TAG_TABLE = tag_table

    def parse_tags(self):
        self.stats_tag = self.bs.find('td', {'class': 'alt1 stats-container'})
        self.cat_tag = self.bs.find('td', {'class': 'cat'})
        if self.stats_tag:
            self.keywords_tag = self.stats_tag.find('div', {'id': 'keywords'})
            self.posted_tag = self.stats_tag.find('span', {'class': 'popup_date'})
        else:
            self.keywords_tag = None
            self.posted_tag = None
            logger.debug('cannot parse stats_tag, set keywords_tag and posted_'
                         'tag to None.')
        logger.debug('parsed tags used to retrieve artwork attribute.')

    def __init__(self, html):
        if not ArtworkParser.REGEX_TABLE:
            ArtworkParser.generate_regex_table()
        if not ArtworkParser.TAG_TABLE:
            ArtworkParser.generage_tag_table()

        super(ArtworkParser, self).__init__(html)
        self.parse_tags()

        logger.debug('artwork parser initialized.')

    def get_download_link(self):
        download_link = ''

        image_tag = self.bs.find('img', {'id': 'submissionImg'})
        if image_tag and image_tag.has_attr('src'):
            download_link = 'https:' + image_tag['src']
            logger.debug('retrieved download link - "%s".' % download_link)
        else:
            logger.debug('unable to retrieve download link.')

        return download_link

    @staticmethod
    def get_matched_string(tag, regex):
        match = re.findall(regex, str(tag))
        if match:
            return match

    @staticmethod
    def format_resolution(resolution):
        resolution = resolution.split('x')
        if (len(resolution) >= 2):
            formatted_resolution = {'Width'     : resolution[0],
                                    'Height'    : resolution[1]}
            return formatted_resolution

    @staticmethod
    def get_posted_time(posted_time):
        if posted_time.has_attr('title'):
            return posted_time['title']

    @staticmethod
    def combine_keywords(keywords):
        return reduce(lambda x, y : x + ' ' + y, keywords)

    @staticmethod
    def generate_unparsed_attributes_log(unparsed_attributes):
        unparsed_attributes = list(unparsed_attributes)
        return 'unparsed attribute: ' + reduce(lambda x, y : x + ' ' + y, unparsed_attributes) + '.'

    def get_artwork_attributes(self):
        unparsed_set = set(ArtworkParser.ARTWORK_ATTRIBUTES)
        attributes = {}

        if self.posted_tag:
            posted_time = self.get_posted_time(self.posted_tag)
            if posted_time:
                posted_time = util.parse_datetime(posted_time)
                attributes['Posted'] = posted_time.strftime("%Y-%m-%d %H:%M")
            else:
                unparsed_set.add('Posted')

        for attribute in ArtworkParser.ARTWORK_ATTRIBUTES:
            tag_name = ArtworkParser.TAG_TABLE[attribute]
            try:
                tag = getattr(self, tag_name)
            except AttributeError as error:
                logger.debug('failed to get tag: %s.' % tag_name)
                continue
            regex = ArtworkParser.REGEX_TABLE[attribute]
            content = self.get_matched_string(tag, regex)

            if not content:
                logger.debug('failed to extract attribute: %s.' % attibute)
                continue
            else:
                if attibute == 'Keywords':
                    content = self.combine_keywords(content)
                else:
                    content = content[0]
                    if attibute in ArtworkParser.INT_ATTRIBUTES:
                        content = int(content)

            if attribute == 'Resolution':
                resolution = self.format_resolution(content)
                if resolution:
                    attributes.update(resolution)
                    unparsed_set.remove('Resolution')
            else:
                attributes[attribute] = content
                unparsed_set.remove(attribute)

        attributes['Adult'] = False

        logger.debug(self.generate_unparsed_attributes_log(unparsed_set))
        return attributes

    @staticmethod
    def get_filename_extension(link):
        match = re.search(ArtworkParser.FILENAME_EXTENSION_REGEX, link)
        if match:
            return match.group(1)

    @staticmethod
    def view_to_full(url):
        return url.replace('view', 'full')
