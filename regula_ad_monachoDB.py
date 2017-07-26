import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# several names in the <pagehead> but not sure what to put as an author name

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/regula.html'
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
        c.execute("DELETE FROM texts WHERE title = 'REGULA AD MONACHOS I'")
        c.execute("DELETE FROM texts WHERE title = 'SS. PATRUM REGULA AD MONACHOS II.'")
        c.execute("DELETE FROM texts WHERE title = 'SS. PATRUM REGULA AD MONACHOS III.'")
        c.execute("DELETE FROM texts WHERE title = 'REGULA ORIENTALIS\nEX PATRUM ORIENTALIUM REGULIS COLLECTA'")


        for url in textsURL:
            chapter = "Preface"
            verse = 0
            title = "REGULA AD MONACHOS I"
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
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
                    if text.startswith("SS.") or text.startswith("REGULA"):
                        # this is the title of a new work
                        title = text
                        chapter = -1
                        continue
                    else:
                        if text.startswith("CAPUT"):
                            chapter = text
                            print(chapter)
                            verse = 0
                            continue
                        else:
                            chapter = chapter + ": " + text
                            continue

                if title == "REGULA AD MONACHOS I":
                    verses.append(text)

                elif text.startswith("PRAEFATIO"):
                    chapter = text
                    verse = 0
                    continue
                elif re.match('[IVXL]+\.', text):
                    chapter = text.split(" ")[0].strip()
                    print(chapter)
                    verse = 0
                    text = text.replace(chapter, '')
                    verses.append(text)
                else:
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
                               verse, v, url, 'prose'))


if __name__ == '__main__':
    main()
