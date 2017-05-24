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
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('center')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    i = 0
    k=1
    s1=[]
    s=''
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        sen=p.text
        j=1
        for s in sent_tokenize(sen):
            sentn=s.strip()
            if sentn == '':
                # I wish people used HTML properly.
                continue
            chapter=k
            num=j
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))
            j+=1
        k+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/patricius.html'
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

    author = biggsSOUP.font.string
    author = author.strip()
    collectiontitle = 'NOVA DE UNIVERSIS PHILOSOPHIA Tome I: Panaugia'
    date='1529-1597'

    title = []
    for link in biggsSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html') and link.get('href') != 'http://ourworld.cs.com/latintexts/index.htm' and link.get('href') != 'may/maytitle.shtml':
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'FRANCISCUS PATRICIUS'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()
