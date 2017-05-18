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
    idx=True
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('sup')]
    [e.extract() for e in soup.find_all('a')]
    [e.extract() for e in soup.find_all('table')]
    getp=soup.find_all('p')
    i=0
    j = 1
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
            idx=False
        if idx:
            chapter=str(j)
            sen = str(p.text).strip()
            k=1
            for s in sent_tokenize(sen):
                num=k
                sentn=str(s)
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                k+=1
            j+=1
        elif not idx:
            if not i==32:
                num=i
                sentn = str(p.text).strip()
                if sentn.startswith("Notes:"):
                    i +=1
                    continue
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i += 1



def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/1644.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title="Polono Missa Mozambico"

    author = "Michaele Boym"
    author = author.strip()
    collectiontitle = "Cafraria1 a Patre Michaele Boym Polono Missa Mozambico"
    collectiontitle=collectiontitle.strip()
    date = 1644

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Michaele Boym'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
