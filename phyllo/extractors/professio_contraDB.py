import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/professio.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = "PROFESSIO CONTRA SECTAM PRISCILLIANI"
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'Professio contra Sectam Priscilliani'")

        for url in textsURL:
            chapter = "Preface"
            verse = 0
            verses = []
            title = collSOUP.title.string.strip()
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            d = textsoup.find("div")
            verses.append(d.contents[0])
            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass


                text = p.get_text()
                text = text.strip()

                verses.append(text)

                for v in verses:
                    if v.startswith('Christian'):
                        continue

                    if v is None or v == '' or v.isspace():
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'prose'))
                verses = []


if __name__ == '__main__':
    main()
