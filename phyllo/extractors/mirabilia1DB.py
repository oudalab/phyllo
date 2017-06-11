import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = 0
    sen = ""
    num = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('a')]
    for x in soup.find_all():
        if len(x.text) == 0:
            x.extract()
    getp = soup.find_all('p')
    #print(getp)
    i = 0
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen = p.text
        sen = sen.strip()
        sen = re.sub('<[^>]+>', '', sen)
        sen = sen.strip()
        s1 = ''.join([i for i in sen if not i.isdigit()])
        s1 = s1.strip()
        if s1 != '':
            if s1.startswith('.'):
                chapter += 1
                s1 = s1[2:]
                s1 = s1.strip()
                num = 0
                for s in sent_tokenize(s1):
                    sentn = s
                    num += 1
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
            else:
                num = 0
                for s in sent_tokenize(sen):
                    sentn = s
                    num += 1
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/mirabilia1.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Gregorius: Narratio de Mirabilibus Urbis Romae'

    author = 'Gregorius'
    author = author.strip()
    collectiontitle = 'MAGISTRI GREGORII NARRATIO DE MIRABILIBUS URBIS ROMAE'
    collectiontitle = collectiontitle.strip()
    date = '12th/13th century'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Gregorius'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()