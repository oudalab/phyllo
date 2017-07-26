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

def parseRes2(soup, title, url, cur, author, date, collectiontitle):
    chapter = 0
    getp = soup.find_all('p')[:-1]
    i = len(getp)
    num = 0
    verse = 0
    if url == 'http://www.thelatinlibrary.com/boethiusdacia/deaeternitate.html':
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            passage = ''
            text = p.get_text().strip()
            # Skip empty paragraphs. and skip the last part with the collection link.
            if len(text) <= 0 or text.startswith('Medieval Latin\n'):
                continue
            text = re.split('^\[([0-9]+)\.\]\s', text)
            for element in text:
                if element is None or element == '' or element.isspace():
                    text.remove(element)
            # The split should not alter sections with no prefixed roman numeral.
            if len(text) > 1:
                i = 0
                while text[i] is None:
                    i += 1
                chapter = text[i]
                i += 1
                while text[i] is None:
                    i += 1
                passage = text[i].strip()
                verse = 1
            else:
                passage = text[0]
                verse += 1
            # check for that last line with the author name that doesn't need to be here
            if passage.startswith('Medieval Latin'):
                continue
            cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, collectiontitle, title, 'Latin', author, date, chapter,
                       verse, passage.strip(), url, 'prose'))

    else:
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            chapter += 1
            num = 0
            sen = p.text
            sen = sen.strip()
            for s in sent_tokenize(sen):
                num += 1
                sentn = s.strip()
                cur.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                            (None, collectiontitle, title, 'Latin', author, date, chapter,
                             num, sentn, url, 'prose'))



def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    anselmURL = 'http://www.thelatinlibrary.com/boethiusdacia.html'
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
        textsURL.remove("http://www.thelatinlibrary.com/medieval.html")
    logger.info("\n".join(textsURL))

    author = anselmSOUP.title.string
    author = author.strip()
    collectiontitle = 'BOETHIUS OF DACIA'
    date = anselmSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

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
        c.execute("DELETE FROM texts WHERE author = 'Boethius of Dacia'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            parseRes2(gestSoup, title[i], u, c, author, date, collectiontitle)
            i=i+1


if __name__ == '__main__':
    main()
