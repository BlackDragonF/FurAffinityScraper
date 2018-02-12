# FurAffinity Scraper

## Description

A scraper to furaffinity.net written with python. Uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to parse html and [cfscrape](https://github.com/Anorov/cloudflare-scrape) to bypass Cloudflare's anti-bot page.

Any issues/pull requests are welcomed.

Project directory generally structs below:
.
|-fa_scraper/       source code directory
||-__init__.py      
||-constant.py      global constant definition
||-database.py      database module
||-parse.py         parser module
||-scrapy.py        main scrapy module  
||-util.py          set of utility functions
|-fa.py             command-line tools to scrapy furaffinity.net
|-images/           downloaded images directory
|-fa_scraper.db     sqlite database file that holds image attributes
|-fa_scraper.log    log file that holds detailed log
|-scraper.cache     cache file that used to resume scrapying process
|-requirements.txt  project dependencies
|-README.md         readme
|-LICENSE           license

### About

I don't want to make any misunderstanding here. And this scraper is ONLY used to learn network scrapying.
Setting scrapy-interval to a small value will lead to heavy burden on servers, which is ABSOLUTELY IMMORAL. Think twice before ever trying to use it.

## Requirements

Python 3.6+, Sqlite 3.22.0.
Node.js is also required for cf-scrape.
Other dependencies are listed in requirements.txt.

## Installation

1. Clone the repository by `git clone https://github.com/BlackDragonF/FurAffinityScraper`
2. Install dependencies by running pip install -r requirements.txt, you may consider using virtualenv
3. Execute command `python fa.py` to start the scraper with default arguments

## Usage
    usage: fa.py [OPTIONS]

    optional arguments:
    -h, --help          show this help message and exit
    --log-level {debug,info,warning,error,fatal}
                        sets verbosity level for console log messages, default: info
    --scrapy-mode {default,update}
                        sets scrapying mode, default: default
    --expire-time EXPIRE_TIME
                        sets expire time(days) for scrapied images, default: 15
    --scrapy-interval SCRAPY_INTERVAL
                        sets sleep interval(seconds) between two network requests, default: 15
    --skip-check        skip integrity check(ONLY works in default mode) between database and images


## License

MIT License(c) 码龙黑曜/CoSidian
