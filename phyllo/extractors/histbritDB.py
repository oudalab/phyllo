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
    # [e.extract() for e in soup.find_all('span')]
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
        if p.b:
            if p.b.text.strip().isnumeric():
                num = p.b.text.strip()
                sen = p.text
                sen = sen.strip()
                if sen != '':
                    for s in sen.split('\n'):
                        sentn = s.strip()
                        if len(sentn) < 2:
                            continue
                        if sentn.startswith(num):
                            sentn = sentn.replace(num, '').strip()
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))

            else:
                chapter = p.b.text
                chapter = chapter.strip()
        else:
            sen = p.text
            sen = sen.strip()
            if sen != '':
                for s in sen.split('\n'):
                    sentn = s.strip()
                    if len(sentn) < 2:
                        continue
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/histbrit.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Historia Brittonum'

    author = 'Anonymous'
    author = author.strip()
    collectiontitle = 'HISTORIA BRITTONUM'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE title = 'HISTORIA BRITTONUM'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
