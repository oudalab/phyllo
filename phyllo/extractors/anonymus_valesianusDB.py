import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


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
        textsURL.remove("http://www.thelatinlibrary.com/misc.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/valesianus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    #date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    date = 'no date found'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Anonymus Valesianus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            chapter = '-1'
            verse = 1

            for p in getp:
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
                text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
                for element in text:
                    if element is None or element == '' or element.isspace():
                        text.remove(element)
                # The split should not alter sections with no prefixed roman numeral.
                if len(text) > 1:
                    i = 0
                    while text[i] is None:
                        i += 1
                    chapter = text[i]
                    i += 1
                    while text[i] is None:
                        i += 1
                    passage = text[i].strip()
                    verse = 1
                else:
                    passage = text[0]
                    verse += 1
                # check for that last line with the author name that doesn't need to be here
                if passage.startswith('The'):
                    continue
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
