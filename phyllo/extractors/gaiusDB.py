import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems to work fine


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
        try:
            textsURL.remove("http://thelatinlibrary.com/ius.html")
        except:
            pass
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/gaius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = 'GAI INSTITVTIONVM COMMENTARII QVATTVOR'
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()

        c.execute("DELETE FROM texts WHERE author = 'Gaius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0

            getp = textsoup.find_all('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main text
                        continue
                except:
                    pass

                verses = []

                pstring = p.get_text()
                pstring = pstring.strip()

                if re.match("\[[IVXL]+", pstring):
                    # get chapters if applicable
                    chapter = pstring.split("]")[0].replace('[', '').strip()
                    pstring = pstring.replace(chapter, '').strip()

                lines = re.split('([0-9]+\.) | ([0-9]+[ab]\.)', pstring)
                for l in lines:

                    if l is None or l == '' or l.isspace():
                        continue
                    l = l.strip()
                    print(l)
                    if l[0].isdigit():
                        print("FOUND A VERSE")
                        verse = l
                        continue
                    if l.startswith('Gaius'):
                        continue
                    if l.startswith('[]'):
                        continue
                    # we put values in the DB here to b/c it is necessary to preserve verse numbering
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, l.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
