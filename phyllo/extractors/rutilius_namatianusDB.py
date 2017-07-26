import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# good to go!!!!

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/rutilius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = author.upper()
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Rutilius Namatianus'")


        for url in textsURL:
            chapter = "-1"
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[0].strip()
            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                if p.find('b') is not None:
                    chapter = p.find('b').string.strip()
                    verse = 0
                    continue

                brtags = p.findAll('br')
                verses = []

                try:
                    try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.strip()
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
                    # remove in-text line numbers
                    if text.endswith(r'[0-9]+'):
                        try:
                            text = text.split(r'[0-9]')[0].strip()
                        except:
                            pass
                    verses.append(text)


                for v in verses:
                    if v.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'poetry'))



if __name__ == '__main__':
    main()
