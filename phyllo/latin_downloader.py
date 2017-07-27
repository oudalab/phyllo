#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module contains code to download data from TheLatin Libary.com


Example:

    $ python3 latin_downloader.py


"""


import collections
import io
import os
from urllib.parse import urlparse

import requests

from bs4 import BeautifulSoup
from pybloomfilter import BloomFilter

from phyllo.phyllo_logger import logger


THELATINLIBRARY = "http://www.thelatinlibrary.com"


def latin_downloader():
    """Downloads all collections and saves it locally."""

    home_page = "http://www.thelatinlibrary.com/index.html"

    # A bloomfilter http://pybloomfiltermmap3.readthedocs.io/en/latest/ref.html
    visited = BloomFilter(10000000, 0.01, 'thelatinlibrary.bloom')
    to_visit = collections.deque()

    to_visit.append(home_page)

    # Main Loop
    while len(to_visit) > 0:
        # Get the next list of pages
        pageurl = to_visit.popleft()

        page = requests.get(pageurl)
        if not page.ok:
            logger.error("Couldn't find url. {}".format(pageurl))
            # page.raise_for_status()

        if page.text in visited or page.url in visited:
            continue

        soup = BeautifulSoup(page.text, "lxml")

        #  Save the page to a file
        url = urlparse(page.url)

        # Removing the first path before joining
        if url.path.startswith("/"):
            fileloc = os.path.join(url.netloc, url.path[1:])
        else:
            fileloc = os.path.join(url.netloc, url.path)

        os.makedirs(os.path.dirname(fileloc), mode=0o755, exist_ok=True)
        with io.open(fileloc, mode='w', encoding='utf-16') as newfile:
            logger.info("Created: {}".format(fileloc))
            newfile.write(soup.text)

        # Get the next pages
        for link in soup.find_all('a'):
            href = link.get('href')

            # No empty or mail links
            if href is None or len(href) == 0 or href.startswith('mailto:'):
                continue

            # Prevent non-local links e.g. http://www.apple.com
            if "http" in href and "thelatinlibrary" not in href:
                continue

            # No pdf or doc or docx fimes
            if href.endswith("pdf") or href.endswith("doc") or\
                    href.endswith("docx") or href.endswith("zip") or\
                    href.endswith("jpg"):
                continue

            # No local links, we already have the page
            if href.startswith("#"):
                continue

            # Annomalies
            if href in ("78b", "ovid/ovid/ovid.ponto.shtml", "bib.html",
                        "brevechronicon.html"):
                continue

            # Remove absolute paths
            if href.startswith('/'):
                href = href[1:]

            if "thelatinlibrary" in href:
                newpageurl = href
            else:
                newpageurl = os.path.join(THELATINLIBRARY, href or "")

            # Redirect to a specific index.html
            if href.endswith('/'):
                href = "{}index.html".format(href)
                logger.info("expanded href to: {}".format(href))

            # More anomolies
            if href in ["medieval"]:
                href = "{}/index.html".format(href)

            if newpageurl not in visited:
                to_visit.append(newpageurl)
                logger.info("page->newpage: {} {}".format(pageurl, newpageurl))

        # Add to the bloom table last
        visited.add(page.text)

        # Add the link too
        visited.add(page.url)


if __name__ == '__main__':
    latin_downloader()
