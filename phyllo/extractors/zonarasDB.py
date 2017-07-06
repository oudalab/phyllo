import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger



def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/zonaras.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = author
    date = "no date found"
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Zonaras'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = collSOUP.title.string.split(":")[1].strip()
            chapter = -1
            verse = 612

            getp = textsoup.find_all('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main text
                        continue
                except:
                    pass

                verses = []

                if p.find('br') is not None:
                    # these are a few random lines of poetry, and the list of notes at the end.

                    lines = re.split("\n", p.get_text())
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        verses.append(l)
                else:
                    btags = p.findAll('b')
                    try:
                        try:
                            firstline = btags[0].previous_sibling.strip()
                        except:
                            firstline = btags[0].previous_sibling.previous_sibling.strip()
                    except:
                        firstline = p.get_text()
                    verses.append(firstline.strip())
                    for b in btags:
                        bstring = b.string.strip()
                        if re.match('[IVXL]+', bstring):
                            # this is a chapter
                            chapter = bstring
                        elif bstring.startswith("NOTES"):
                            # this is also a chapter, with no text in the paragraph
                            chapter = bstring
                        else:
                            # if it's not a chapter, its a verse
                            verse = bstring
                        try:
                            text = b.next_sibling.next_sibling.strip()
                        except:
                            text = b.next_sibling.strip()
                        if text is None or text == '' or text.isspace():
                            continue
                        verses.append(text)
                if chapter == "NOTES.":
                    verse = 0
                    for v in verses:
                        if v.startswith('The Miscellany'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        if v.startswith("The translator"):
                            continue
                            # skip an english note
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))
                else:
                    for v in verses:
                        if v.startswith('The Miscellany'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        if v.startswith("End of"):
                            continue
                            # skip an english note
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
