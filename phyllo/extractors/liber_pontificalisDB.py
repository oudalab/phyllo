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
    while ("http://www.thelatinlibrary.com//index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com//index.html")
        textsURL.remove("http://www.thelatinlibrary.com//classics.html")
        textsURL.remove("http://www.thelatinlibrary.com//christian")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/liberpontificalis.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = 'no date found'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()

        c.execute("DELETE FROM texts WHERE title = 'Liber Pontificalis'")
        c.execute("DELETE FROM texts WHERE title = 'Catalogue Libérien'")
        c.execute("DELETE FROM texts WHERE title = 'Fragmentum Laurentianum'")
        c.execute("DELETE FROM texts WHERE title = 'Epitome Feliciana'")
        c.execute("DELETE FROM texts WHERE title = 'Epitome Cononiana'")


        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0

            # some questions about how to handle footnotes and out of order verses
            if title.startswith("Liber"):
                date = textsoup.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
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

                    verses = re.split("([0-9]+\s)", text)

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        if len(v) < 10:
                            continue
                            # this is a stray punctuation mark or something
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Catalogue"):
                date = textsoup.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
                chapter = "-1"
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

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Fragmentum"):
                chapter = "-1"
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []
                    brtags = p.findAll('br')
                    if brtags != []:
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
                    else:
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                chapter = "Preface"
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []
                    brtags = p.findAll('br')

                    text = p.get_text()
                    text = text.strip()

                    if brtags != []:
                        try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.strip()
                        verses.append(firstline)

                        for br in brtags:
                            try:
                                t = br.next_sibling.next_sibling.strip()
                            except:
                                t = br.next_sibling.strip()
                            if t is None or t == '' or t.isspace():
                                continue
                            verses.append(t)
                    elif re.match("[IVXL]+\.", text):
                        # this is a chapter heading
                        chapter = text.split(",")[0]
                        text = text.replace(chapter + ",", '')
                        verses.append(text)
                        verse = 0
                        print(chapter)
                    else:
                        verses.append(text)

                    for v in verses:
                        if v.startswith('Christian'):
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
