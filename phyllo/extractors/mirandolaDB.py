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
    j = 1
    s1=[]
    s3=''
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')

    if url == 'http://www.thelatinlibrary.com/mirandola/oratio.shtml':
        i = 1
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation', 'pagehead']:  # these are not part of the main t
                    continue
            except:
                pass
                sen = p.text
                sen = sen.strip()
                if sen.startswith('§'):
                    chapter = str(j)
                    j += 1
                else:
                    for s in sen:
                        if s.isdigit():
                            sen = sen.replace(s, '')
                    s3 = sen[2:]
                    s3 = s3.replace('\n     ', '')
                    if s3!='':
                        sentn = s3
                        num = i
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        i += 1
    else:
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation', 'pagehead']:  # these are not part of the main t
                    continue
            except:
                pass
            sen = p.text
            s1 = sen.split('\n')
            s2 = []
            i = 0
            while i + 1 < len(s1):
                s = s1[i].strip() + ' ' + s1[i + 1].strip()
                s = s.strip()
                if s != '':
                    s2.append(s)
                i += 2
            for s in s2:
                chapter=str(i)
                num=i
                sentn=s
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i+=1

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/mirandola.html'
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
    collectiontitle = biggsSOUP.td.contents[0].strip()
    date = biggsSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    date=date.strip()

    title = []
    for link in biggsSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html') and link.get('href') != 'http://ourworld.cs.com/latintexts/index.htm' and link.get('href') != 'may/maytitle.shtml':
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Pico della Mirandola'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()