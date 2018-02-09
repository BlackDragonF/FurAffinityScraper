import os

from dateutil.parser import parse

from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

def if_images_directory_exists():
    if os.path.exists('images'):
        if os.path.isdir('images'):
            logger.debug('images directory exists.')
            return True
    return False

def create_images_directory():
    if not if_images_directory_exists():
        if os.path.isfile('images'):
            logger.error('exists file named "images".')
            return False
        os.mkdir('images')
        logger.info('directory "images" created.')
        return True
    return True

def combine_filename(artwork_id, filename_extension):
    if filename_extension:
        return artwork_id + '.' + filename_extension
    else:
        return artwork_id

def parse_datetime(date):
    return parse(date)

def convert_boolean(boolean):
    return 1 if boolean else 0

def generate_url_from_id(artwork_id):
    return BASE_URL + '/view/' + str(artwork_id)
