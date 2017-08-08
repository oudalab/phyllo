import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
from phyllo_logger import logger
import nltk
from itertools import cycle

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    sen = ""
    s=''
    h=''
    s1=[]
    s2=[]
    inv=['b','i','u']
    get=strip_tags(soup, inv)
    getp=get.findAll('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        if p.string != None:
            sen=str(p.string)
            s=''.join(i for i in sen if not i.isdigit())
            s1.append(s)
    for i,f in enumerate(s1):
        if i==0:
            s2.append(f.strip())
        else:
            s2.append(f[3:].strip())
    j=1
    for f in s2:
        chapter=str(j)
        i=1
        for v in sent_tokenize(f):
            if v != '.':
                sentn = v
                num = i
                if sentn.startswith('Quae ut prim'): # correction for chap 4.
                    chapter = 4
                    num = 1
                    i = 1 # reset counter
                    j+=1 # increase chapter counter
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i += 1
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
    biggsURL = 'http://www.thelatinlibrary.com/biggs.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='EXPEDITIO FRANCISCI DRAKI EQUITIS ANGLI'

    author = biggsSOUP.p.contents[0].strip()
    author = author.strip().title()
    collectiontitle = author
    date = 1588

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'WALTER BIGGES'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
