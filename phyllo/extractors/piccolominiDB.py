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
    siteURL = 'http://www.thelatinlibrary.com'
    [e.extract() for e in soup.find_all('br')]
    j = 0
    inv = ['i', 'u']
    get = strip_tags(soup, inv)
    getp = get.find_all('p')
    s1=[]
    ur=[]
    tite=[]
    if url == 'http://www.thelatinlibrary.com/piccolomini.carmen.html':
        verse = 0
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            # find chapter
            chapter_f = p.get_text().strip()
            if chapter_f.startswith("Carmina"):
                chapter = chapter_f
                verse = 0
                continue
            verses = re.split('\n', chapter_f)
            for v in verses:
                if v is None:
                    continue
                elif v.isspace() or v == '':
                    continue
                # verse number assignment.
                verse+=1
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           verse, v.strip(), url, 'poetry'))

    elif url == 'http://www.thelatinlibrary.com/piccolomini.turcos.html':
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            sen = p.text
            sen = sen.strip()
            i = 1
            for s in sent_tokenize(sen):
                sentn = s
                num = i
                chapter = str(j)
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))
                i += 1
            j += 1

    else:
        [e.extract() for e in soup.find_all('table')]
        for a in soup.find_all('a', href=True):
            link = a['href']
            ur.append("{}/{}".format(siteURL, link))
            tite.append(a.string)
        i=0
        s1=[]
        for u in ur:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            getp = gestSoup.find_all('p')
            chapter = tite[i]
            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                sen = p.text
                sen = sen.strip()
                sen=sen.replace('\n                                                         ','')
                s1=sent_tokenize(sen)
                if s1!=[]:
                    l=1
                    for s in s1:
                        sentn=s
                        num=l
                        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, collectiontitle, title, 'Latin', author, date, chapter,
                                     num, sentn, url, 'prose'))
                        l+=1
            i+=1

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
    biggsURL = 'http://www.thelatinlibrary.com/piccolomini.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    texts = []
    textsURL=[]

    for a in biggsSOUP.find_all('a', href=True):
        link = a['href']
        texts.append("{}/{}".format(siteURL, link))

    # remove some unnecessary urls
    textsURL=texts[0:3]
    logger.info("\n".join(textsURL))

    author = biggsSOUP.title.string
    author = author.strip()
    collectiontitle = biggsSOUP.center.contents[0].strip()
    date = '1405-1464'

    title = []
    for link in biggsSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'neo.html' and link.get(
                'href') != 'classics.html'):
            title.append(link.string)

    i = 0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Piccolomini'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i = i + 1


if __name__ == '__main__':
    main()
