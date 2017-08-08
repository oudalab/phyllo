import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
from phyllo_logger import logger
import nltk
from itertools import cycle

nltk.download('punkt')

from nltk import sent_tokenize
s1=[]
def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    j = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('font')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation', 'pagehead']:  # these are not part of the main t
                continue
        except:
            pass
        if p.text!='':
            sen = p.text
            sen = sen.strip()
            i = 1
            s1 = sen.split('\n')
            l = 0
            s2 = []
            if len(s1) % 5 > 0:
                while l < (len(s1) - (len(s1) % 5)):
                    s = s1[l] + ' ' + s1[l + 1] + ' ' + s1[l + 2] + ' ' + s1[l + 3] + ' ' + s1[l + 4]
                    s2.append(s)
                    l += 5
                s = ''
                for i in range(len(s1) - (len(s1) % 5), len(s1)):
                    s = s + s1[i] + ' '
                s2.append(s)
                l = 0
            elif len(s1) % 5 == 0:
                while l < len(s1):
                    s = s1[l] + ' ' + s1[l + 1] + ' ' + s1[l + 2] + ' ' + s1[l + 3] + ' ' + s1[l + 4]
                    s2.append(s)
                    l += 5
            if s2[0]!=' ':
                for x in s2:
                    sentn = x.strip()
                    num = i
                    chapter = str(j)
                    cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                (None, collectiontitle, title, 'Latin', author, date, chapter,
                                 num, sentn, url, 'prose'))
                    i += 1
                j += 1



def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/may.html'
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
        textsURL.remove("http://www.thelatinlibrary.com/may/maytitle.shtml")
        textsURL.remove("http://www.thelatinlibrary.com/http://ourworld.cs.com/latintexts/index.htm")
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
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Thomas May'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()
