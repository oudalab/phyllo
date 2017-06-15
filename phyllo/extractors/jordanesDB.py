import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# this works!!! yay!

def getBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/misc.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/iordanes.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Iordanes'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.split('Iordanis')[1].strip()
            chapter = -1
            verse = 0

            if title.startswith("de Origine"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    spantags = p.findAll('span')
                    verses = []
                    try:
                        try:
                            chapter = spantags[0].previous_sibling.strip()
                        except:
                            chapter = spantags[0].previous_sibling.previous_sibling.strip()
                    except:
                        pass
                    for s in spantags:
                        try:
                            text = s.next_sibling.strip()
                        except:
                            text = s.next_sibling.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue

                        verses.append(text)

                    for v in verses:
                        if v.startswith('The'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                # this skips chapter 315 for reasons not apparent to me
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    chaptags = p.findAll('b')
                    for ch in chaptags:
                        chapter = ch.string.strip()
                        verses = []
                        if p.find('br') is not None:
                            brtags = p.findAll('br')
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

                        else:
                            try:
                                text = ch.next_sibling.strip()
                            except:
                                text = ch.next_sibling.next_sibling.strip()
                            verses.append(text)

                        for v in verses:
                            if v.startswith('The Miscellany'):
                                continue
                            if v is None or v == '' or v.isspace():
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
