from fa_scraper import *


if __name__ == "__main__":
    util.prepare()
    conn = db.connect_db("fa_scraper.db")
    db.create_artwork_table(conn)
    scraper = scrapy.Scraper()
    scraper.next_arkwork()
    db.close_db(conn)
