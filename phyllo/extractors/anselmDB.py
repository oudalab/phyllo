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

anselmSOUP=""
idx = -1
cha_array=[]
suburl = []
verse = []

def parseRes2(soup, title, url, c, author, date, collectiontitle):
    chapter = '-'
    if url=="http://www.thelatinlibrary.com/anselmepistula.html":
        getp = soup.find_all('p')[:-1]
        i=len(getp)
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            num = len(getp) - (i - 1)
            if p.findAll('br'):
                sentn=p.get_text()
                num=1
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                i=0

            else:
                i=i+1
                ptext = p.string
                chapter = str(i)  # App. not associated with any chapter
                # the first element is an empty string.
                ptext = ptext[3:]
                num=0
                for sentn in sent_tokenize(ptext):
                    num=num+1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
    else:
        getp = soup.find_all('p')[:-1]
        geturl=soup.find_all('a', href=True)
        global idx
        j = 0
        #print(getp)
        for u in geturl:
            if u.get('href') != 'index.html' and u.get('href') != 'classics.html' and u.get('href') != 'christian.html':
                suburl.append('http://www.thelatinlibrary.com/anselmproslogion.html'+u.get('href'))
        suburl[13]='http://www.thelatinlibrary.com/anselmproslogion.html#capxiii'
        suburl[23]='http://www.thelatinlibrary.com/anselmproslogion.html#capxxiii'
        suburl.insert(14, 'http://www.thelatinlibrary.com/anselmproslogion.html#capxiv')
        suburl.insert(24, 'http://www.thelatinlibrary.com/anselmproslogion.html#capxxiii')

        i = len(getp)


        for ch in soup.findAll('b'):
            chap = ch.string
            cha_array.append(''.join([i for i in chap if not i.isdigit()]))


        for p in getp:
            # make sure it's not a paragraph without the main text

            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin'
                                             'internal_navigation']:  # these are not part of the main text
                    continue
            except:
                pass
                if p.string == None:
                    idx = (idx + 1) % len(suburl)
                    chapter = cha_array[idx]
                    nurl = suburl[idx]


            if p.string:
                j=j+1
                num=j
                sentn = str(p.string)
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, collectiontitle, title, 'Latin', author, date, chapter,
                       num, sentn, nurl, 'prose'))




def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    anselmURL = 'http://www.thelatinlibrary.com/anselm.html'
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
        textsURL.remove("http://www.thelatinlibrary.com/christian.html")
    logger.info("\n".join(textsURL))

    author = anselmSOUP.title.string
    author = author.strip()
    collectiontitle = anselmSOUP.span.contents[0].strip()
    date = anselmSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    title = []
    for link in anselmSOUP.findAll('a'):
        if (link.get('href') and link.get('href') != 'index.html' and link.get('href') != 'classics.html' and link.get('href') != 'christian.html'):
            title.append(link.string)

    i=0

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Anselm'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
