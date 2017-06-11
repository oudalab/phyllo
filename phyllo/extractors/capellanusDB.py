import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger
import regex

from regex import Regex

import nltk

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    if url == 'http://www.thelatinlibrary.com/capellanus/capellanus2.html':
        chapter = '-'
        s1 = []
        num = 0
        [e.extract() for e in soup.find_all('br')]
        [e.extract() for e in soup.find_all('table')]
        [e.extract() for e in soup.find_all('div')]
        getp = soup.find_all('p')
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
                chapter = p.b.text
                chapter = chapter.strip()
            else:
                sen = p.text
                sen = sen.strip()
                sen1 = ''.join([i for i in sen if not i.isdigit()])
                sen1 = sen1.replace('[]', '')
                sen1 = sen1.strip()
                j=1
                if i < 400:
                    for s in sent_tokenize(sen1):
                        sentn = s
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        num+=1
                        i += 1
                else:
                    for s in sen1.split('\n'):
                        sentn = s
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        num+=1
    else:
        chapter = '-'
        s1 = []
        num = 0
        [e.extract() for e in soup.find_all('br')]
        [e.extract() for e in soup.find_all('table')]
        [e.extract() for e in soup.find_all('div')]
        getp = soup.find_all('p')
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
                chapter = p.b.text
                chapter = chapter.strip()
            else:
                sen = p.text
                sen = sen.strip()
                sen1 = ''.join([i for i in sen if not i.isdigit()])
                sen1 = sen1.replace('[]', '')
                sen1 = sen1.strip()
                num = 1
                if i < 400:
                    for s in sent_tokenize(sen1):
                        sentn = s
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        num+=1


def main():
    # collection name: Abelard/Abaelard
    abeURL = 'http://www.thelatinlibrary.com/capellanus.html'
    siteURL = 'http://www.thelatinlibrary.com'
    abeOpen = urllib.request.urlopen(abeURL)
    soup = BeautifulSoup(abeOpen, "html5lib")
    textsURL = []

    # search for links to his works
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))
    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/medieval")
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    author = soup.title.string
    author = author.strip()
    collectiontitle = soup.td.contents[0].strip()
    date = soup.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    date = date.strip()

    title = []
    for link in soup.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html'):
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Andreas Capellanus'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()