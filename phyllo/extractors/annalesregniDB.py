import sqlite3
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString

import nltk

nltk.download('punkt')

from nltk import sent_tokenize

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = "-"
    sen = ""
    num = 1
    [e.extract() for e in soup.find_all('br')]
    [e.extract() for e in soup.find_all('table')]
    getp = soup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        sen = p.text
        sen = sen.strip()
        sen1 = ''.join([i for i in sen if not i.isdigit()])
        if sen.startswith("["):
            chapter = sen[1]+sen[2]+sen[3]
            if sen[1] == '*':
                chapter += sen[4]
            num = 1
        else:
            num +=1

        sen1 = sen1.replace('[*]', '')
        sen1 = sen1.replace('[]', '')
        sen1 = sen1.strip()
        sentn = sen1

        if sentn == '':
            continue
        cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                        (None, collectiontitle, title, 'Latin', author, date, chapter,
                         num, sentn, url, 'prose'))



def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/annalesregnifrancorum.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'ANNALES LAURISSENSES MAIORES'

    author = 'Annesl Regni Francorum'
    author = author.strip()
    collectiontitle = 'ANNALES LAURISSENSES MAIORES'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Annesl Regni Francorum'")
        parseRes2(biggsSOUP, title, biggsURL, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
