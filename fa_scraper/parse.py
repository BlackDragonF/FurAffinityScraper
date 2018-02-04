from bs4 import BeautifulSoup

from http.client import HTTPResponse

import re

import logging
logger = logging.getLogger('default')

class Parser(object):

    URL_TYPES = ['view', 'gallery', 'favorites', 'user']

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

    @classmethod
    def generate_regex_table(cls):
        regex_table = {}

        for attribute in cls.ARTWORK_ATTRIBUTES:
            regex_table[attribute] = '<b>' + attribute + ':</b>\s*(.+?)<br/>'

        regex_table.update({'Keywords': '<a href=\'.*\'>(.+?)</a>',
                        'Author': '<b>(.+)</b>',
                        'Name': '<a href=\'.*\'>(.+)</a>'})

        logger.debug('artwork parser\'s regex table generated.')
        cls.REGEX_TABLE = regex_table

    @staticmethod
    def get_filename_extension(link):
        match = re.search(re.compile('.*\.(.+)'), link)
        if match:
            return match.group(1)

    @staticmethod
    def get_artwork_id(url):
        return url.replace('/', '').replace('full', '')



    def get_matched_string(tag, regex):
        match = re.search(re.compile(regex), str(tag))
        if match:
            return match.group(1)


    def __init__(self, html):
        if not ArtworkParser.REGEX_TABLE:
            ArtworkParser.generate_regex_table();

        super(ArtworkParser, self).__init__(html)
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


    def get_artwork_attributes(self):
        pass






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
