import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger
import nltk
from itertools import cycle


nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    sen=""
    s=[]
    [e.extract() for e in soup.find_all('br')]
    getp=soup.find_all('p')
    if url == 'http://www.thelatinlibrary.com/bultelius/bultelius1.html':
        for p in soup.findAll('p'):
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            if not p.table:
                sen=sen+p.text
    s=sen.split('\n\n')
    while '' in s:
        s.remove('')
    for j,b in enumerate(s):
        chapter=str(j+1)
        num=j+1
        sentn=b.strip()
        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                     num, sentn, url, 'prose'))
    if url == 'http://www.thelatinlibrary.com/bultelius/bultelius2.html':
        ch=''
        sen=''
        s=''
        h=''
        g=''
        global j
        j=1
        [e.extract() for e in soup.find_all('br')]
        for p in soup.findAll('p'):
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass

            if not p.table:
                if p.b:
                    ch=p.b.text
                else:
                    chapter='-'
                    j=1
                    sen=str(p.text)
                    s=sen[6:]
                    h=''.join(i for i in s if not i.isdigit())
                    g=h.split('()')
                    for v in g:
                        sentn=v.strip()
                        num=j
                        if ch:
                            chapter=ch
                        else:
                            chapter='-'
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        j=j+1


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    anselmURL = 'http://www.thelatinlibrary.com/bultelius.html'
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
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    author = anselmSOUP.title.string
    author = author.strip()
    collectiontitle = anselmSOUP.p.contents[0].strip()
    date = anselmSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    title = []
    for link in anselmSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'classics.html' and link.get('href') != 'christian.html'):
            title.append(link.string)

    i=0
    print(author)
    print(collectiontitle)
    print(date)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Bultelius'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
