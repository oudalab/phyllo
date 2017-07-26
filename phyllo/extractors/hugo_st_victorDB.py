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
    collURL = 'http://www.thelatinlibrary.com/hugo.html'
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
        c.execute("DELETE FROM texts WHERE author = 'Hugo of St. Victor'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(":")[1].strip()
            except:
                title = "SOLILOQUIUM DE ARRHA ANIMAE"
            print(title)
            chapter = -1
            verse = 0


            if title.startswith("SOLILOQUIUM"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []

                    chapter_f = p.find('i')
                    text = p.get_text()
                    text = text.strip()

                    if chapter_f is not None or text.startswith("Confessio"):
                        chapter = text
                        print(chapter)
                        verse = 0
                        continue
                    else:
                        verses.append(text.strip())


                    for v in verses:
                        if v.startswith('Hugo of'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            # does things a bit differently to handle verses split across paragraphs

            else:
                chapter = "Praefatio"
                verse = 0
                getp = textsoup.find_all('p')
                textstr = ''
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass



                    text = p.get_text()
                    text = text.strip()

                    if chapter == "APPENDIX":
                        # the appendix has different verse numbering
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, text.strip(), url, 'prose'))

                    if text.startswith("LIBER") or text.startswith("DE STUDIO LEGENDI"):
                        # book numbers, which are dealt with elsewhere
                        continue

                    elif text.startswith("CAPUT"):
                        # this is a chapter heading. We will now process the previous chapter.

                        verses = re.split('(\[[0-9]+[ABCD]\])', textstr)
                        for v in verses:
                            if v.startswith('Hugo of'):
                                continue
                            if v.startswith('Praefatio'):
                                continue
                            if v is None or v == '' or v.isspace():
                                continue

                            # verse number assignment.
                            if len(v) < 10:
                                # this is a verse number
                                verse = v
                                print(verse)
                                continue
                            if verse == 0:
                                continue
                                
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))
                        textstr = ''
                        chapter = text
                        print(chapter)
                        verses = []
                        continue

                    elif text.startswith("APPENDIX"):
                        chapter = text
                        verse = 0
                        continue
                    else:
                        textstr = textstr + " " + p.get_text()

if __name__ == '__main__':
    main()
