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
        textsURL.remove("http://www.thelatinlibrary.com/misc.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/columella.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "LUCIUS IUNIUS MODERATUS COLUMELLA"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Columella'")

        for url in textsURL:
            chapter = -1
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            if title.endswith("Arboribus"):
                chapter = '-1'
                verse = 1

                for p in getp:
                    # make sure it's not a paragraph without the main text
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    # find chapter
                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.get_text().strip()
                        if chapter.endswith("."):
                            chapter.replace(".", "")
                        verse = 0
                        continue

                    else:
                        text = p.get_text().strip()

                    # Skip empty paragraphs.
                        if len(text) <= 0:
                            continue
                        text = re.split('([IVX]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
                        for element in text:
                            if element is None or element == '' or element.isspace():
                                text.remove(element)

                        for count, item in enumerate(text):
                            if item is None:
                                continue
                            if item.startswith("Columella"):
                                continue
                            if item.isnumeric() or len(item) < 5:
                                verse = item
                            else:
                                passage = item
                                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                    (None, colltitle, title, 'Latin', author, date, chapter,
                                    verse, passage.strip(), url, 'prose'))
            else:
                for p in getp:
                # make sure it's not a paragraph without the main text
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                # find chapter
                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.get_text().strip()
                        if chapter.endswith("."):
                            chapter.replace(".", "")
                        verse = 0


                    text = p.get_text().strip()
                    # using negative lookbehind assertion to not match with abbreviations of one or two letters and ellipses.
                    # ellipses are not entirely captured, but now it doesn't leave empty cells in the database
                    try:
                        verses = re.split('\[([0-9]+)\]|(?<!\s[A-Z]|[A-Z][a-z])\.\s(?!\.\s)', text)
                    except:
                        continue
                    for v in verses:

                        if v is None or v == '' or v.isspace(): # get rid of empty strings
                            continue
                        if len(v) < 5:
                            continue # make sure chapter numbers don't get their own database entry
                        else: # verse number assignment.
                            v.strip()
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter.replace(".", ""),
                               verse, v, url, 'prose'))


if __name__ == '__main__':
    main()
