import os

import time

import pickle

from dateutil.parser import parse

from fa_scraper.constant import *

import logging
logger = logging.getLogger('default')

def if_images_directory_exists():
    """
    Checks if ./images/ exists.

    Args:
        None

    Returns:
        A boolean indicates whether exists directory 'images' in current working
    directory.
    """
    if os.path.exists('images'):
        if os.path.isdir('images'):
            logger.debug('images directory exists.')
            return True
    return False

def create_images_directory():
    """
    Create ./images/ if not exists.

    Args:
        None

    Returns:
        False if there exists a FILE named 'images', which means cannot create a
    directory named 'images'.
        True if successfully create 'images' directory or there exists a directory
    named 'images'.
    """
    if not if_images_directory_exists():
        if os.path.isfile('images'):
            logger.fatal('exists file named "images".')
            return False
        os.mkdir('images')
        logger.info('directory "images" created.')
        return True
    return True

def combine_filename(artwork_id, filename_extension):
    # artwork_id here is a str
    if filename_extension:
        return artwork_id + '.' + filename_extension
    else:
        return artwork_id

def parse_datetime(date):
    return parse(date)

def get_current_time():
    # the format string can be recognized by sqlite
    return time.strftime("%Y-%m-%d %H:%M", time.localtime())

def convert_boolean(boolean):
    # convert boolean to int, used by sqlite
    return 1 if boolean else 0

def generate_url_from_id(artwork_id):
    # artwork_id here is an int
    return BASE_URL + '/view/' + str(artwork_id)
