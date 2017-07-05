import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup


# possible further line splitting needed in Apostles' Creed
# poetry or prose

def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/creeds.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "various authors"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE title = 'Early Christian Creeds'")


        for url in textsURL:
            chapter = "-1"
            verse = 0
            title = colltitle
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['pagehead']:  # these are not part of the main t
                        # this is a creed title
                        chapter = p.string.strip()
                        verse = 0
                        print(chapter)
                        continue
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                verses = []

                brtags = p.findAll('br')
                if brtags != []:
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

                        verses.append(text)

                else:
                    text = p.get_text()
                    verses.append(text.strip())


                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'poetry'))



if __name__ == '__main__':
    main()
