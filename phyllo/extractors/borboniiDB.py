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
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen=sen+p.text
    s1=sen.split('\n')
    while '' in s1:
        s1.remove('')
    for j,s in enumerate(s1):
        s1[j] = ''.join(i for i in s if not i.isdigit())
    for j,b in enumerate(s1):
        sentn=str(b[2:])
        num=j
        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                     num, sentn, url, 'prose'))

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/ferraria.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='Vandoperani Ferraria'

    author = 'Nicolai Borbonii'
    author = author.strip()
    collectiontitle ='N. BORBONII VANDOPERANI FERRARIA. Quam scripsit annum agens XIIII '
    collectiontitle=collectiontitle.strip()
    date = '1503-1550'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Nicolai Borbonii'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()