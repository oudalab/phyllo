import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# this works

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/priapea.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.p.get_text().strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'CARMINA PRIAPEA'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            title = title.strip()
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

                brtags = p.findAll('br')
                verses = []
                if brtags == []:
                    textstr = p.get_text()
                    if textstr.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    else:
                        chapter = textstr.replace("[", '').replace("]", "").strip()
                        verse = 0
                        continue
                else:
                    try:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.strip()
                    if firstline.startswith("*"):
                        continue  # ignore some lines of **** that aren't actual text
                    verses.append(firstline)

                    for br in brtags:
                        try:
                            text = br.next_sibling.next_sibling.strip()
                        except:
                            text = br.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        if text.startswith("*") or text.startswith(" *"):
                            continue  # ignore some lines of **** that aren't actual text

                        verses.append(text)

                for v in verses:
                    if v.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter.strip(),
                               verse, v.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
