import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# works as intended.


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/grattius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(":")[0].strip()
    colltitle = 'FALISCUS GRATTIUS'
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Grattius'")


        for url in textsURL:
            chapter = "-1"
            verse = 0
            title = collSOUP.title.string.split(":")[1].strip()
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            getp = textsoup.find_all('p')

            for p in getp:

                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                # skip paragraphs that don't contain actual text
                txtstr = p.get_text().strip()
                if txtstr.startswith("The") or txtstr.startswith("*"):
                    continue

                brtags = p.findAll('br')
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
                    if text.endswith(r'[0-9]+'):
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
