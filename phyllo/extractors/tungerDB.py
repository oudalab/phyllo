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
    inv = ['i', 'u', 'b']
    get = strip_tags(soup, inv)
    getp = get.find_all('p')[:-1]
    i=1
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
        sen=p.text
        sen=sen.strip()
        if sen!='':
            if sen[0].isdigit():
                sen = sen[3:].strip()
        i=1
        for s in sent_tokenize(sen):
            sentn=s
            num=i
            chapter=str(j)
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))
            i+=1
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
    biggsURL = 'http://www.thelatinlibrary.com/tunger.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='AUGUSTIN TÜNGER FACETIAE LATINAE ET GERMANICAE'

    author = 'Augustin Tunger'
    author = author.strip()
    collectiontitle='FACETIAE LATINAE ET GERMANICAE'
    date = '1486'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Scaliger'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()