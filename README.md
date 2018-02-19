# FurAffinity Scraper

## Description

A scraper to furaffinity.net written with python. Uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to parse html and [cfscrape](https://github.com/Anorov/cloudflare-scrape) to bypass Cloudflare's anti-bot page.

Any issues/pull requests are welcomed.

Project directory generally structs below:

    .
    ├── fa.py                   command-line tool to scrape furaffinity.net
    ├── fa_scraper              fa_scraper module
    │   ├── constant.py             global constant definition
    │   ├── database.py             database module
    │   ├── __init__.py             init
    │   ├── parse.py                parser module
    │   ├── scrapy.py               scraper module
    │   └── util.py                 utility functions
    ├── fa_scraper.db           database(generate by fa.py)
    ├── fa_scraper.log          log file(generate by fa.py)
    ├── images                  downloaded images(generate by fa.py)
    ├── LICENSE                 license
    ├── README.md               readme
    ├── requirements.txt        dependencies
    └── scraper.cache           cache used to resume(generate by fa.py)
### About

I don't want to make any misunderstanding here. And this scraper is ONLY used to learn network scrapying.

Setting scrapy-interval to a small value will lead to heavy burden on servers, which is ABSOLUTELY IMMORAL. Think twice before trying to use it.

## Requirements

Python 3.6+, Sqlite 3.22.0.

Node.js is also required for cf-scrape.

Other dependencies are listed in requirements.txt.

## Installation

1. Clone the repository by `git clone https://github.com/BlackDragonF/FurAffinityScraper`
2. Install dependencies by running `pip install -r requirements.txt`, you may consider using virtualenv
3. Make sure sqlite and node.js are installed
4. Execute command `python fa.py` to start the scraper with default arguments

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
                        sets sleep interval(seconds) between two network requests, default: 60
    --skip-check        skip integrity check(ONLY works in default mode) between database and images
    -c COOKIES, --cookies COOKIES
                        specify the user cookies(json format file) to be used,
                        needed if you want to scrape as login status

## Cookies

To specify cookies to scrape in login state please add --cookies/-c COOKIES_FILE_NAME in command-line arguments.

cookies file is a serialized json file which looks like:

    {
        "name1": "value1",
        "name2": "value2",
        "name3": "value3"
    }

You may use your web browser/web browser extension to get cookies of furaffinity.net.

## License

MIT License(c) 码龙黑曜/CoSidian
