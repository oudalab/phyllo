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
    collURL = 'http://www.thelatinlibrary.com/cassiodorus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "FLAVIVS MAGNVS AVRELIVS CASSIODORVS"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Cassiodorus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            if url.startswith("http://www.thelatinlibrary.com/cassiodorus/epist.shtml"):
                title = "EPISTULAE THEODERICIANAE VARIAE."
            else:
                title = textsoup.title.string.split(':')[1].strip()
            print(title)

            if title.startswith("Variae") or title.startswith('EPISTULAE'):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        if pstring.startswith("LIBER"):
                            continue
                        else:
                            chapter = pstring
                            verse = 0
                            print(chapter)
                            continue


                    lines = re.split('\[[0-9]+\]', pstring)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith('Christian'):
                            continue
                        verses.append(l)

                    for v in verses:
                        if v.startswith('Cassiodorus'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))

            elif title.startswith("Orationes"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if len(pstring) < 10:
                        # this is a chapter heading
                        chapter = pstring
                        verse = 0
                        continue

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Cassiodorus'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("de Anima"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        chapter = pstring
                        verse = 0
                        print(chapter)
                        continue

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Cassiodorus'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


            elif title.startswith("de Trinitate"):
                getp = textsoup.find_all('p')
                chapter = "PROLOGUS"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        continue
                        # these headings are handled elsewhere

                    if re.match("\[", pstring):
                        # this is a heading
                        heading = pstring.split("]")[0].replace("[", "").strip()
                        if re.match("[IVXL]+", heading):
                            # this is a chapter and verse heading
                            try:
                                chapter = re.split(" ", heading)[0].strip()
                                verse = re.split(" ", heading)[1].strip()
                            except:
                                verse = heading
                        else:
                            verse = heading

                        pstring = pstring.split("]")[1].strip()

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                getp = textsoup.find_all('p')
                chapter = "PRAEFATIO"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        chapter = pstring
                        verse = 0
                        print(chapter)
                        continue

                    lines = re.split('[0-9]+\.', pstring)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith('Cassiodorus'):
                            continue
                        verses.append(l)

                    for v in verses:
                        if v.startswith('Cassiodorus'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
