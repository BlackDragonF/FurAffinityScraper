from fa_scraper import *

import argparse


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--log-level", \
        nargs = 1, \
        choices = ["debug", "info", "warning", "error", "critical"], \
        help = "console log level")

    arguments = argparser.parse_args()

    util.prepare(arguments.log_level[0].upper())
    conn = db.connect_db("fa_scraper.db")
    db.create_artwork_table(conn)
    # scraper = scrapy.Scraper()
    # while True:
    #     scraper.next_arkwork()
    # db.close_db(conn)
