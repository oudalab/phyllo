import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


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
        textsURL.remove("http://www.thelatinlibrary.com/christian.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/hydatius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = collSOUP.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Hydatius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()
            print(title)
            chapter = -1
            verse = 0

            # this just numbers paragraphs as verses
            # does not split chapters b/c I wasn't sure how to split them
            if title.startswith("Chronicon"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []


                    text = p.get_text()
                    text = text.strip()
                    verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            # leaves internal numbers as part of text and numbers each line
            # poetry or prose?

            else:
                chapter = "-1"
                verse = 0
                getp = textsoup.find_all('p')

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    txtstr = p.get_text().strip()
                    if txtstr.startswith("Christian"):
                        continue

                    brtags = p.findAll('br')
                    verses = []
                    try:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.strip()
                    verses.append(firstline)

                    for br in brtags:
                        try:
                            text = br.next_sibling.next_sibling.strip()
                        except:
                            text = br.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        verses.append(text)

                    for v in verses:
                        if v.startswith('Christian'):
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
