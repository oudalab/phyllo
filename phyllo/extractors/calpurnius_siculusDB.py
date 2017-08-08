import sqlite3
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/calpurniussiculus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "T. Calpurnius Siculus"
    colltitle = "Bucolica"
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'T. Calpurnius Siculus'")

        for url in textsURL:
            chapter = -1
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = 'Bucolica'
            getp = textsoup.find_all('p')

            for p in getp:
                # reset verse counter
                verse = 0

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                try:
                    if p is None:
                        continue
                except:
                    pass


                try:
                    if p.string() is None:
                        continue
                except:
                    pass



                # find chapter
                try:
                    text = p.string.strip()
                    if text.startswith("BVCOLICA"):
                        chapter = text
                        continue
                except:
                    pass

                brtags = p.find_all('br')
                verses = []
                try:
                    try:
                        firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    verses.append(firstline)
                except:
                    pass

                count = 0
                for br in brtags:
                    count += 1
                    try:
                        text = br.next_sibling.strip()
                    except:
                        text = br.next_sibling.next_sibling.strip()
                    if text is None or text == '' or text.isspace():
                        continue
                    verses.append(text)
                for v in verses:
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'poetry'))


if __name__ == '__main__':
    main()
