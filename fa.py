from fa_scraper import *

import argparse
import sys
import os
import signal
import pickle

import json

import logging
import logging.config

def signal_handler(signum, frame):
    # exit signal received, use pickle to dump scraper
    logger.info('exit signal received, saving scrapying progress...')
    logger.info('current scraper with %u urls scrapied, and %u scrapying urls.' % (len(scraper.scrapied_set), len(scraper.scrapying_queue)))
    with open('scraper.cache', 'wb') as temp:
        pickle.dump(scraper, temp)
        logger.info('successfully saved scrapying progress to scraper.cache.')

    exit(0)

def parse_arguments():
    """
    Parse arguments from commandline.

    Args:
        None

    Returns:
        arguments - arguments parsed from command line
    """
    argparser = argparse.ArgumentParser(
        usage = '%s [OPTIONS]' % sys.argv[0],
        description = 'A scraper of furaffinity.net written with python.'
    )

    # scrapy-mode - can be choosen from 'default', 'update'
    # default is 'default', set scrapy mode
    argparser.add_argument(
        '-m', '--scrapy-mode',
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
        default = [15],
        help = 'sets expire time(days) for scrapied images, default: 15'
    )

    # scrapy-interval - int ,set scraper's sleep interval between two requests
    argparser.add_argument(
        '-i', '--scrapy-interval',
        nargs = 1,
        type = int,
        default = [60],
        help = 'sets sleep interval(seconds) between two network requests, default: 60'
    )

    # cookies - filename, use cookies(json) provided to scrape as logined
    argparser.add_argument(
        '-c', '--cookies',
        nargs = 1,
        help = 'specify the user cookies(json format file) to be used, needed if you want to scrape as login status'
    )

    # base-url - sub-url scraper to replace with default '/', must be a valid sub-url defined in constant.py
    argparser.add_argument(
        '--begin-url',
        nargs = 1,
        help = 'begin sub-URL to replace default "/", "/user/blackdragonf" for example'
    )

    # skip-check - when specified, skip integrity check step
    argparser.add_argument(
        '--skip-check',
        action='store_true',
        help = 'skip integrity check(ONLY works in default mode) between database and images'
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

    # set signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # initialize database and scraper
    db = database.Database('fa_scraper.db')
    if util.if_cache_exists():
        # trying to load scraper from scraper.cache
        with open('scraper.cache', 'rb') as temp:
            scraper = pickle.load(temp)
            logger.info('continued with last scrapying progress, with %u scrapied urls and %u scrapying urls.' % (len(scraper.scrapied_set), len(scraper.scrapying_queue)))
        # os.remove('scraper.cache') commented for potiential error

        # fix Scraper lazy load *manually* because pickle will NOT save class variable
        scrapy.Scraper.SCRAPIED_BASE = True
        
        # reset scrapy_interval
        scraper.scrapy_interval = arguments.scrapy_interval[0]
    else:
        cookies = {}
        if arguments.cookies:
            # load provided cookies from file
            cookies = util.get_cookies(arguments.cookies[0])
    
        begin_url = None
        if arguments.begin_url:
            # alternative begin-url specified
            begin_url = arguments.begin_url[0]

        scraper = scrapy.Scraper(arguments.scrapy_interval[0], cookies, begin_url)
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
        expired_artwork_ids = db.get_expired_artwork_ids(arguments.expire_time[0])
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
