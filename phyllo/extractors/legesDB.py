import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems to work fine
# should probably check on chapter divisions

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
    collURL = 'http://thelatinlibrary.com/leges.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "various authors"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        c.execute("DELETE FROM texts WHERE title = 'DUODECIM TABULARUM LEGES'")
        c.execute("DELETE FROM texts WHERE title = 'SENATUS CONSULTUM DE BACCHANALIBUS'")
        c.execute("DELETE FROM texts WHERE title = 'EDICTUM ADVERSUS LATINOS RHETORES'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0


            if title.startswith("DUODECIM"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        verse = 0
                        continue
                    elif p.find('br') is not None:
                        # this is the chapter list.

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
                        pstring = p.get_text()
                        verses.append(pstring.strip())


                    for v in verses:
                        if v.startswith('Ius Romanum'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            # does things a bit differently to handle verses split across paragraphs

            elif title.startswith("SENATUS CONSULTUM DE BACCHANALIBUS"):
                chapter = 0
                verse = 0
                getp = textsoup.find_all('p')
                textstr = ''
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'shortborder', 'smallborder']:
                            # reset chapter and verse at the border
                            verses = re.split('\([0-9]+\)', textstr)
                            for v in verses:
                                if v.startswith('Ius Romanum'):
                                    continue
                                if v is None or v == '' or v.isspace():
                                    continue
                                # verse number assignment.
                                verse += 1
                                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                          (None, colltitle, title, 'Latin', author, date, chapter,
                                           verse, v.strip(), url, 'prose'))
                            textstr = ''
                            chapter += 1
                            verse = 0
                            verses = []
                            continue
                        elif p['class'][0].lower() in [ 'pagehead', 'margin', 'internal_navigation']:
                            continue
                    except:
                        pass

                    textstr = textstr + " " + p.get_text()
            elif title.startswith("EDICTUM ADVERSUS LATINOS RHETORES"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        verse = 0
                        continue
                    else:
                        pstring = p.get_text()
                        verses.append(pstring.strip())

                    for v in verses:
                        if v.startswith('The Latin Library'):
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
