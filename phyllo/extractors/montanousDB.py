import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
from phyllo.phyllo_logger import logger
import nltk
from itertools import cycle


def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    j = 1
    s1=[]
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    for p in getp:
        s2 = []
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        s1=sen.split('\n')
        i=1
        while i+1<len(s1):
            s=s1[i]+' '+s1[i+1]
            s=s.strip()
            s2.append(s)
            i+=1
        for s in s2:
            if s!='':
                sentn=s
                num=i
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/montanus.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='JOHANNES FABRICIUS MONTANUS'

    author = 'Fabricius Montanus'
    author = author.strip()
    collectiontitle='Fabricius Montanus: De Wilhelmo Thellio elegia'
    date = '-'
    print(author)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Fabricius Montanus'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()