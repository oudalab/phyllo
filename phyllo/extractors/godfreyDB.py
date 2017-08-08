import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger
import nltk
from itertools import cycle

nltk.download('punkt')

from nltk import sent_tokenize

anselmSOUP=""
idx = -1
cha_array=[]
suburl = []
verse = []

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    num = 0
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('a')]
    getp = soup.find_all('p')[:-1]
    i = len(getp)
    for p in getp:
        # make sure it's not a paragraph without the main text

        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin'
                                                                                              'internal_navigation']:  # these are not part of the main text
                continue
        except:
            pass
        if p.i:
            if num == 10 and chapter == 'De Willelmo Fiscamnensi abbate':
                sentn = p.i.text
                sentn = sentn.strip()
                num += 1
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'poetry'))
            else:
                chapter = p.i.text
                chapter = chapter.strip()

        else:
            sen = p.text
            sen = sen.strip()
            num = 0
            for s in sen.split('\n'):
                sentn = s
                num += 1
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    anselmURL = 'http://www.thelatinlibrary.com/godfrey.html'
    anselmOPEN = urllib.request.urlopen(anselmURL)
    anselmSOUP = BeautifulSoup(anselmOPEN, 'html5lib')
    textsURL = []

    for a in anselmSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, link))

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/medieval.html")
    logger.info("\n".join(textsURL))

    author = anselmSOUP.title.string
    author = author.strip()
    collectiontitle = author.upper()
    date = anselmSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    title = []
    for link in anselmSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'classics.html' and link.get('href') != 'medieval.html'):
            title.append(link.string)

    i=0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Godfrey of Winchester'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
