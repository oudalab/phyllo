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
    collURL = 'http://www.thelatinlibrary.com/kempis.html'
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

        c.execute("DELETE FROM texts WHERE author = 'Thomas à Kempis'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = "placeholder"  # we set the title later
            verses = []
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

                text = p.get_text()
                text = text.strip()

                if text.startswith("Liber"):
                    title = text
                    print(title)
                    continue
                elif text.startswith("De devota exhortatione"):
                    title = "Liber Quartus: " + text
                    print(title)
                    d = textsoup.find("div")
                    verses.append(d.contents[0].string.strip())
                    continue

                if p.find('b') is not None:
                    chapter = text
                    print(chapter)
                    verse = 0
                    continue

                if re.match('[0-9]+\.',text):
                    removetext = text.split(" ")[0]
                    text = text.replace(removetext, '')

                verses.append(text)

                for v in verses:
                    if v is None or v == '' or v.isspace():
                        continue
                    if v.startswith('Thomas à Kempis'):
                        continue
                    verse += 1
                    # verse number assignment.
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))
                verses = []

if __name__ == '__main__':
    main()
