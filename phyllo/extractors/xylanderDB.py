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
    [e.extract() for e in soup.find_all('br')]
    j = 1
    getp = soup.find_all('p')[:-1]
    s1=[]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation','pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        sen=sen.strip()
        j=1
        for s in sent_tokenize(sen):
            if s.isupper():
                chapter=s
            else:
                if s.startswith('('):
                    sentn=s[3:]
                else:
                    sentn=s
                sentn=sentn.strip()
                num=j
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                j+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://thelatinlibrary.com/xylander/caesar.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='Vita Caesaris'
    title=title.strip()

    author = 'Xylander'
    author = author.strip()
    collectiontitle='GUILIEMLMUS XYLANDER'
    date = '1532-1576'

    print(author)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Xylander'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()