import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# chose to use internal numbers meaning there are some duplicate verse numbers. Check this.

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/bonaventura.itinerarium.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "ITINERARIUM MENTIS IN DEUM"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'St. Bonaventure'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle

            getp = textsoup.find_all('p')
            chapter = -1
            verse = 0

            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'shortborder', 'smallborder']:  # these are not part of the main t
                        chapter = ""
                        continue
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                verses = []

                text = p.get_text()
                text = text.strip()

                chapter_f = p.find('b')
                if chapter_f is not None or text.startswith("CAPUT"):
                    if text.startswith("CAPUT PRIMUM"):
                        continue
                    if text.startswith("INCIPIT SPECULATIO PAUPERIS IN DESERTO"):
                        chapter = "CAPUT PRIMUM"
                    chapter = chapter + " " + text
                    print(chapter)
                    verse = 0
                    continue

                if re.match("[0-9]+\.", text):
                    # this paragraph has a verse number
                    verse = text.split(".")[0].strip()
                    text = text.replace(verse + ".", "").strip()

                verses.append(text)

                for v in verses:
                    if v is None or v == '' or v.isspace():
                        continue
                    if v.startswith('Christian'):
                        continue
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
