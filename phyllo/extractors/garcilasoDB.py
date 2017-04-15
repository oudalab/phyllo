import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
from phyllo.phyllo_logger import logger
import nltk
from itertools import cycle

nltk.download('punkt')

from nltk import sent_tokenize

global i

i=1

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    i = 1
    [e.extract() for e in soup.find_all('br')]
    getp = soup.find_all('p')[:-1]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        if sen.isupper():
            chapter=sen.strip()
            i = 1
        else:
            if chapter == 'III.':
                sen=sen.replace('... ... ... ... ... ... ... ... ...', '')
                for s in sent_tokenize(sen):
                    sentn = s.strip()
                    num = i
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    i += 1
            else:
                sentn = sen.strip()
                num = i
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i += 1




def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/garcilaso.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='Carmina'

    author = 'Garcilaso de la Vega'
    author = author.strip()
    collectiontitle='Garcilaso de la Vega: Carmina'
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Garcilaso de la Vega'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()