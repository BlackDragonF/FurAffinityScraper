import os

import logging
logger = logging.getLogger('default')

def create_images_directory():
    if not os.path.exists('images'):
        os.mkdir('images')
        logger.info('directory "images" created.')

def get_url_type(url, url_types):
    for url_type in url_types:
        sub_url = '/' + url_type + '/'
        if url.find(sub_url) != -1:
            return url_type

    logger.warning('unknown url type from url: %s' % url)
    return 'unknown'

def combine_filename(artwork_id, filename_extension):
    return artwork_id + '.' + filename_extension

def get_fullview_url(url):
    return url.replace('view', 'full')
