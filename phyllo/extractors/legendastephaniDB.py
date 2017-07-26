import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString


def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 1

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
        # Skip empty paragraphs. and skip the last part with the collection link.
        if len(text) <= 0 or text.startswith('Medieval\n'):
            continue
        text = re.split('^([0-9]+)\.\s|^([0-9]+)\.\.', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        # The split should not alter sections with no prefixed roman numeral.
        if len(text) > 1:
            i = 0
            while text[i] is None:
                i+=1
            chapter = text[i]
            i+=1
            while text[i] is None:
                i+=1
            passage = text[i].strip()
            verse = 1
        else:
            passage = text[0]
            verse+=1
        # check for that last line with the author name that doesn't need to be here
        if passage.startswith('Medieval'):
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    biggsURL = 'http://www.thelatinlibrary.com/legenda.stephani.html'
    biggsOPEN = urllib.request.urlopen(biggsURL)
    biggsSOUP = BeautifulSoup(biggsOPEN, 'html5lib')
    textsURL = []

    title = 'Legenda Maior Sancti Regis Stephani'

    author = 'Legenda Regis Stephani'
    author = author.strip()
    collectiontitle = 'LEGENDA MAIOR SANCTI REGIS STEPHANI'
    collectiontitle = collectiontitle.strip()
    date = '-'

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Legenda Regis Stephani'")
        parsecase1(biggsSOUP.find_all('p'), c, collectiontitle, title, author, date, biggsURL)


if __name__ == '__main__':
    main()
