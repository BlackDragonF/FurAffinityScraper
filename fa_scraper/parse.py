from bs4 import BeautifulSoup

import re

from fa_scraper import util
from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

from functools import reduce

class Parser(object):
    """
    Parser class to initialize from a html and parse information from it

    Attributes:
        bs - BeautifulSoup object to parse tags/attributes easily from DOM tree
    """
    # compiled url regex table
    URL_REGEX_TABLE = {}

    @classmethod
    def generate_url_regex_table(cls):
        """
        Generate compiled regex table to match url quickly from given html.

        Args:
            cls - Parser class
        """
        url_regex_table = {}

        for url_type in URL_TYPES:
            url_regex_table[url_type] = re.compile('^(/' + url_type + '/)')

        # user's regex is not exactly same with others
        # /user/history is banned from robots.txt, so to be excluded
        url_regex_table['user'] = re.compile('^(/user/)(?!history/)')

        logger.debug('url regex table(stores compiled regexes for url '
                     'match) generated.')
        cls.URL_REGEX_TABLE = url_regex_table

    @staticmethod
    def get_url_type(url):
        # get url type of given url, simply implements with find
        for url_type in URL_TYPES:
            sub_url = '/' + url_type + '/'
            if url.find(sub_url) != -1:
                return url_type

        logger.warning('unknown url type from url: %s.' % url)
        return 'unknown'

    def __init__(self, html):
        # lazy load, trying to generate compiled regex table when the first
        # instance initialized.
        if not Parser.URL_REGEX_TABLE:
            Parser.generate_url_regex_table()

        # initialize bs object for parsing
        self.bs = BeautifulSoup(html, "html.parser")

        logger.debug('parser initialized.')

    def get_all_urls(self):
        """
        Get all matched urls from html.

        Args:
            self - instance of class Parser

        Returns:
            urls - a list of all matched urls
        """
        urls = []
        url_count = 0

        for url_type in URL_TYPES:
            # look up directly from regex table
            temp_urls = self.bs.findAll('a', href = Parser.URL_REGEX_TABLE[url_type])
            if temp_urls:
                # use map to get href attribute(url) from matched tag
                temp_urls = list(map(lambda tag: tag.get('href'), temp_urls))
                url_count = url_count + len(temp_urls)
                urls = urls + temp_urls

        logger.info("retrieved %u available urls." % url_count)

        return urls


class ArtworkParser(Parser):
    """
    ArtworkParser class inherit from Parser and parse information from a artwork
website.

    Attributes:
        bs - inherit from super class Parser
        stats_tag - status tag where most attributes are included
        cat_tag - cat tag where name and author attributes are included
        keywords_tag - keywords tag in status tag
        posted_tag - posted tag in status tag
    """
    ARTWORK_ATTRIBUTES = ['Category', 'Theme', 'Species', 'Gender', 'Favorites',
                          'Comments', 'Views', 'Resolution', 'Keywords', 'Author',
                          'Name'] # attributes used by regex table and tag table
    INT_ATTRIBUTES = set(['Views', 'Comments', 'Favorites'])
    # attributes needs to be convert to int

    REGEX_TABLE = {} # compiled regex table
    TAG_TABLE = {} # tag table

    FILENAME_EXTENSION_REGEX = re.compile('.*\.(.+)') # compiled regex to get file extension from download url

    @classmethod
    def generate_regex_table(cls):
        """
        Generate compiled regex table to extract attribute quickly from certain
        tag.

        Args:
            cls - ArtworkParser class
        """
        regex_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            regex_table[attribute] = re.compile('<b>' + attribute + ':</b>\s*(.+?)\s*<br/>')

        # keywords author name uses different regexes
        regex_table.update({'Keywords'  : re.compile('<a href=".*">(.+?)</a>'),
                            'Author'    : re.compile('<a href=".*">(.+)</a>'),
                            'Name'      : re.compile('<b>(.+)</b>')})

        logger.debug('artwork parser\'s regex table(stores compiled regexes for '
                     'extract artwork attribute) generated.')
        cls.REGEX_TABLE = regex_table

    @classmethod
    def generate_tag_table(cls):
        """
        Generate tag table to map attribute to tag(property of ArtworkParser).

        Args:
            cls -ArtworkParser class
        """
        tag_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            tag_table[attribute] = 'stats_tag'

        # keywords author name uses different tags
        tag_table.update({'Name'        : 'cat_tag',
                          'Author'      : 'cat_tag',
                          'Keywords'    : 'keywords_tag'})

        logger.debug('artwork parser\'s tag table(stores tag name each attribute '
                     'uses) generated.')
        cls.TAG_TABLE = tag_table

    def parse_tags(self):
        """
        Parse tags that used to extract attributes from html, tags to be parsed
        are stas_tag, cat_tag, keywords_tag and posted_tag.

        Args:
            self - instance of class ArtworkParser
        """
        self.stats_tag = self.bs.find('td', {'class': 'alt1 stats-container'})
        self.cat_tag = self.bs.find('td', {'class': 'cat'})
        if self.stats_tag:
            self.keywords_tag = self.stats_tag.find('div', {'id': 'keywords'})
            self.posted_tag = self.stats_tag.find('span', {'class': 'popup_date'})
        else:
            # even cannot get stats_tag, still set tag to None to make sure other
            # method can access property accordingly
            self.keywords_tag = None
            self.posted_tag = None
            logger.debug('cannot parse stats_tag, set keywords_tag and posted_'
                         'tag to None.')
        logger.debug('parsed tags used to retrieve artwork attribute.')

    def __init__(self, html):
        # lazy load similar to Parser, will compile regex for only once
        if not ArtworkParser.REGEX_TABLE:
            ArtworkParser.generate_regex_table()
        if not ArtworkParser.TAG_TABLE:
            ArtworkParser.generate_tag_table()

        # call super class's init method
        super(ArtworkParser, self).__init__(html)
        # parse tags
        self.parse_tags()

        logger.debug('artwork parser initialized.')

    def get_download_link(self):
        """
        Get download link from html.

        Args:
            self - instance of class ArtworkParser

        Returns:
            download_link - the download link of artwork, '' if cannot get
        """
        download_link = ''

        image_tag = self.bs.find('img', {'id': 'submissionImg'})
        if image_tag and image_tag.has_attr('src'):
            download_link = 'https:' + image_tag['src']
            logger.info('retrieved download link - "%s".' % download_link)
        else:
            logger.info('unable to retrieve download link.')

        return download_link

    @staticmethod
    def get_matched_string(tag, regex):
        # use findall to get all matched string from tag and regex
        match = re.findall(regex, str(tag))
        if match:
            return match

    @staticmethod
    def format_resolution(resolution):
        # convert from resolution like "1920x1080" to a attribute dictionary
        resolution = resolution.split('x')
        if (len(resolution) >= 2):
            # convert string to int here
            formatted_resolution = {'Width'     : int(resolution[0]),
                                    'Height'    : int(resolution[1])}
            return formatted_resolution

    @staticmethod
    def get_posted_time(posted_time):
        # get posted time from posted_tag
        if posted_time.has_attr('title'):
            return posted_time['title']

    @staticmethod
    def combine_keywords(keywords):
        # use reduce to combine all keywords to a string seperate by space
        return reduce(lambda x, y : x + ' ' + y, keywords)

    @staticmethod
    def generate_unparsed_attributes_log(unparsed_attributes):
        # use unparsed_attributes set to generate log message
        # convert set to list
        unparsed_attributes = list(unparsed_attributes)
        if unparsed_attributes:
            # use reduce to combine all attributes together seperate by space
            return 'unparsed attributes: ' + reduce(lambda x, y : x + ' ' + y, unparsed_attributes) + '.'
        else:
            return 'all attributes parsed.'

    def get_artwork_attributes(self):
        """
        Get artwork's attributes from html.

        Args:
            self - instance of class ArtworkParser

        Returns:
            attributes - attribute dictionary
        """
        # generate unparsed attributes set
        unparsed_set = set(ArtworkParser.ARTWORK_ATTRIBUTES)
        # initalize attributes
        attributes = {}

        # get posted time
        if self.posted_tag:
            posted_time = self.get_posted_time(self.posted_tag)
            if posted_time:
                # parse posted time and format it to string that will
                # recognized by sqlite
                posted_time = util.parse_datetime(posted_time)
                attributes['Posted'] = posted_time.strftime("%Y-%m-%d %H:%M")
            else:
                unparsed_set.add('Posted')

        # get other attributes
        for attribute in ArtworkParser.ARTWORK_ATTRIBUTES:
            # regular form - get tag and regex, and use regex to match from tag
            tag_name = ArtworkParser.TAG_TABLE[attribute]
            try:
                tag = getattr(self, tag_name)
            except AttributeError as error:
                # failed to get tag, skip
                continue
            regex = ArtworkParser.REGEX_TABLE[attribute]
            content = self.get_matched_string(tag, regex)

            if not content:
                # cannot extract attribute from tag, skip
                continue
            else:
                if attribute == 'Keywords':
                    # combine keywords
                    content = self.combine_keywords(content)
                else:
                    # other attributes
                    content = content[0]
                    if attribute in ArtworkParser.INT_ATTRIBUTES:
                        # convert string to int if necessary
                        content = int(content)

            if attribute == 'Resolution':
                # format resolution here
                resolution = self.format_resolution(content)
                if resolution:
                    attributes.update(resolution)
                    unparsed_set.remove('Resolution')
            else:
                # other attribute
                attributes[attribute] = content
                unparsed_set.remove(attribute)

        # current scraper cannot login, so there is no NSFW content
        # set 'Adult' directly to False
        attributes['Adult'] = False

        logger.info(self.generate_unparsed_attributes_log(unparsed_set))

        return attributes

    @staticmethod
    def get_filename_extension(link):
        # get filename extension from given download link
        match = re.search(ArtworkParser.FILENAME_EXTENSION_REGEX, link)
        if match:
            return match.group(1)

    @staticmethod
    def view_to_full(url):
        # convert url like /view/ to /full/
        return url.replace('view', 'full')
