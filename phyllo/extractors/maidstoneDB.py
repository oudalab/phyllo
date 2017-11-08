import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString


# Case 2: Sections are split by <p> tags and subsections by un/bracketed numbers.
def parsecase2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
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
        if text.startswith("Medieval"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        text = re.split('^([0-9]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)

        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric() or len(item) < 5:
                verse = item
            else:
                passage = item
                # assign chapter
                if passage.startswith('Prima causa fuit,'):
                    chapter = 'Hae fuerunt causae, quare decollatus est archiepiscopus Ricardus Scrope'
                    verse = 0
                if passage.startswith('Anno Domini MCCCCV.,'):
                    chapter = 'Hic incipit Martyrium praedicti Ricardi archiepiscopi'
                    verse = 0
                try:
                    verse += 1
                except:
                    pass
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), URL, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/maidstone.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = [biggsURL]

    author = 'Clement Maidstone'
    author = author.strip()
    collectiontitle = 'MARTYRIUM RICARDI ARCHIEPISCOPI'
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Clement Maidstone'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            parsecase2(getp, c, collectiontitle, title, author, date, url)


if __name__ == '__main__':
    main()
