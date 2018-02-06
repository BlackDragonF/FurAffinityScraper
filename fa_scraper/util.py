import os

from dateutil.parser import parse

import logging
logger = logging.getLogger('default')

def create_images_directory():
    if not os.path.exists('images'):
        os.mkdir('images')
        logger.info('directory "images" created.')

def combine_filename(artwork_id, filename_extension):
    return artwork_id + '.' + filename_extension

def parse_datetime(date):
    return parse(date)

def convert_boolean(boolean):
    if boolean:
        return 1
    else:
        return 0
