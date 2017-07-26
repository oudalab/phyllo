import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# good to go!

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/junillus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Junillus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = "Instituta Regularia Divinae Legis"

            getp = textsoup.find_all('p')
            verse = 0
            chapter = -1

            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                verses = []

                text = p.get_text()
                text = text.strip()

                findB = p.find('b')
                if findB is not None:
                    if text.endswith("Primus."):
                        title = title + " I"
                        continue
                    elif text.endswith("Secundus."):
                        title = title + "I"
                        continue
                    else:
                        chapter = text
                        verse = 0
                        print(chapter)
                        continue

                lines = re.split("[0-9]+\.", text)
                for l in lines:
                    if l.startswith('Christian'):
                        continue
                    if l is None or l == '' or l.isspace():
                        continue
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, l.strip(), url, 'prose'))



if __name__ == '__main__':
    main()
