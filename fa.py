from fa_scraper import *

import argparse
import sys
import os

import json

import logging
import logging.config

def parse_arguments():
    argparser = argparse.ArgumentParser(
        usage = '%s [OPTION]' % sys.argv[0],
        description = 'A scraper of furaffinity.net written with python.'
    )

    argparser.add_argument(
        '--log-level',
        nargs = 1,
        default = ['info'],
        choices = ['debug', 'info', 'warning', 'error', 'critical'],
        help = 'sets verbosity level for console log messages, default: info'
    )
    argparser.add_argument(
        '--scrapy-mode',
        nargs = 1,
        default = ['default'],
        choices = ['default', 'update'],
        help = 'sets scrapying mode, default: default'
    )
    argparser.add_argument(
        '--expire-time',
        nargs = 1,
        type = int,
        default = 15,
        help = 'sets expire time(days) for scrapied images, default: 15'
    )
    argparser.add_argument(
        '--skip-check',
        action='store_true',
        help = 'skip integrity check between database and images'
    )

    arguments = argparser.parse_args()
    return arguments

def config_logger(console_log_level):
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
    artwork_ids = set(db.get_artwork_ids())
    os.chdir('images')
    logger.debug('changed working directory to images.')

    artworks = os.listdir('.')
    for artwork in artworks:
        if os.path.isfile(artwork):
            artwork_id = int(os.path.splitext(os.path.basename(artwork))[0])
            if artwork_id in artwork_ids:
                artwork_ids.remove(artwork_id)

    db.delete_artworks(artwork_ids)

    unscrapied_urls = list(map(util.generate_url_from_id, list(artwork_ids)))
    scraper.add_unscrapied_urls(unscrapied_urls)

    os.chdir('..')
    logger.debug('changed working directory to origin.')
    logger.info('%u wrong records removed from database.' % len(artwork_ids))


if __name__ == '__main__':
    arguments = parse_arguments()

    log_level = arguments.log_level[0].upper()
    logger = config_logger(log_level)

    if not util.create_images_directory():
        exit(-1)

    db = database.Database('fa_scraper.db')
    scraper = scrapy.Scraper()
    logger.info('initialization completed.')

    if not arguments.skip_check:
        check_and_fix_artworks(db, scraper)
        logger.info('integrity check completed.')
    else:
        logger.info('skipped integrity check.')

    scrapy_mode = arguments.scrapy_mode[0]
    logger.info('scrapy mode set to %s' % scrapy_mode)
    if scrapy_mode == 'default':
        while True:
            artwork = scraper.scrapy_pending_url()
            if artwork:
                artwork['Added'] = util.get_current_time()

                information = json.dumps(artwork)
                logger.info('scrapied artwork information: %s' % information)

                db.insert_or_replace_artwork(artwork)
                logger.info('completed to scrapy artwork with ID: %u.' % artwork.get('ID'))
    elif scrapy_mode == 'update':
        expired_artwork_ids = db.get_expired_artwork_ids(arguments.expire_time)
        logger.info('retrieved all expired artwork IDs.')

        for artwork_id in expired_artwork_ids:
            artwork = scraper.scrapy_expired_url(util.generate_url_from_id(artwork_id))
            if artwork:
                artwork['ID'] = artwork_id
                artwork['Added'] = util.get_current_time()

                information = json.dumps(artwork)
                logger.info('updated artwork information: %s' % information)

                db.insert_or_replace_artwork(artwork)
                logger.info('completed to re-scrapy expired artwork(with ID: %u)\'s info .' % artwork.get('ID'))

    db.close_db(conn)

    logger.info('exiting scraper...')
    exit(0)
