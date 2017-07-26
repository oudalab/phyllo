import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
# verses are split by sentences


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/ampelius.shtml'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = 'LUCIUS AMPELIUS'
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Ampelius'")

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
                    chapter = chapter_f.string.strip()
                    verse = 0
                    continue
                text = p.get_text().strip()
                # using negative lookbehind assertion to not match with abbreviations of one or two letters and ellipses.
                # ellipses are not entirely captured, but now it doesn't leave empty cells in the database.
                text = re.split('\[([0-9]+)\]|(?<!\s[A-Z]|[A-Z][a-z])\.\s(?!\.\s)', text)
                for v in text:
                    if v is None:
                        continue # skip empty elements
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, re.sub(r'[[\]<>]', '', chapter),
                                   verse, v, url, 'prose'))


if __name__ == '__main__':
    main()
