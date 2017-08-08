import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# Problems:
# mommsen 2nd ed. : verse assignment issues b/c some verses are split across paragraphs

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
    collURL = 'http://thelatinlibrary.com/solinus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "GAIUS JULIUS SOLINUS"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Solinus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            # assigning titles based on URLs because the edition info is only on the collection page
            if url.strip().endswith('5.html'):
                title = "DE MIRABILIBUS MUNDI: Mommsen 2nd edition (1895)"
            elif url.strip().endswith("a.html"):
                title = "DE MIRABILIBUS MUNDI: Mommsen 1st edition (1864)"
            else:
                title = "DE MIRABILIBUS MUNDI: C.L.F. Panckoucke edition (Paris 1847)"
            logger.info(title)  # see what is screwed up when it inevitably is

            if title.startswith("DE MIRABILIBUS MUNDI: Mommsen 2nd edition (1895)"):

                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                textstr = ''
                verses = []
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        # we found the beginning of a new chapter!
                        # we'll process the previous chapter now.
                        lines = re.split("[0-9]+", textstr)
                        for l in lines:
                            if l is None or l == '' or l.isspace():
                                continue
                            if l.startswith("The Miscellany"):
                                continue
                            verses.append(l)

                        for v in verses:
                            if v.startswith('The Miscellany'):
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))
                        textstr = ''
                        verses = []
                        # now we get the new chapter
                        try:
                            chapter = chapter_f.string.strip()
                            verse = 0
                            try:
                                try:
                                    text = chapter_f.next_sibling.next_sibling.strip()
                                except:
                                    text = chapter_f.next_sibling.strip()
                            except:
                                pass
                        except:
                            pass
                        textstr = textstr + " " + text
                    elif p.find('a') is not None:
                        # we have reached the end!
                        # we'll process the last chapter now.
                        lines = re.split("[0-9]+", textstr)
                        for l in lines:
                            if l is None or l == '' or l.isspace():
                                continue
                            if l.startswith("The Miscellany"):
                                continue
                            verses.append(l)

                        for v in verses:
                            if v.startswith('The Miscellany'):
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))
                    else:
                        text = p.get_text()
                        text = text.strip()
                        textstr = textstr + " " + text


            elif(title.startswith("DE MIRABILIBUS MUNDI: Mommsen 1st edition (1864)")):

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
                            try:
                                text = chapter_f.next_sibling.next_sibling.strip()
                            except:
                                text = chapter_f.next_sibling.strip()
                        except:
                            pass

                    else:
                        text = p.get_text()
                        text = text.strip()
                    verses.append(text)

                    for v in verses:
                        if v.startswith('The Miscellany'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

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
                        try:
                            chapter = chapter_f.string.strip()
                            print(chapter)
                            verse = 0
                            continue
                        except:
                            pass

                    else:
                        text = p.get_text()
                        text = text.strip()

                    lines = re.split("[0-9]+", text)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith("The Miscellany"):
                            continue
                        verses.append(l)

                    for v in verses:
                        if v.startswith('The Miscellany'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))
if __name__ == '__main__':
    main()
