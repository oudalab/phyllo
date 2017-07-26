import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = 0
    sen = ""
    num = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('span')]
    [e.extract() for e in soup.find_all('a')]
    for x in soup.find_all():
        if len(x.text) == 0:
            x.extract()
    getp = soup.find_all('p')
    #print(getp)
    i = 0
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        chapter += 1
        sen = p.text
        sen = sen.strip()
        if sen != '':
            num = 0
            for s in sen.split('\n'):
                sentn = s.strip()
                num += 1
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/inquisitio.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Inquisitio'

    author = 'Inquisitio'
    collectiontitle = "AN ELEVENTH-CENTURY INQUISITION OF ST. AUGUSTINE'S CANTERBURY"
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Inquisitio'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
