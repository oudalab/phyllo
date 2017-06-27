import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = "Prologus"
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
        sen = p.text
        sen = sen.strip()
        if sen == 'Prologus.':
            i = 0
        elif sen.startswith('Capitulum'):
            chapter = sen.replace('\n', '')
            chapter = chapter.strip()
        else:
            num = 0
            for s in sent_tokenize(sen):
                num += 1
                sentn = s
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/oresmius.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'NICOLAUS ORESMIUS'

    author = 'NICOLAUS ORESMIUS'
    author = author.strip()
    collectiontitle = 'TRACTATUS DE ORIGINE, NATURA, IIURE ET MUTATIONIBUS MONETARUM'
    collectiontitle = collectiontitle.strip()
    date = '1320 - 1382'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'NICOLAUS ORESMIUS'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()