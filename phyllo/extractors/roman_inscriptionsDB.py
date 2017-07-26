import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/inscriptions.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "various authors"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'Inscriptiones'")


        for url in textsURL:
            chapter = "-1"
            verse = 0
            title = colltitle
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                if p.find('b') is not None:
                    chapter = p.find('b').string.strip()
                    continue

                verses = []

                text = p.get_text()
                if text.startswith("The Miscellany"):
                    continue

                try:
                    verse = text.split(":")[0]
                    verses.append(text.split(":")[1])
                except:
                    pass

                for v in verses:
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))



if __name__ == '__main__':
    main()
