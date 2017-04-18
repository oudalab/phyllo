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
    inv = ['i', 'u']
    get = strip_tags(soup, inv)
    [e.extract() for e in get.find_all('br')]
    j = 1
    getp = get.find_all('p')[:-1]
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        k = 1
        if url=='http://www.thelatinlibrary.com/petrarch.rom.html' or url=='http://www.thelatinlibrary.com/petrarch.numa.html':
            sen=p.text
            sen=sen.strip()
            sen=sen[3:].strip()
            for s in sent_tokenize(sen):
                sentn=s.strip()
                chapter=str(j)
                num=k
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                k+=1
            j+=1
        elif url=='http://www.thelatinlibrary.com/petrarchmedicus.html':
            if p.b:
                chapter=p.b.text
            else:
                sen=p.text
                for s in sent_tokenize(sen):
                    sentn=s.strip()
                    num=k
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    k+=1
        else:
            sen=p.text
            sen=sen.strip()
            for s in sent_tokenize(sen):
                sentn=s.strip()
                num=k
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                k+=1
            j+=1

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
    biggsURL = 'http://www.thelatinlibrary.com/petrarch.html'
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
    author = 'Francis'+' '+author.strip()
    collectiontitle = biggsSOUP.div.contents[0].strip()
    date = '-'

    title = []
    for link in biggsSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html'):
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Francis Petrarch'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()