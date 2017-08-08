import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/rimbaud.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "ARTHUR RIMBAUD"
    date = collSOUP.span.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    date=date.strip()
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Arthur Rimbaud'")

        for url in textsURL:
            chapter = 0
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            getp = textsoup.find_all('p')
            title = "VER ERAT"
            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation', 'smallborder']:  # these are not part of the main t
                        continue
                except:
                    pass

                brtags = p.findAll('br')
                verses = []
                try:
                    try:
                        firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    verses.append(firstline)
                except:
                    pass
                if brtags is not None:
                    chapter += 1
                    tx = p.get_text().strip()
                    if tx != '' or tx is not None:
                        verses.append(tx)
                for br in brtags:
                    try:
                        text = br.next_sibling.next_sibling.strip()
                    except:
                        text = br.next_sibling.strip()
                    if text is None or text == '' or text.isspace():
                        continue
                    verses.append(text)
                for v in verses:
                    if v.strip().startswith("Neo-"):
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))


if __name__ == '__main__':
    main()
