import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems ok!

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
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/justinian.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Justinian'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0

            if title.startswith("The Institutes of Justinian: Introduction"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

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

                    for v in verses:
                        if v.startswith('Ius Romanum'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

            elif title.startswith("The Institutes of Justinian,"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    if p.find('div') is not None or p.find('table') is not None:
                        continue

                    verses = []

                    if p.find('br') is not None:
                        chapter = p.get_text()
                        chapter = chapter.strip()
                        verse = 0
                        continue

                    else:
                        verses.append(p.get_text())

                    for v in verses:
                        if v.startswith('Ius Romanum'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

            elif title.startswith("Codex of Justinian"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    if p.find('br') is not None:
                        # these are chapter/verse lists
                        # probably redundant
                        continue
                    verses = []

                    pstring = p.get_text()
                    pstring = pstring.strip()


                    if pstring.startswith("CJ"):
                        # this is either a chapter or verse heading
                        if '0' in re.split('\.', pstring):
                            # this is a chapter heading
                            chapter = pstring
                            continue
                        else:
                            verse = pstring
                            continue

                    verses.append(pstring)
                    for v in verses:
                        if v.startswith('Ius Romanum'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

            elif title.startswith("Digest of Justinian"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    if p.find('br') is not None:
                        # these are chapter/verse lists
                        # probably redundant
                        continue
                    verses = []

                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if pstring.startswith("Dig."):
                        # this is either a chapter or verse heading
                        if '0' in re.split('\.', pstring):
                            # this is a chapter heading
                            chapter = pstring
                            continue
                        else:
                            verse = pstring
                            continue

                    verses.append(pstring)
                    for v in verses:
                        if v.startswith('Ius Romanum'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
