import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# this works as intended.

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/prec.terr.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'Precatio Terrae'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle
            chapter = -1
            verse = 0

            getp = textsoup.find_all('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                verses = []
                brtags = p.findAll('br')
                if brtags != []:
                    try:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.strip()
                    verses.append(firstline)

                    for br in brtags:
                        try:
                            text = br.next_sibling.next_sibling.strip()
                        except:
                            text = br.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        verses.append(text)

                else:
                    text = p.get_text()
                    text = text.strip()
                    verses.append(text)

                for v in verses:
                    if v.startswith('The'):
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))


if __name__ == '__main__':
    main()
