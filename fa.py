from fa_scraper import util
from fa_scraper import scrapy

if __name__ == "__main__":
    util.prepare()
    scraper = scrapy.Scraper()
    scraper.next_arkwork()
#  for view in bs.findAll("a", href = re.compile("^(/view/)"))
