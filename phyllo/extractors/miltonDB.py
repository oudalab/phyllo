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
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('span')]
    getp = soup.find_all('p')[:-1]
    i = 1
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        sen = sen.strip()
        s1 = sen.split('\n')
        l = 0
        s2 = []
        if len(s1) % 5 > 0:
            while l < (len(s1) - (len(s1) % 5)):
                s = s1[l] + ' ' + s1[l + 1] + ' ' + s1[l + 2] + ' ' + s1[l + 3] + ' ' + s1[l + 4]
                s=s.strip()
                s2.append(s)
                l += 5
            s = ''
            for i in range(len(s1) - (len(s1) % 5), len(s1)):
                s = s + s1[i] + ' '
            s2.append(s)
        i = 1
        for s in s2:
            if not s.startswith('From the Neo-Latin'):
                sentn=s
                chapter=str(i)
                num=i
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/milton.quintnov.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
        textsURL.remove("http://www.thelatinlibrary.com/https://eee.uci.edu/~papyri/homepage/webpage.html")
    logger.info("\n".join(textsURL))

    title='IN QUINTUM NOVEMBRIS'

    author = 'John Milton'
    author = author.strip()
    collectiontitle='JOHN MILTON'
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'John Milton'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()