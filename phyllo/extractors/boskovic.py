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
    sen = ""
    s = ''
    h = ''
    s1 = []
    s2 = []
    i = 1
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('sup')]
    [e.extract() for e in soup.find_all('a')]
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    inv = ['i', 'u']
    get=strip_tags(soup, inv)
    getp = get.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        s = p.text
        if p.b:
            chapter=p.b.text
        else:
            i=i+1
            sen=str(p.text).strip()
            sen=sen.replace('[','')
            sen=sen.replace(']','')
            sen=re.sub(r'\d', '', sen)
            sen=re.sub(r'\x08','',sen)
            j=1
            if i>190:
                rsen = ''
                s=sen.split('\n')
                for b in s:
                    rsen=rsen+' '+b.strip()
                sen=rsen
            for s in sent_tokenize(sen):
                if s != 'Ty.' and s != 'Ly.' and s != 'Dor.' and s != 'cor.' and s != 'Elisus.' and s != 'Thyr.' and s != 'Mel.' and s != 'Daph.' and s != 'Thel.':
                    sentn = str(s).strip()
                    num = j
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    j += 1



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
    biggsURL = 'http://www.thelatinlibrary.com/boskovic.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    title='SOCIETATE JESU ECLOGAE'

    author = 'Bartolomej Boskovic'
    author = author.strip()
    collectiontitle = 'BARTHOLOMAEI BOSCOVICHIIE SOCIETATE JESU ECLOGAE'
    collectiontitle=collectiontitle.strip()
    date = '1772'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Bartolomej Boskovic'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()