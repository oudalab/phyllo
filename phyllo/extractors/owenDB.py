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
    chapter = '-'
    j = 1
    inv = ['blockqoute']
    get = strip_tags(soup, inv)
    [e.extract() for e in get.find_all('br')]
    [e.extract() for e in get.find_all('center')]
    getp = get.find_all('p')
    i = 1
    k=1
    if i==1:
        chapter='Venus'
        i+=1
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        if p.i:
            chapter=p.i.text
            chapter=chapter.strip()
        elif j<24:
            sen=p.text
            sen=sen.replace('\xa0\xa0\xa0\xa0\xa0','')
            sen=sen.strip()
            sentn=sen
            num=k
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))
            j+=1

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
    biggsURL = 'http://www.thelatinlibrary.com/owen.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='Select epigrams'

    author = 'John Owen'
    author = author.strip()
    collectiontitle='Iohannes Audoenus'
    date = '1564-1622'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'John Owen'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
