import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def parsecase2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 0
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
        if text.startswith("Medieval"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        if text.startswith('[Caput'):
            continue # these are tehcnically chapter numbers, but chapters are dealt with below
        # find chapter name
        chapterfind = p.find('i')
        if chapterfind is not None:
            chapterf2 = chapterfind.find(text=True)
            if chapterf2 == text[:-1]: # sometimes things that aren't the chapter are in italics
                chapter = chapterf2
            verse = 0
            continue
        if text.isupper():
            title = text # book title is in uppercase for whatever reason.
            continue
        # some pages are missing their book name entirely, or are hard to reach in the tree
        if URL.endswith('sermo1.shtml'):
            title = 'SERMO I'
        elif URL.endswith('sermo2.shtml'):
            title = 'SERMO II'
        elif URL.endswith('sermo3.shtml'):
            title = 'SERMO III'
        elif URL.endswith('sermo4.shtml'):
            title = 'SERMO IV'
        elif URL.endswith('sermo5.shtml'):
            title = 'SERMO V'
        elif URL.endswith('sermo.shtml'):
            title = 'SERMO JANUENSIS'
        elif URL.endswith('consol.shtml'):
            title = 'LIBER CONSULATIONIS ET CONSILII'
        elif URL.endswith('loquendi.shtml'):
            title = 'ARS LOQUENDI ET TACENDI'
        passage = text
        verse += 1
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))
    logger.info('Parsed '+ URL)


def getBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/medieval.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


# main code
def main():
    # The collection URL below and other information from the author's main page
    collURL = 'http://www.thelatinlibrary.com/albertanus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = author.upper()
    date = '-'

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Albertano of Brescia'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.
            parsecase2(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
