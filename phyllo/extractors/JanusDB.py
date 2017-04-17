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

global s1,s2

s1=[]

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    [e.extract() for e in soup.find_all('br')]
    getp = soup.find_all('p')[:-1]
    if url == 'http://www.thelatinlibrary.com/janus1.html':
        for p in getp:
            # make sure it's not a paragraph without the main text
            j = 1
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            if p.b:
                chapter = p.b.text
            else:
                sen = p.text
                s1=sen.split('\n')
                j = 1
                i=1
                s2 = []
                for s in s1:
                    if j + 1 <= len(s1) - 1:
                        s = s1[j].strip() + ' ' + s1[j + 1].strip()
                        j += 2
                        s2.append(s)
                for s in s2:
                    sentn = s
                    num = i
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    i += 1
    elif url == 'http://www.thelatinlibrary.com/janus2.html':
        chapter='-'
        for p in getp:
            # make sure it's not a paragraph without the main text
            j = 1
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            sen=p.text
            for s in sen:
                if s.isdigit():
                    sen=sen.replace(s,'')
            chapter=str(j)
            num=j
            sentn=sen[4:]
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/janus.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    for a in biggsSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, link))

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    author = biggsSOUP.title.string
    author = author.strip()
    collectiontitle = biggsSOUP.p.contents[0].strip()
    date = biggsSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    date=date.strip()

    title = []
    for link in biggsSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html'):
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Janus Secundus'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()