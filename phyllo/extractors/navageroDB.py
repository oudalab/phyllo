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
    j = 1
    s1=[]
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    i = 1
    s2=[]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        if sen.isupper():
            chapter=sen.strip()
        elif p.i:
            chapter=chapter+' '+p.i.text
            chapter=chapter.strip()
        else:
            s1=sen.split('\n')
            i=1
            while i+1<len(s1):
                s=s1[i].strip()+' '+s1[i+1].strip()
                s2.append(s)
                i+=2
    k = 1
    for h in s2:
        if h!=' ':
            sentn = h
            num = k
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))
            k += 1


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/navagero.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='ANDREA NAVAGERO'

    author = 'Andrea Navagero'
    author = author.strip()
    collectiontitle='LUSUS'
    date = '1483-1529'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Andrea Navagero'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
