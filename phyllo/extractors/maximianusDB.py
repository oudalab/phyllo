import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# works great!

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/maximianus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = collSOUP.title.string.split(":")[1].strip()
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Maximianus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.find("p").string.strip()
            chapter = -1
            verse = 0

            getp = textsoup.findAll('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                if p.find('b') is not None:
                    chapter = p.find('b').get_text()
                    verse = 0
                    continue

                brtags = p.findAll('br')
                if brtags == []:
                    continue
                verses = []
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
                    # remove in-text line numbers
                    if text.endswith(r'[0-9]+ | [0-9]+a'):
                        try:
                            text = text.split(r'[0-9]')[0].strip()
                        except:
                            pass
                    verses.append(text)

                for v in verses:
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v, url, 'poetry'))

if __name__ == '__main__':
    main()
