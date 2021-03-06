import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def main():
    # The collection URL below.
    url = 'http://www.thelatinlibrary.com/persius.html'
    openurl = urllib.request.urlopen(url)
    textsoup = BeautifulSoup(openurl, 'html5lib')
    author = textsoup.title.string.strip()

    # info taken from Wikipedia
    colltitle = 'AVLVS PERSIVS FLACCVS'
    date = "4 December 34 - 24 November 62"

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Persius'")

        chapter = -1
        verse = 0
        openurl = urllib.request.urlopen(url)
        textsoup = BeautifulSoup(openurl, 'html5lib')
        try:
            title = textsoup.title.string.split(':')[1].strip()
        except:
            title = textsoup.title.string.strip()
        getp = textsoup.find_all('p')
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            # find chapter
            chapter_f = p.find('b')
            if chapter_f is not None:
                chapter = p.get_text().strip()
                verse = 0
                continue
            else:
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
                for br in brtags:
                    try:
                        text = br.next_sibling.next_sibling.strip()
                    except:
                        text = br.next_sibling.strip()
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
