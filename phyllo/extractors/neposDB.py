import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def parsefrag(ptags, c, colltitle, title, author, date, URL):
    chapter = 0
    verse = -1
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
        if text.startswith("Nepos\n"):
            continue
        #find chapter
        potchap = p.find('b')
        if potchap is not None:
            chapter = potchap.find(text=True)
        else:
            text = re.split('\.\s', text)
            for element in text:
                if element is None or element == '' or element.isspace():
                    text.remove(element)
            for i, j in enumerate(text):
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           i+1, j.strip(), URL, 'prose'))

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
        if text.startswith("Nepos\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        text = re.split('([0-9]+)\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        chapter +=1
        simil = False
        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric() or len(item) < 5:
                verse = item
                try:
                    if int(verse) == int(chapter) and simil == False:
                        verse = 1
                        simil = True
                    if int(verse) == int(chapter)-2 and simil == False:
                        verse = 1
                        simil = True
                except:
                    pass
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
    # The collection URL below. In this example, we have a link to Cicero.
    collURL = 'http://thelatinlibrary.com/nepos.html'
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
        c.execute("DELETE FROM texts WHERE author='Cornelius Nepos'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            if url == 'http://www.thelatinlibrary.com/nepos/nepos.fragmenta.shtml':
                parsefrag(getp, c, colltitle, title, author, date, url)
            else:
                parsecase2(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
