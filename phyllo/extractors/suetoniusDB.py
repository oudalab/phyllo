import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# Case 1: Sections split by numbers (Roman or not) followed by a period, or bracketed. Subsections split by <p> tags
def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 1
    # fix off-by=one the easy way.
    if URL.endswith('virgil.html') or URL.endswith('horace.html') or URL.endswith('tibullus.html') \
            or URL.endswith('persius.html') or URL.endswith('lucan.html') or URL.endswith('pliny.html') \
            or URL.endswith('crispus.html'):
        verse = 0

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
        # Skip empty paragraphs. and skip the last part with the collection link.
        if len(text) <= 0 or text.startswith('Suetonius\n'):
            continue
        text = re.split('^([IVXL]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        # The split should not alter sections with no prefixed roman numeral.
        if len(text) > 1:
            i = 0
            while text[i] is None:
                i+=1
            if text[i].isnumeric() and 'suet.nero' in URL:
                verse = int(text[i])
            else:
                chapter = text[i]
                verse = 1
            i+=1
            while text[i] is None:
                i+=1
            passage = text[i].strip()
        else:
            passage = text[0]
            verse+=1
        # check for that last line with the author name that doesn't need to be here
        if passage.startswith('Suetonius'):
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


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
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


# main code
def main():
    # The collection URL below. In this example, we have a link to Cicero.
    collURL = 'http://www.thelatinlibrary.com/suet.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Suetonius'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.
            parsecase1(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
