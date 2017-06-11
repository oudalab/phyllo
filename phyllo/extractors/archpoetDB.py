import sqlite3
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize


def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = 0
    sen = ""
    sv = ""
    num = 1
    s1 = []
    s2 = []
    sx = ""
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('span')]
    getp = soup.find_all('p')
    i = 1
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass

        if p.b:
            chapter = p.b.text
            num = 0
        else:
            sen = p.text
            sen = sen.replace('\n', '')
            sen = sen.replace('\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', ' ')
            sen = sen.strip()
            if sen != '':
                num += 1
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
            #print(s1)


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/archpoet.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Archpoeta'

    author = 'Archpoeta'
    author = author.strip()
    collectiontitle = 'ARCHIPOETA'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Archpoeta'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()