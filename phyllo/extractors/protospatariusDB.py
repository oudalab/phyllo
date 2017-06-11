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
    s1 = []
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('span')]
    [e.extract() for e in soup.find_all('a')]
    [e.replaceWith('9999') for e in soup.find_all('b')]
    for x in soup.find_all():
        if len(x.text) == 0:
            x.extract()
    getp = soup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass

        sen = p.text
        sen = sen.strip()
        chapter = sen[:11]
        chapter = chapter.strip()
        sen = sen[11:]
        sentn = sen.strip()
        print(collectiontitle)
        print(title)
        print(author)
        print(date)
        print(chapter)
        print(num)
        print(sentn)
        print(url)


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/protospatarius.shtml'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Protospatariu: Breve Chronicon'

    author = 'Protospatariu'
    author = author.strip()
    collectiontitle = 'LUPUS PROTOSPATARIUS BARENSIS RERUM IN REGNO NEAPOLITANO GESTARUM BREVE CHRONICON'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Protospatariu'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()