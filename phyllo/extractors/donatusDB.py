import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# Alternate Case 2: Sections are split by capital letters and subsections by <p> tags
def altparsecase2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 0
    # entry deletion is done in main()
    for p in ptags:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        passage = ''
        text = p.get_text().strip()
        if text.startswith("The Miscellany"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # chapters are in caps and on their own paragraph.
        if text.isupper():
            chapter = text
            verse = 0
            continue
        passage = text
        verse += 1
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


# main code
def main():
    # The collection URL below and other information from the author's main page
    collURL = 'http://www.thelatinlibrary.com/don.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(':')[0].strip()
    colltitle = 'DE PARTIBUS ORATIONIS ARS MINOR AELII DONATI'
    date = '-'
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Donatus'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            altparsecase2(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
