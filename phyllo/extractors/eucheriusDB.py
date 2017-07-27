import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# good to go!


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/eucherius.html'
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
        c.execute("DELETE FROM texts WHERE author = 'Eucherius'")

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

                if p.find('b') is not None:
                    continue


                if re.match('2\.', text):
                    # handle 2 verses in same <p>
                    verse = 1
                    text = text.replace("2.", "").strip()
                    lines = re.split("3\.", text)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith('Christian'):
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, l.strip(), url, 'prose'))
                    continue

                elif re.match('[0-9]+\.', text):
                    # get verse numbers
                    verse = text.split(".")[0].strip()
                    text = text.replace(verse + ".", "").strip()

                verses.append(text)

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))



if __name__ == '__main__':
    main()
