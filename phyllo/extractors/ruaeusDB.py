# has organizational issues everywhere.

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

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '1'
    j = 1
    inv = ['i', 'u']
    get = strip_tags(soup, inv)
    [e.extract() for e in get.find_all('br')]
    [e.extract() for e in get.find_all('center')]
    [e.extract() for e in get.find_all('table')]
    getp = get.find_all('p')
    print(getp)
    i = 0
    c=1
    s1=[]
    s=''
    s2=[]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        if c<8:
            if p.b:
                chapter = p.b.text
                c += 1
                print(c)
            else:
                sen = p.text
                k = 1
                for s in sent_tokenize(sen):
                    if s.strip().startswith("Liber"):
                        s = s.replace(chapter,'')
                    if s.isupper():
                        g = 1
                    else:
                        sentn = s
                        num = k
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        k += 1
        else:
            if p.b:
                chapter = p.b.text
                sen = p.text
                k = 1
                for s in sent_tokenize(sen):
                    if s.strip().startswith("Liber"):
                        s = s.replace(chapter,'')
                    sentn = s
                    num = k
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    k += 1


def strip_tags(soup, invalid_tags):
    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""

            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(str(c), invalid_tags)
                s += str(c)

            tag.replaceWith(s)

    return soup


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/ruaeus.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='Argumentum Aeneidos cum XII librorum argumentis scripsit Carolus Ruaeus (soc. Iesu.) ex libro ' \
          '"ad usum serenissimi Delphini, Philadelphia MDCCCXXXII p. Ch. n. '

    author = 'Ruaeus'
    collectiontitle='Ruaeus Aeneid'
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Ruaeus'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
