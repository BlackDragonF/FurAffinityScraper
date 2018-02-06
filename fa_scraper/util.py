import os

import logging
logger = logging.getLogger('default')

def create_images_directory():
    if not os.path.exists('images'):
        os.mkdir('images')
        logger.info('directory "images" created.')

def combine_filename(artwork_id, filename_extension):
    return artwork_id + '.' + filename_extension
