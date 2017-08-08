import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


def main():
    siteURL = 'http://www.thelatinlibrary.com'
    aurURL = 'http://www.thelatinlibrary.com/victor.html'
    aurOPEN = urllib.request.urlopen(aurURL)
    aurSOUP = BeautifulSoup(aurOPEN, 'html5lib')
    textsURL = []

    for a in aurSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    author = aurSOUP.title.string
    author = author.strip()
    collectiontitle = aurSOUP.h1.contents[0].strip()
    date = aurSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Aurelius Victor'")
        title = ''
        for URL in textsURL:
            openSoup = urllib.request.urlopen(URL)
            soup = BeautifulSoup(openSoup, 'html5lib')
            try:
                title = soup.title.string.strip().title()
            except:
                pass
            ptags = soup.find_all('p')[:-1]
            chapter = '-1'
            sentence = '-1'
            for p in ptags:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                # chapters are bold numbers.
                potentialchap = p.find('b')
                if potentialchap is not None:
                    chapter = potentialchap.find(text=True)
                    a = p.b.decompose() # decompose returns value; store it to hide from the world.
                text = p.get_text()
                text = re.split('([0-9])\s|([0-3][1-9])\s', text) # bug: probably 0-9 and not 1-9
                for element in text:
                    if element is None:
                        continue
                    element = element.strip()
                    if element == '':
                        continue
                    if element.isnumeric():
                        if element == '0':
                            if sentence == '9':
                                sentence = '10'
                            elif sentence == '19':
                                sentence = '20'
                        else:
                            sentence = element
                        continue
                    else:
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, collectiontitle, title, 'Latin', author, date, chapter,
                                   sentence, element, URL, 'prose'))

if __name__ == '__main__':
    main()
