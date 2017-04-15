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

global r

r = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
s2=[]
def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    [e.extract() for e in soup.find_all('br')]
    getp = soup.find_all('p')[:-1]
    j=1
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        if sen.isupper():
            chapter=sen
        else:
            s1=sen.split('\n')
            j=1

            for s in s1:
                if j+1<=len(s1)-1:
                    s= s1[j].strip() + ' ' + s1[j+1].strip()
                    j+=2
                    s2.append(s)
            i=1
            for h in s2:
                if h != ' ':
                    sentn = h
                    num = i
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    i += 1





def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/cotta.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='CARMINA'

    author = 'Giovanni Cotta'
    author = author.strip()
    collectiontitle = biggsSOUP.title.string
    collectiontitle=collectiontitle.strip()
    date = '1480-1510'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Giovanni Cotta'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()