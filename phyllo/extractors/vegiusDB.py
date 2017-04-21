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
    j = 0
    getp = soup.find_all('p')[:-1]
    i=0
    s1=[]
    s2=[]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        if i<2:
            if p.b:
                chapter = p.b.text
                i += 1
            else:
                sen = p.text
                s1 = sen.split('\n')
                while j < len(s1):
                    s1[j] = s1[j].strip()
                    j += 1
                l=1
                for s in s1:
                    if s!='':
                        sentn=s
                        num=l
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        l+=1
                i+=1
        else:
            chapter='-'
            sen = p.text
            s1 = sen.split('\n')
            while j < len(s1):
                s1[j] = s1[j].strip()
                j += 1
            l = 1
            for s in s1:
                if s != '':
                    sentn = s
                    num = l
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    l += 1
            i += 1


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/vegius.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='Vegius: Aeneidos Supplementum'

    author = 'Vegius'
    author = author.strip()
    collectiontitle='LIBRI XII AENEIDOX SVPPLEMENTVM MAPHAEI VEGII'
    date = ''

    print(author)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Scaliger'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()