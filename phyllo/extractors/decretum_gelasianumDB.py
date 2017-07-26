import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# chose to ignore internal numbering (I, II, etc.) in favor of numbering paragraphs
# left internal numbers as part of text
# check this assumption

# problem:
# chapter titles are enclosed in <div> tags. I can't seem to get the text out of them.

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/decretum.html'
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
        c.execute("DELETE FROM texts WHERE title = 'Decretum Gelasianum'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle
            verses = []
            tablerows = []
            skipThese = []

            getp = textsoup.find_all('p')
            verse = 0
            chapter = -1

            table = textsoup.find('table')
            print('TABLE: ' + table.get_text())
            rows = table.find_all('tr')
            for r in rows:
                print(r)
                if r.find('p') is not None:
                    r.p.unwrap()  # remove p tags within table
                rtext = r.get_text()
                tablerows.append(rtext.strip())
                skipThese.append(rtext.split('\n')[0].strip())

            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                verses = []
                tbl = p.find('table')
                if tbl is not None:
                    rows = tbl.find_all('tr')
                    for r in rows:
                        if r.find('p') is not None:
                            r.p.unwrap()  # remove p tags within table
                        rtext = r.get_text()
                        verses.append(rtext.strip())
                        skipThese.append(rtext.split('\n')[0].strip())
                else:
                    text = p.get_text()
                    text = text.strip()
                    if re.match('[IVXL]+\.', text):
                        # this is a chapter
                        chapter = text.split(' ')[0]
                        verse = 0
                        text = text.replace(chapter, '')
                    verses.append(text)
                    if text.startswith("1. INCIPIT ORDO VETERIS TESTAMENTI:"):
                        # this where the table we found above goes
                        for t in tablerows:
                            verses.append(t)
                    if text.startswith("ad") or text.startswith("secundum") or text.startswith("proverbia"):
                        continue
                    if text.startswith("ecclesiast") or text.startswith("cantica canticorum"):
                        continue

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
