import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# Panegyricus is written a little differently from the books.
def parsepane(ptags, c, colltitle, title, author, date, URL):
    chapter = 0
    verse = '-1'
    # chapters are roman numberals (bold, in their own <p> tag); verses are sentences.
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
        if text.startswith("Pliny the Younger\n"):
            continue
        # ababababa the chapters are roman numerals!
        potchap = p.find('b')
        if potchap is not None:
            chapter = text[:-1] # rid of the period at the end
        else:
            # not a chapter paragraph
            text = re.split('\.', text) # the sentences are verses
            for element in text:
                if element is None or element == '' or element.isspace():
                    text.remove(element)
            for count, item in enumerate(text):
                if item is None:
                    continue
                else:
                    verse = count+1
                    passage = item
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, passage.strip(), URL, 'prose'))



# Case 2: Sections are split by <p> tags and subsections by un/bracketed numbers.
def parsecase2(ptags, c, colltitle, title, author, date, URL):
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
        if text.startswith("Pliny the Younger\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        if text.isnumeric():
            chapter = text
            continue
        if text.startswith('C. PLIN'):
            chapter += ' '
            chapter += text
            continue
        text = re.split('([IVX]+)\.\s|([0-9]+)\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric() or len(item) < 5:
                verse = item
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
    collURL = 'http://www.thelatinlibrary.com/pliny.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Pliny the Younger'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = 'EPISTULAE'
            booknum_a = textsoup.find('p', class_='pagehead')
            booknum_b = booknum_a.find(text = True).replace('C. PLINII CAECILII SECVNDI EPISTVLARVM','')
            title += booknum_b
            getp = textsoup.find_all('p')
            if url == 'http://www.thelatinlibrary.com/pliny.panegyricus.html':
                title = booknum_a.find(text=True).replace('C. PLINII CAECILI SECVNDI ','')
                parsepane(getp, c, colltitle, title, author, date, url)
            else:
                parsecase2(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
