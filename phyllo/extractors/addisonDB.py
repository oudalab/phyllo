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
        j=1
        sen=""
        b=[]
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c=0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1,20):
            b.insert(9+c, "9999")
            c=10+c+1

        for s in b:
            if s == "9999":
                num = i
                sentn=sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen=""
                i = i + 1
            else:
                sen=sen+s
    if url=='http://www.thelatinlibrary.com/addison/barometri.shtml':
        j=1
        s=''
        sen=''
        i=1
        [e.extract() for e in soup.find_all('br')]
        [e.extract() for e in soup.find_all('font')]
        for p in soup.findAll('p'):
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            s=s+p.get_text()

        s1=s.split('\n')
        while '' in s1:
            s1.remove('')
        c=0
        for j, s in enumerate(s1):
            s1[j] = s.replace('\xa0', '')
        for j in range(1,8):
            s1.insert(10+c, "9999")
            c=10+c+1

        for s in s1:
            if s == "9999":
                num = i
                sentn=sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen=""
                i = i + 1
            else:
                sen=sen+s+'\n'
    if url == 'http://www.thelatinlibrary.com/addison/praelium.shtml':
        j = 1
        sen = ""
        b = []
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c = 0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 17):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s
    if url == 'http://www.thelatinlibrary.com/addison/resurr.shtml':
        j = 1
        sen = ""
        b = []
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c = 0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 13):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s
    if url == 'http://www.thelatinlibrary.com/addison/sphaer.shtml':
        j = 1
        sen = ""
        b = []
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c = 0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 8):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s
    if url == 'http://www.thelatinlibrary.com/addison/hannes.shtml':
        j = 1
        sen = ""
        b = []
        i=1
        title='D. D. HANNES, INSIGNISSIMUM MEDICUM ET POETAM'

        for a in soup.findAll('dd'):
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            b.append(a.text)
        c = 0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 6):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s
    if url == 'http://www.thelatinlibrary.com/addison/sphaer.shtml':
        j = 1
        sen = ""
        b = []
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c = 0
        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 8):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s
    if url == 'http://www.thelatinlibrary.com/addison/machinae.shtml':
        j = 1
        sen = ""
        b = []
        i=1

        for a in soup.findAll('dd'):
            b.append(a.text)
        c = 0

        for j, s in enumerate(b):
            b[j] = s.replace('\xa0', '')
        for j in range(1, 10):
            b.insert(9 + c, "9999")
            c = 10 + c + 1

        for s in b:
            if s == "9999":
                num = i
                sentn = sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen = ""
                i = i + 1
            else:
                sen = sen + s

    if url=='http://www.thelatinlibrary.com/addison/burnett.shtml':
        j=1
        s=''
        sen=''
        i=1
        title='AD INSIGNISSIMUM VIRUM D. THO. BURNETTUM, SACRAE THEORIAE TELLURIS AUTOREM'
        [e.extract() for e in soup.find_all('br')]
        [e.extract() for e in soup.find_all('font')]
        for p in soup.findAll('p'):
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            s=s+p.get_text()

        s1=s.split('\n')
        while '' in s1:
            s1.remove('')
        c=0

        for j, s in enumerate(s1):
            s1[j] = s.replace('\xa0', '')
        for j in range(1,7):
            s1.insert(10+c, "9999")
            c=10+c+1

        for s in s1:
            if s == "9999":
                num = i
                sentn=sen
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
                sen=""
                i = i + 1
            else:
                sen=sen+s+'\n'



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
        c.execute("DELETE FROM texts WHERE author = 'Joseph Addison'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
