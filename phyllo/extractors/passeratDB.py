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
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        sen=sen.replace('[','')
        sen=sen.replace(']','')
        s1=sen.split('\n')
        for s in s1:
            if s!='':
                sentn = re.sub(r'[0-9]+$','',s)
                sentn = sentn.strip()
                if sentn == 'de nihilo':
                    chapter = sentn
                    continue
                num = j
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                j += 1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/passerat.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title='POEMA CI N. JOANNIS PASSERATI REGII IN ACADEMIA PARISIENSI PROFESSORIS AD ORNATISSIMVM VIRVM ERRICVM MEMMIVM '

    author = 'Jean Passerat'
    collectiontitle='JEAN PASSERAT'
    date = '1534-1602'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Jean Passerat'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
