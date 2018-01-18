from bs4 import BeautifulSoup

import re

import logging
logger = logging.getLogger('default')

def parse_artwork_site(html):
    bs = BeautifulSoup(html, "html.parser")
    result = {}

    image_tag = bs.find("img", {"id": "submissionImg"})
    if image_tag != None:
        result["download_link"] = "http:" + image_tag["src"]

    result["artwork_sites"] = bs.findAll("a", href=re.compile("^(/view/)"))

    return result
