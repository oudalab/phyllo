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
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('center')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    i = 0
    k=1
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
        if i<4:
            sen=p.text
            sen=sen.strip()
            s1=sen.split('\n')
            l=0
            while l+1<len(s1):
                s=s1[l]+' '+s1[l+1]
                s2.append(s)
                l+=2
            s2.append(s1[len(s1)-1])
            k=1
            for h in s2:
                sentn=h
                num=k
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                k+=1
        i+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/rimbaud.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='VER ERAT'

    author = 'Arthur Rimbaud'
    author = author.strip()
    collectiontitle='ARTHUR RIMBAUD'
    date = '1854-1891'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Arthur Rimbaud'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()