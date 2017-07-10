import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# Gellius Case 1
def parsegel1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = '-1'
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
        if text.startswith("Gellius\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # Chapters start with a roman numeral
        text = re.split('^([IVX]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        chapter = text[0]
        verse = '-1'
        text = ''.join(text).replace(chapter, '').strip()
        # Verses split by un/bracketed numbers or roman numerals followed by full stop
        text = re.split('([IVX]+)\.\s|([0-9]+)\.\s|\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        pattern = re.compile('([IVX]+)|([0-9]+)|\[([0-9]+)\]')
        for item in text:
            if item is None:
                continue
            if item == '' or item.isspace():
                continue
            if pattern.match(item):
                verse = item
                continue
            else:
                passage = item
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), URL, 'prose'))

# Gellius Case 2: Capitula
def parsegel2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = '-1'
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
        if text.startswith("Gellius\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # Chapters are bold and on their own paragraph
        # find chapter
        chapter_f = p.find('b')
        if chapter_f is not None:
            chapter = p.get_text().strip()
            verse = '-1'
            continue
        text = ''.join(text).replace(chapter, '').strip()
        # Verses split by roman numerals followed by full stop
        text = re.split('([IVX]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        pattern = re.compile('([IVX]+)')
        for item in text:
            if pattern.match(item):
                verse = item
                continue
            else:
                passage = item
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
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/gellius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Aulus Gellius'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            # finally, parse
            if not url.endswith('capitula.shtml'):
                parsegel1(getp, c, colltitle, title, author, date, url)
            else:
                parsegel2(getp, c, colltitle, title, author, date, url)
            logger.info('Parsed '+url)


    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
