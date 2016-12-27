# Eutropius writes in prose.
# Chapters are split by capital letters and the verses by paragraph.
import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = -1
    verse = -1
    # entry deletion is done in main()
    for p in ptags:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        passage = ''
        text = p.get_text().strip()
        # Skip empty paragraphs.
        if len(text) <= 0 or text.startswith('Eutropius\n'):
            continue
        # sections split by bracketed roman numerals
        text = re.split('^\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        # The split should not alter sections with no prefixed roman numeral.
        if len(text) > 1:
            i = 0
            while text[i] is None:
                i+=1
            verse = text[i]
            i+=1
            while text[i] is None:
                i+=1
            passage = text[i].strip()
        else:
            passage = text[0]
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


def getBooks(soup, siteURL):
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    siteURL = 'http://www.thelatinlibrary.com'
    eutURL = 'http://www.thelatinlibrary.com/eutropius.html'
    eutOpen = urllib.request.urlopen(eutURL)
    eutSOUP = BeautifulSoup(eutOpen, 'html5lib')
    author = eutSOUP.title.string.strip()
    colltitle = eutSOUP.h1.string.strip()
    date = eutSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(eutSOUP, siteURL)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Eutropius'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            logger.info("Parsing " + url)
            parsecase1(getp, c, colltitle, title, author, date, url)


if __name__ == '__main__':
    main()
