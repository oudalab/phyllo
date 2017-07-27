import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# chose to ignore internal numbering (I, II, etc.) in favor of numbering paragraphs
# left internal numbers as part of text
# check this assumption

# problem:
# chapter titles are enclosed in <div> tags. I can't seem to get the text out of them.

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/eugippius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(':')[0].strip()
    colltitle = collSOUP.title.string.split(':')[1].strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Eugippius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle

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
                    print("FOUND A <B>")
                    divs = p.find_next("div")
                    print(divs)
                    for d in divs:
                        chapter = d.contents[0]
                        verse = 0
                        print(chapter)
                    continue

                verses.append(text)

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))



if __name__ == '__main__':
    main()
