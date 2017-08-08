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
    j = 1
    chapter="-1"
    s = ''
    sen = ''
    i = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    for p in soup.findAll('p'):
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        s = s + str(p.get_text()).strip()

    s1 = s.split('\n')
    while '' in s1:
        s1.remove('')
    for j,s in enumerate(s1):
        s1[j]=s.replace('\xa0', '')
    c = 0
    if url=='http://www.thelatinlibrary.com/balde1.html':
        for j in range(1, 4):
            s1.insert(7 + c, "9999")
            c = 7 + c + 1
    if url=='http://www.thelatinlibrary.com/balde2.html':
        for j in range(1, 7):
            s1.insert(7 + c, "9999")
            c = 7 + c + 1
    for s in s1:
        if s == "9999":
            sentn = sen
            sentn = re.split('\n', sentn)
            sentn = filter(lambda x: len(x) > 3, sentn)
            for v in sentn:
                num = i
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, v, url, 'poetry'))
                i = i+1
            sen = ""
        else:
            sen = sen + s + '\n'


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    baldeURL = 'http://www.thelatinlibrary.com/balde.html'
    baldeOPEN = urllib.request.urlopen(baldeURL)
    baldeSOUP = BeautifulSoup(baldeOPEN, 'html5lib')
    textsURL = []

    for a in baldeSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, link))

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/neo.html")
    logger.info("\n".join(textsURL))

    author = baldeSOUP.title.string
    author = author.strip()
    collectiontitle = baldeSOUP.p.contents[0].strip()
    date = baldeSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')


    title = []
    for link in baldeSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'classics.html' and link.get('href') != 'neo.html'):
            title.append(link.string)

    i=0
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Jacob Balde'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
