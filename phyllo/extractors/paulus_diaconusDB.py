import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# works as intended

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
    collURL = 'http://thelatinlibrary.com/pauldeacon.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "PAULUS DIACONUS"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Paul the Deacon'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            print(title)

            if title.startswith("Historia Langobardorum"):

                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []
                    textstr = p.get_text()
                    textstr = textstr.strip()

                    if textstr[0].isdigit():
                        chapter = textstr.split(".")[0]
                        verse = 0

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
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Paul Diaconus'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            # i divided this pretty simply -- possibly needs to be improved
            elif(title.startswith("Historia Romana")):

                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        verse = 0

                        try:
                            text = chapter_f.next_sibling.next_sibling.strip()
                        except:
                            text = chapter_f.next_sibling.strip()
                            verses.append(text)
                    else:
                        text = p.get_text()
                        text = text.strip()
                        # there's a typo such that Liber V is listed as Liber II. We'll fix that here.
                        if text == "INCIPIT LIBER QVINTVS":
                            title = "Historia Romana Liber V"
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Paul Diaconus'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif (title.startswith("Carmina")):
                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []
                    if p.find('b') is not None and p.find('br') is None:
                        # this is a chapter name
                        chapter = p.get_text()
                        chapter = chapter.strip()
                        verse = 0
                        continue
                    if chapter.startswith("Hymnus"):
                        # there's some weird <b> tags in here, so our usual poetry scraper won't work
                        textstr = p.get_text()
                        textstr = textstr.strip()
                        lines = re.split("\n", textstr)
                        for l in lines:
                            if l is None or l == '' or l.isspace():
                                continue
                            if l.endswith(r'[0-9]+'):
                                try:
                                    l = l.split(r'[0-9]')[0].strip()
                                except:
                                    pass
                            if len(l.strip()) < 5:
                                if not l.endswith("."):
                                    continue  # skip line numbers
                                else:
                                    pass
                            verses.append(l)
                    else:
                        brtags = p.findAll('br')
                        if brtags == []:
                            continue
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
                            # remove in-text line numbers
                            if text.endswith(r'[0-9]+'):
                                try:
                                    text = text.split(r'[0-9]')[0].strip()
                                except:
                                    pass
                            verses.append(text)
                    for v in verses:
                        if v.startswith('Paul Diaconus'):
                            continue
                        if len(v) < 5:
                            if not v.endswith("."):
                                continue  # skip line numbers
                            else:
                                pass  # skip line numbers and stuff
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))

            else:
                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        verse = 0
                        continue

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
                    elif p.find('a') is not None:
                        continue
                    else:
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Paul Diaconus'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'poetry'))

if __name__ == '__main__':
    main()
