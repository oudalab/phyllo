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

def parsePoem(soup, title, url, cur, author, date, collectiontitle):
    chapter = -1
    verse = 0
    openurl = urllib.request.urlopen(url)
    textsoup = BeautifulSoup(openurl, 'html5lib')

    try:
        title = textsoup.title.string.split(':')[1].strip()
    except:
        title = textsoup.title.string.strip()

    if title.startswith("Preface"):
        type = "prose"
    else:
        type = "poetry"
    getp = textsoup.find_all('p')

    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        # find chapter
        chapter_f = p.find('b')
        if chapter_f is not None:
            chapter = p.get_text().strip()
            verse = 0
            continue
        else:
            brtags = p.findAll('br')
            verses = []
            try:
                try:
                    firstline = brtags[0].previous_sibling.strip()
                except:
                    firstline = brtags[0].previous_sibling.previous_sibling.strip()
                verses.append(firstline)
            except:
                pass
            for br in brtags:
                try:
                    text = br.next_sibling.next_sibling.strip()
                except:
                    text = br.next_sibling.strip()
                if text is None or text == '' or text.isspace():
                    continue
                verses.append(text)
        for v in verses:
            # verse number assignment.
            verse += 1
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         verse, v, url, type))

def altParsePoem(soup, title, url, cur, author, date, collectiontitle, jrange):
    chapter = -1
    j = 1
    sen = ""
    b = []
    i = 1

    for a in soup.findAll('dd'):
        b.append(a.text)
    c = 0
    for j, s in enumerate(b):
        b[j] = s.replace('\xa0', '')
    for j in range(1, jrange):
        b.insert(9 + c, "9999")
        c = 10 + c + 1

    for s in b:
        if s == "9999":
            sentn = sen
            sentext = re.split('\n', sentn)
            sentext = filter(lambda x: len(x) > 3, sentext)
            for line in sentext:
                num = i
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, line, url, 'prose'))
                i = i + 1
            sen = ""
        else:
            sen = sen + s


def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = '-'
    sen=""
    i=1
    sentenc=[]
    getp = soup.findAll('p')
    if url == 'http://www.thelatinlibrary.com/addison/preface.shtml':
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            if p.text == None:
                s=""
            else:
                sen=sen+str(p.string)
        sen.strip()
        sentenc=sen.split('\n\n')
        while '' in sentenc:
            sentenc.remove('')
        for ss in sentenc:
            num = i
            sentn =ss
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, collectiontitle, title, 'Latin', author, date, chapter,
                       num, sentn, url, 'prose'))
            i=i+1
    if url == 'http://www.thelatinlibrary.com/addison/pax.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 20)
    if url=='http://www.thelatinlibrary.com/addison/barometri.shtml':
        parsePoem(soup, title, url, cur, author, date, collectiontitle)
    if url == 'http://www.thelatinlibrary.com/addison/praelium.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 17)
    if url == 'http://www.thelatinlibrary.com/addison/resurr.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 13)
    if url == 'http://www.thelatinlibrary.com/addison/sphaer.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 8)
    if url == 'http://www.thelatinlibrary.com/addison/hannes.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 6)
    if url == 'http://www.thelatinlibrary.com/addison/sphaer.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 8)
    if url == 'http://www.thelatinlibrary.com/addison/machinae.shtml':
        altParsePoem(soup, title, url, cur, author, date, collectiontitle, 10)
    if url=='http://www.thelatinlibrary.com/addison/burnett.shtml':
        parsePoem(soup, title, url, cur, author, date, collectiontitle)


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    anselmURL = 'http://www.thelatinlibrary.com/addison.html'
    anselmOPEN = urllib.request.urlopen(anselmURL)
    anselmSOUP = BeautifulSoup(anselmOPEN, 'html5lib')
    textsURL = []
    ctitle=[]
    j=0

    for a in anselmSOUP.findAll('a'):
        if a.get('href'):
            if a.get('href') != 'index.html' and a.get('href') != 'classics.html' and a.get('href') != 'neo' and a.get('href') != 'http://eee.uci.edu/~papyri/Addison':
                link = a.get('href')
                textsURL.append("{}/{}".format(siteURL, link))


    # remove some unnecessary urls
    logger.info("\n".join(textsURL))

    author = anselmSOUP.title.string
    author = author.strip()
    collectiontitle = anselmSOUP.center.contents[0].strip()
    date=1667

    title = []
    for link in anselmSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'classics.html' and link.get('href') != 'christian.html'):
            title.append(link.string)

    i=0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Joseph Addison'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
