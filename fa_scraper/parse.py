from bs4 import BeautifulSoup

from http.client import HTTPResponse

import re

import logging
logger = logging.getLogger('default')

class Parser(object):

    URL_TYPES = ['view', 'gallery', 'favorites', 'user']

    @staticmethod
    def get_url_type(url, url_types):
        for url_type in url_types:
            sub_url = '/' + url_type + '/'
            if url.find(sub_url) != -1:
                return url_type

        logger.warning('unknown url type from url: %s' % url)
        return 'unknown'

    def __init__(self, html):
        self.bs = BeautifulSoup(html, "html.parser")
        logger.info('parser initialized.')

    def get_page_links(self):
        sites = []
        site_count = 0

        for url_type in Parser.URL_TYPES:
            regex = '^(/' + url_type + '/)'
            temp_sites = self.bs.findAll('a', href = re.compile(regex))
            if temp_sites:
                temp_sites = list(map(lambda tag: tag.get('href'), temp_sites))
                site_count = site_count + len(temp_sites)
                sites = sites + temp_sites

        logger.info("retrieved %d sites." % site_count)

        return sites




class ArtworkParser(Parser):

    ARTWORK_ATTRIBUTES = ['Category', 'Theme', 'Species', 'Gender', 'Favorites', 'Comments', 'Views', 'Resolution', 'Keywords', 'Author', 'Name']
    REGEX_TABLE = {}
    TAG_TABLE = {}

    @classmethod
    def generate_regex_table(cls):
        regex_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            regex_table[attribute] = '<b>' + attribute + ':</b>\s*(.+?)\s*<br/>'

        regex_table.update({'Keywords': '<a href=".*">(.+)</a>',
                        'Author': '<a href=".*">(.+)</a>',
                        'Name': '<b>(.+)</b>'})

        logger.debug('artwork parser\'s regex table generated.')
        cls.REGEX_TABLE = regex_table

    @classmethod
    def generage_tag_table(cls):
        tag_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            tag_table[attribute] = 'stats_tag'

        tag_table.update({'Name': 'cat_tag',
                          'Author': 'cat_tag',
                          'Keywords': 'keywords_tag'})

        logger.debug('artwork parser\'s tag table generated.')
        cls.TAG_TABLE = tag_table


    @staticmethod
    def get_filename_extension(link):
        match = re.search(re.compile('.*\.(.+)'), link)
        if match:
            return match.group(1)

    @staticmethod
    def get_artwork_id(url):
        return url.replace('/', '').replace('full', '')

    @staticmethod
    def get_fullview_url(url):
        return url.replace('view', 'full')

    def parse_tags(self):
        self.stats_tag = self.bs.find('td', {'class': 'alt1 stats-container'})
        self.cat_tag = self.bs.find('td', {'class': 'cat'})
        if (self.stats_tag):
            self.keywords_tag = self.stats_tag.find('div', {'id': 'keywords'})
            self.posted_tag = self.stats_tag.find('span', {'class': 'popup_date'})

    def __init__(self, html):
        if not ArtworkParser.REGEX_TABLE:
            ArtworkParser.generate_regex_table()
        if not ArtworkParser.TAG_TABLE:
            ArtworkParser.generage_tag_table()

        super(ArtworkParser, self).__init__(html)
        self.parse_tags()

        logger.info('artwork parser initialized.')

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
        match = re.search(re.compile(regex), str(tag))
        if match:
            return match.group(1)

    @staticmethod
    def format_resolution(resolution):
        temp = resolution.split('x')
        if (len(temp) >= 2):
            return (int(temp[0]), int(temp[1]))

    @staticmethod
    def extract_posted_time(posted_time):
        if posted_time.has_attr('title'):
            return posted_time['title']


    def get_artwork_attributes(self):
        unparsed_set = set(ArtworkParser.ARTWORK_ATTRIBUTES)
        attributes = {}

        for attribute in ArtworkParser.ARTWORK_ATTRIBUTES:
            try:
                tag = getattr(self, ArtworkParser.TAG_TABLE[attribute])
            except AttributeError as error:
                continue
            regex = ArtworkParser.REGEX_TABLE[attribute]
            content = self.get_matched_string(tag, regex)

            if not content:
                continue

            if attribute == 'Resolution':
                resolution = self.format_resolution(content)
                if resolution:
                    attributes['Width'] = resolution[0]
                    attributes['Height'] = resolution[1]
                    unparsed_set.remove('Resolution')
            else:
                attributes[attribute] = content
                unparsed_set.remove(attribute)

        if self.posted_tag:
            posted_time = self.extract_posted_time(self.posted_tag)
            if posted_time:
                attributes['Posted'] = posted_time
        else:
            unparsed_set.add('Posted')

        return attributes















# def get_keywords(tag):
#     keywords = re.findall(re.compile('<a href=\'.*\'>(.+?)</a>'), str(tag))
#     if keywords:
#         return keywords

# def get_author(cat_tag):
#     match = re.search(re.compile('<b>(.+)</b>'), str(cat_tag))
#     if match:
#         return match.group(1)
#
# def get_name(cat_tag):
#     match = re.search(re.compile('<a href=\'.*\'>(.+)</a>'), str(cat_tag))
#     if match:
#         return match.group(1)
#
# def get_artwork_attributes(tag, attr):
#     empty_attributes = set()
#
#     for attribute in attributes:
#         regex = generate_regex(attribute)
#         content = get_matched_string(tag, regex)
#         if content:
#             attr[attribute] = content
#         else:
#             empty_attributes.add(attribute)
#
#     resolution = get_state(tag, 'Resolution')
#     if resolution:
#         resolution = resolution.split('x')
#         if (len(resolution) >= 2):
#             attr['width'] = int(resolution[0])
#             attr['height'] = int(resolution[1])
#     else:
#         empty_attributes.add('Resolution')
#
#     keywords = tag.find('div', {'id': 'keywords'})
#     keywords = get_keywords(keywords_tag)
#     if keywords:
#         attr['keywords'] = keywords
#     else:
#         logger.debug('unable to get keywords.')
#
#     attr['adult'] = False
#
# def get_artwork_info(html, url_types):
#     bs = BeautifulSoup(html, 'html.parser')
#     info = {}
#     attr = {}
#
#     image_tag = bs.find('img', {'id': 'submissionImg'})
#     if image_tag and image_tag.has_attr('src'):
#         download = 'https:' + image_tag['src']
#         logger.debug('retrieved download link - "%s".' % download_link)
#         info['download'] = download
#     else:
#         logger.debug('unable to retrieve download link.')

    # artwork_cat = bs.find('td', {'class': 'cat'})
    # artwork_stats = bs.find('td', {'class': 'alt1 stats-container'})
    # if artwork_cat:
    #     author = get_author(artwork_cat)
    #     name = get_name(artwork_cat)
    #     if author:
    #         attr['author'] = author
    #     else:
    #         logger.debug('unable to get author.')
    #     if name:
    #         attr['name'] = name
    #     else:
    #         logger.debug('unable to get name.')
    # if artwork_stats:
    #     posted = artwork_stats.find('span', {'class': 'popup_date'})
    #     if posted and posted.has_attr('title'):
    #         attr['posted'] = posted['title']
    #         get_artwork_attr(artwork_stats, attr)
    #     else:
    #         logger.debug('unable to get posted time.')
    # logger.debug('artwork attributes collected.')
    # info['attributes'] = attr
    #
    # sites = get_page_links(bs, url_types)
    # info['sites'] = sites
    #
    # return info
