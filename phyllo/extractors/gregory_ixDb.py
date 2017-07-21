import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger



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
    collURL = 'http://www.thelatinlibrary.com/gregory.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = collSOUP.find('p').string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()

        c.execute("DELETE FROM texts WHERE author = 'Gregory IX'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()

            if url == "http://www.thelatinlibrary.com/gregdecretals5.html":
                title = "Decretals V"  # fix a typo

            chapter = "preface"
            verse = 0
            titulus = "" # used to store part of the chapter name
            caput = ''  # also used to store part of chapter name
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

                if p.find('b') is not None:
                    if text.startswith("LIBER"):
                        continue
                    elif text.startswith("TITULUS"):
                        titulus = text
                        continue
                    else:
                        caput = p.find('b').string.strip()
                        text = text.replace(caput, '')

                elif text.startswith("CAP"):
                    if title.endswith(" V"):
                        caput = text.split(" ")[0] + " " + text.split(" ")[1]
                        text = text.replace(caput, '')
                        chapter = titulus + ": " + caput
                        print(chapter)
                        verse = 0

                    else:
                        caput = text
                        chapter = titulus + ": " + caput
                        print(chapter)
                        verse = 0
                        continue

                verses.append(text)

                for v in verses:
                    if v.startswith('Christian Latin'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    verse += 1
                    # verse number assignment.
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
