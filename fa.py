from fa_scraper import *

import argparse
import sys

def parse_arguments():
    argparser = argparse.ArgumentParser(
        usage = "%s [OPTION]" % sys.argv[0],
        description = "A scraper of furaffinity.net written with python."
    )

    argparser.add_argument(
        "--log-level",
        nargs = 1,
        default = ["info"],
        choices = ["debug", "info", "warning", "error", "critical"],
        help = "sets verbosity level for console log messages, default: info"
    )
    argparser.add_argument(
        "--scrapy-mode",
        nargs = 1,
        default = ["default"],
        choices = ["default", "update", "fusion"],
        help = "sets scrapying mode, default: default"
    )
    argparser.add_argument(
        "--expire-time",
        nargs = 1,
        type = int,
        default = 15,
        help = "sets expire time(days) for scrapied images, default: 15"
    )
    argparser.add_argument(
        "--skip-check",
        action="store_true",
        help = "skip integrity check between database and images"
    )

    arguments = argparser.parse_args()
    return arguments

if __name__ == "__main__":
    arguments = parse_arguments()

    util.prepare(arguments.log_level[0].upper())
    conn = db.connect_db("fa_scraper.db")
    db.create_artwork_table(conn)
    # scraper = scrapy.Scraper()
    # while True:
    #     scraper.next_arkwork()
    # db.close_db(conn)
