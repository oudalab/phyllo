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
    [e.extract() for e in soup.find_all('i')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('span')]
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
        chapter += 1
        sen = p.text
        sen = sen.strip()
        s1 = ''.join([i for i in sen if not i.isdigit()])
        if s1.startswith('['):
            sen = s1[3:]
            sen = sen.strip()
        num = 0
        for s in sent_tokenize(sen):
            num += 1
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sen, url, 'prose'))

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/origo.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Origo gentis Langobardorum'

    author = 'Origo'
    author = author.strip()
    collectiontitle = 'ORIGO GENTIS LANGOBARDORVM'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Origo'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
