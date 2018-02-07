import os

from dateutil.parser import parse

import logging
logger = logging.getLogger('default')

def create_images_directory():
    if not os.path.exists('images'):
        os.mkdir('images')
        logger.info('directory "images" created.')

def combine_filename(artwork_id, filename_extension):
    if filename_extension:
        return artwork_id + '.' + filename_extension
    else:
        return artwork_id

def parse_datetime(date):
    return parse(date)

def convert_boolean(boolean):
    return 1 if boolean else 0
