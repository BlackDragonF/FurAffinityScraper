from bs4 import BeautifulSoup

import re

import logging
logger = logging.getLogger('default')

def get_state(html_tag, state_name):
    match = re.search(re.compile("<b>" + state_name + ":</b> (.+?)<br/>"), str(html_tag))
    if match:
        return match.group(1)

def get_keywords(keywords_tag):
    keywords = re.findall(re.compile("<a href=\".*\">(.+?)</a>"), str(keywords_tag))
    if keywords:
        return keywords

def get_author(cat_tag):
    match = re.search(re.compile("<b>(.+)</b>"), str(cat_tag))
    if match:
        return match.group(1)

def get_name(cat_tag):
    match = re.search(re.compile("<a href=\".*\">(.+)</a>"), str(cat_tag))
    if match:
        return match.group(1)

def get_artwork_attr(html_tag, attr):
    category = get_state(html_tag, "Category")
    if category:
        attr["category"] = category
    else:
        logger.debug("unable to get category.")

    theme = get_state(html_tag, "Theme")
    if theme:
        attr["theme"] = theme
    else:
        logger.debug("unable to get theme.")

    species = get_state(html_tag, "Species")
    if species:
        attr["species"] = species
    else:
        logger.debug("unable to get species.")

    gender = get_state(html_tag, "Gender")
    if gender:
        attr["gender"] = gender
    else:
        logger.debug("unable to get gender.")

    favorites = get_state(html_tag, "Favorites")
    if favorites:
        attr["favorites"] = int(favorites)
    else:
        logger.debug("unable to get favorites.")

    comments = get_state(html_tag, "Comments")
    if comments:
        attr["comments"] = int(comments)
    else:
        logger.debug("unable to get comments.")

    views = get_state(html_tag, "Views")
    if views:
        attr["views"] = int(views)
    else:
        logger.debug("unable to get views.")

    resolution = get_state(html_tag, "Resolution")
    if resolution:
        resolution = resolution.split('x')
        if (len(resolution) >= 2):
            attr["width"] = int(resolution[0])
            attr["height"] = int(resolution[1])
    else:
        logger.debug("unable to get resolution.")

    keywords_tag = html_tag.find("div", {"id": "keywords"})
    keywords = get_keywords(keywords_tag)
    if keywords:
        attr["keywords"] = keywords
    else:
        logger.debug("unable to get keywords.")

    attr["adult"] = False

def get_artwork_info(html):
    bs = BeautifulSoup(html, "html.parser")
    info = {}
    attr = {}

    image_tag = bs.find("img", {"id": "submissionImg"})
    if image_tag and image_tag.has_attr("src"):
        download_link = "https:" + image_tag["src"]
        logger.debug("retrieved download link - '%s'." % download_link)
        info["download_link"] = download_link
    else:
        logger.debug("unable to retrieve download link.")

    artwork_cat = bs.find("td", {"class": "cat"})
    artwork_stats = bs.find("td", {"class": "alt1 stats-container"})
    if artwork_cat:
        author = get_author(artwork_cat)
        name = get_name(artwork_cat)
        if author:
            attr["author"] = author
        else:
            logger.debug("unable to get author.")
        if name:
            attr["name"] = name
        else:
            logger.debug("unable to get name.")
    if artwork_stats:
        posted = artwork_stats.find("span", {"class": "popup_date"})
        if posted and posted.has_attr("title"):
            attr["posted"] = posted["title"]
            get_artwork_attr(artwork_stats, attr)
        else:
            logger.debug("unable to get posted time.")
    logger.debug("artwork attributes collected.")
    info["attributes"] = attr

    artwork_sites = bs.findAll("a", href = re.compile("^(/view/)"))
    if artwork_sites:
        artwork_sites = list(map(lambda tag: tag.get("href"), artwork_sites))
        logger.debug("retrieved %d artwork sites." % len(artwork_sites))
        info["artwork_sites"] = artwork_sites
    else:
        logger.debug("0 artwork sites retrieved.")

    return info
