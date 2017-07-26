import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

#

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
    collURL = 'http://www.thelatinlibrary.com/papal.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = 'no date found'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        c.execute("DELETE FROM texts WHERE title = 'Solet annuere'")
        c.execute("DELETE FROM texts WHERE title = 'Exivi de paradiso'")
        c.execute("DELETE FROM texts WHERE title = 'Inter Gravissimas'")
        c.execute("DELETE FROM texts WHERE title = 'Quum inter nonnullos'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0

            # some questions about what exactly is a chapter - rn this just uses bold paragraphs
            if title.startswith("Solet"):
                date = 'Nov. 29 1223 A.D.'
                chapter = "Preface"
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
                    verses = []

                    if p.find('b') is not None:
                        chapter = text
                        verse = 0
                        print(chapter)
                        continue

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Papal'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Exivi"):
                date = 'no date found'
                chapter = 0
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

                    if re.match('[0-9]+\.', text):
                        chapter += 1
                        text = text.replace(str(chapter) + ".", '')
                        verse = 0
                        print(chapter)

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Papal'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            # a few discrepancies b/n in-text and paragraph numbers

            elif title.startswith("Inter"):
                date = 'no date found'
                chapter = "-1"
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
                    verses = []

                    if p.find('b') is not None:
                        chapter = text
                        verse = 0
                        print(chapter)
                        continue

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Papal'):
                            continue
                        if v.startswith('From the'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


            # doesn't catch the first paragraph because it is centered
            else:
                verse = 0
                date = '1323'
                chapter = 0
                verses = []
                getp = textsoup.find_all('p')
                centers = textsoup.find_all("center")
                for cen in centers:
                    try:
                        if cen.contents[0].startswith("Opinio"):
                            verses.append(cen.contents[0])
                        else:
                            pass
                    except:
                        pass
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass
                    text = p.string.strip()

                    if re.match('[0-9]+\.', text):
                        chapter += 1
                        text = text.replace(str(chapter) + '.', '')
                        verse = 0
                        print(chapter)

                    verses.append(text)

                    for v in verses:
                        if v is None or v == '' or v.isspace():
                            continue
                        if v.startswith('Papal'):
                            continue
                        verse += 1

                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

                    verses = []

if __name__ == '__main__':
    main()
