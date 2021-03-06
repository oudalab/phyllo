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
    [e.extract() for e in soup.find_all('span')]
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
        s1 = re.sub(r'[[.*?]]', '', sen)
        if sen != '':
            if len(s1) < 16:
                chapter += 1
                # num = 0 # based on how verses are listed, it seems unnecessary to reset verse number
            else:
                for s in s1.split('\n'):
                    sentn = s.strip()
                    num += 1
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/garland.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    collectiontitle = 'John of Garland'

    author = 'John of Garland'
    title = 'INTECUMENTA SUPER OVIDIUM METAMORPHOSEOS SECUNDUM MAGISTRUM IOHANNEM ANGLICUM'
    date = '-'
    # 1246 A.D. is what used to be here, but I'm not sure where it came from or if it's the actual date..
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'John of Garland'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
