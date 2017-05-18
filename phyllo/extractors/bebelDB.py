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
    sen = ""
    s=''
    h=''
    s1=[]
    s2=[]
    i=1
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('sup')]
    [e.extract() for e in soup.find_all('a')]
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    getp=soup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass

        if p.b:
            chapter=p.b.text
        else:
            i=i+1
            sen=str(p.text).strip()
            j=1
            if i>190:
                rsen = ''
                s=sen.split('\n')
                for b in s:
                    rsen=rsen+' '+b.strip()
                sen=rsen
            for s in sent_tokenize(sen):
                if s.isspace():
                    continue
                sentn = str(s).strip()
                num = j
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                j += 1


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/bebel.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='FACETIARUM BEBELIANARUM'

    author = 'Heinrich Bebel'
    author = author.strip()
    collectiontitle = 'LIBER FACETIARUM BEBELIANARUM'
    collectiontitle=collectiontitle.strip()
    date = '1472-1518'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Heinrich Bebel'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
