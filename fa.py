from fa_scraper import *

import argparse
import sys
import os

import json

import logging
import logging.config

def parse_arguments():
    """
    Parse arguments from commandline.

    Args:
        None

    Returns:
        arguments - arguments parsed from command line
    """
    argparser = argparse.ArgumentParser(
        usage = '%s [OPTION]' % sys.argv[0],
        description = 'A scraper of furaffinity.net written with python.'
    )

    # log-level - cen be choosen from 'debug', 'info', 'warning', 'error', 'fatal'
    # default is info, set the console log level
    argparser.add_argument(
        '--log-level',
        nargs = 1,
        default = ['info'],
        choices = ['debug', 'info', 'warning', 'error', 'fatal'],
        help = 'sets verbosity level for console log messages, default: info'
    )

    # scrapy-mode - can be choosen from 'default', 'update'
    # default is 'default', set scrapy mode
    argparser.add_argument(
        '--scrapy-mode',
        nargs = 1,
        default = ['default'],
        choices = ['default', 'update'],
        help = 'sets scrapying mode, default: default'
    )

    # expire-time - int, set expire time
    # only works when scrapy-mode is 'update'
    argparser.add_argument(
        '--expire-time',
        nargs = 1,
        type = int,
        default = 15,
        help = 'sets expire time(days) for scrapied images, default: 15'
    )

    # skip-check - when specified, skip integrity check step
    argparser.add_argument(
        '--skip-check',
        action='store_true',
        help = 'skip integrity check(ONLY works in default mode) between database and images'
    )

    arguments = argparser.parse_args()
    return arguments

def config_logger(console_log_level):
    """
    Configure logger, should be called at the very first of program.

    Args:
        console_log_level - console log level, while log file level is fixed to debug
    """
    config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - [%(levelname)s] %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'standard'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'fa_scraper.log',
                'level': 'DEBUG',
                'formatter': 'standard'
            }
        },
        'loggers': {
            'default': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }
    config['handlers']['console']['level'] = console_log_level
    logging.config.dictConfig(config)

    logger = logging.getLogger('default')
    logger.info('set console log level to %s' % console_log_level)

    logger.debug('logger configured.')
    return logger

def check_and_fix_artworks(db, scraper):
    """
    Integrity check step.
    Traverse through database and see if for each artwork,
    there exists a corresponding image in images sub-directory.
    If there are artworks missing, remove them from database, and add there urls
    to scraper's scrapying queue.
    ONLY works in default mode.

    Args:
        db - database instance
        scraper - scraper instance
    """
    # get all artwork IDs from artwork, and initialize a set
    artwork_ids = set(db.get_artwork_ids())
    # traverse through 'images' sub-directory
    os.chdir('images')
    logger.debug('changed working directory to images.')

    artworks = os.listdir('.')
    for artwork in artworks:
        if os.path.isfile(artwork):
            artwork_id = int(os.path.splitext(os.path.basename(artwork))[0])
            # if exists image named 'artwork ID', remove it from set
            if artwork_id in artwork_ids:
                artwork_ids.remove(artwork_id)

    # remove remaining artwork records from database
    db.delete_artworks(artwork_ids)

    # convert artwork IDs to urls and add to scrapying queue
    unscrapied_urls = list(map(util.generate_url_from_id, list(artwork_ids)))
    scraper.add_unscrapied_urls(unscrapied_urls)

    os.chdir('..')
    logger.debug('changed working directory to origin.')
    logger.info('%u wrong records removed from database.' % len(artwork_ids))


if __name__ == '__main__':
    # parse arguments from command line
    arguments = parse_arguments()

    # configure logger
    log_level = arguments.log_level[0].upper()
    logger = config_logger(log_level)

    # create images sub-directory if not exists
    if not util.create_images_directory():
        exit(-1)

    # initialize database and scraper
    db = database.Database('fa_scraper.db')
    scraper = scrapy.Scraper()
    logger.info('initialization completed.')

    scrapy_mode = arguments.scrapy_mode[0]
    logger.info('scrapy mode set to %s' % scrapy_mode)

    # try to perform integrity check
    if not arguments.skip_check:
        if scrapy_mode == 'default':
            check_and_fix_artworks(db, scraper)
            logger.info('integrity check completed.')
        else:
            logger.info('will not perform integrity check in update mode.')
    else:
        logger.info('skipped integrity check.')

    # main body
    if scrapy_mode == 'default':
        while True:
            # scrapy loop
            # try to get artwork from scraper
            artwork = scraper.scrapy_pending_url()
            if artwork:
                # extend added time
                artwork['Added'] = util.get_current_time()

                information = json.dumps(artwork)
                logger.info('scrapied artwork information: %s' % information)

                # insert into database
                db.insert_or_replace_artwork(artwork)
                logger.info('completed to scrapy artwork with ID: %u.' % artwork.get('ID'))
            else:
                logger.info('didn\'t scrapy artwork in current round.')
    elif scrapy_mode == 'update':
        # get expired artwork IDs from database
        expired_artwork_ids = db.get_expired_artwork_ids(arguments.expire_time)
        logger.info('retrieved all expired artwork IDs.')

        for artwork_id in expired_artwork_ids:
            # try to artwork attributes
            artwork = scraper.scrapy_expired_url(util.generate_url_from_id(artwork_id))
            if artwork:
                # update added time and set ID
                artwork['ID'] = artwork_id
                artwork['Added'] = util.get_current_time()

                information = json.dumps(artwork)
                logger.info('updated artwork information: %s' % information)

                # replace record in database
                db.insert_or_replace_artwork(artwork)
                logger.info('completed to re-scrapy expired artwork(with ID: %u)\'s info .' % artwork.get('ID'))

    db.close_db(conn)

    logger.info('exiting scraper...')
    exit(0)
