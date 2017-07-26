import sqlite3
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize


def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = 1
    sen = ""
    num = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    #print(getp)
    i = 1
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
        if sen != '':
            if i == 1:
                chapter = sen
                i += 1
            else:
                if sen[0].isdigit():
                    chapter = sen[3:]
                    chapter = chapter.strip()
                else:
                    num = 1
                    for s in sen.split('\n'):
                        sentn = s
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'poetry'))
                        num += 1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/anon.nev.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Anonymus Neveleti'

    author = 'Anonymus Neveleti'
    author = author.strip()
    collectiontitle = 'ANONYMUS NEVELETI'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Anonymus Neveleti'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
