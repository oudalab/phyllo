import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# this is good to go!

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/bernardclairvaux.shtml'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(':')[0].strip()
    colltitle = "S. BERNARDUS CLARAEVALLENSIS"
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'S. Bernard of Clairvaux'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(':')[1].strip()

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

                try:
                    text = p.string.strip()
                except:
                    text = p.get_text()
                    text = text.strip()

                if text.startswith("ADMONITIO") or text.startswith("PROLOGUS") or text.startswith("CAPUT"):
                    # this is a chapter heading
                    verse = -1
                    chapter = text
                    print(chapter)
                    continue

                if re.match("[0-9]+\.", text):
                    # this paragraph has a verse number
                    verse = text.split(".")[0].strip()
                    text = text.replace(verse + ".", "").strip()

                verses.append(text)

                for v in verses:
                    if v is None or v == '' or v.isspace():
                        continue
                    if v.startswith('Medieval'):
                        continue
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
