import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# this works

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/epitaphs.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "various authors"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE title = 'ROMAN EPITAPHS'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle
            title = title.strip()
            chapter = -1
            verse = 0
            next_chapter = ''  # for storing chapter values that are stuck in the previous paragraph

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
                if next_chapter != '':
                    chapter = next_chapter
                    verse = 0
                    next_chapter = ''

                if brtags == []:
                    textstr = p.get_text()
                    textstr = textstr.strip()

                    if textstr.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    elif textstr.startswith("B ") or textstr.startswith("CIL "):
                        chapter = textstr.strip()
                        verse = 0
                        continue

                if len(p.findAll('b')) > 1:  # handle B 439 which has <b> tags in the middle of words
                    textstr = p.get_text()
                    lines = textstr.split("\n")
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        verses.append(l)

                else:
                    try:
                        try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = p.get_text()  # handle single-line epitaphs
                    verses.append(firstline)

                    for br in brtags:
                        try:
                            text = br.next_sibling.next_sibling.strip()
                        except:
                            text = br.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        text = text.strip()
                        if text.startswith("B ") or text.startswith("CIL "):  # handle improperly formatted chapter names
                            next_chapter = text
                            continue
                        verses.append(text)

                for v in verses:
                    if v.startswith("The Miscellany"):
                        continue  # ignore links at the end
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'poetry'))


if __name__ == '__main__':
    main()
