import os

import logging
import logging.config

def config_logger(config_dict):
    logging.config.dictConfig(config_dict)
    logger = logging.getLogger('default')
    return logger

def prepare(console_log_level = "INFO"):
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
    logger = config_logger(config)
    logger.info("set console log level to %s" % console_log_level)

    if not os.path.exists('images'):
        os.mkdir('images')
        logger.info("result directory 'images' created.")
