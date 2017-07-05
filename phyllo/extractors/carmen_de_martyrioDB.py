import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems to work fine
# should probably check on chapter divisions

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/anon.martyrio.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "Incerti Auctoris (Hilarii?, Valerii Cemenelensis?)"
    colltitle = collSOUP.title.string.strip()
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE title = 'Carmen de Martyrio Maccabaeorum'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle

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

                if p.find('br') is not None:
                    brtags = p.findAll('br')
                    try:
                        try:
                            firstline = brtags[0].previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        verses.append(firstline)
                    except:
                        pass
                    for br in brtags:
                        try:
                            text = br.next_sibling.next_sibling.strip()
                        except:
                            text = br.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        if text.endswith(r'[0-9]+'):
                            try:
                                text = text.split(r'[0-9]')[0].strip()
                            except:
                                pass
                        verses.append(text)

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))


if __name__ == '__main__':
    main()
