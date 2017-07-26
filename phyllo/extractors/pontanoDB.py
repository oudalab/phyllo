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
    inv = ['i', 'u']
    get = strip_tags(soup, inv)
    [e.extract() for e in get.find_all('br')]
    [e.extract() for e in get.find_all('center')]
    [e.extract() for e in get.find_all('table')]
    getp = get.find_all('p')
    i = 0
    k=1
    s1=[]
    s=''
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
        sen=sen.replace('\xa0\xa0\xa0\xa0\xa0\xa0','')
        if sen.startswith('Eridanus') or sen.startswith('Hendecasyllabi'):
            chapter=sen
        else:
            if sen!='':
                s1 = sen.split('\n')
                i=1
                for s in s1:
                    sentn=s
                    num=i
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    i+=1

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
    biggsURL = 'http://www.thelatinlibrary.com/pontano.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='CARMINA EROTICA SELECTA'

    author = 'Giovanni Pontano'
    author = author.strip()
    collectiontitle='GIOVANNI GIOVIANO PONTANO'
    date = '1429-1503'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'John Owen'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
