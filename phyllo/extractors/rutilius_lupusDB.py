import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# good to go!!!!

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/rutiliuslupus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].replace("P.", "Publius").strip()
    colltitle = collSOUP.title.string.split(":")[1].strip()
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Publius Rutilius Lupus'")


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

                text = p.get_text()
                text = text.strip()

                if text.startswith("[I"):
                    chapter = text
                    verse = 0
                    continue
                else:
                    verses = []
                    verses.append(text)

                for v in verses:
                    if v.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'prose'))



if __name__ == '__main__':
    main()
