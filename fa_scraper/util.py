import os
import logging
import logging.config

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
            'level': 'INFO',
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

def prepare():
    logging.config.dictConfig(config)
    logger = logging.getLogger('default')
    if not os.path.exists("images"):
        os.mkdir("images")
        logger.info("result directory 'images' created.")
    
