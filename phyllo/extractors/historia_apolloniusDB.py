import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# seems fine I think.
# double check author

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/histapoll.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown" # check this???? - make it "attributed to..."
    colltitle = collSOUP.title.string.strip()
    date = 'no date found'
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE title = 'Historia Apollonii regis Tyri'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle
            getp = textsoup.find_all('p')

            chapter = '-1'
            verse = 0

            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main text
                        continue
                except:
                    pass

                chapter_f = p.find('b')
                if chapter_f is not None:
                    if chapter_f.string.startswith("."):
                        continue
                    else:
                        chapter = chapter_f.string.strip()
                        verse = 0

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
                        verses.append(text)

                elif p.find('b') is not None:
                    try:
                        text = p.find('b').next_sibling.next_sibling.strip()
                    except:
                        text = p.find('b').next_sibling.strip()
                    verses.append(text)
                else:
                    text = p.get_text()
                    text = text.strip()
                    verses.append(text)

                for v in verses:
                    if v is None or v == '' or v.isspace():
                        continue
                    if v.startswith("[The"):
                        continue
                    if v.startswith("The"):
                        continue
                    verse += 1
                    if chapter == '':
                        chapter = '-' # what should be 43 is actually not a real chapter.
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
