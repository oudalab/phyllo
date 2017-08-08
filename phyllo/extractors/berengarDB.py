import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# should be good

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/berengar.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(':')[0].strip()
    colltitle = collSOUP.p.string.strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Berengar'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(':')[1].strip()

            getp = textsoup.find_all('p')
            chapter = 0
            verse = 0
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                chapter += 1
                verse = 0
                verses = []
                text = p.get_text()
                text = text.strip() # we can't use br.next_sibling b/c of <i> tags throughout the text
                print(chapter)

                if p.find('br') is not None:
                    lines = re.split("\n", text)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith('Christian'):
                            continue
                        verses.append(l)
                else:
                    verses.append(text.strip())

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
