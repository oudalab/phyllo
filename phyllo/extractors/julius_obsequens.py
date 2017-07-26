import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup


# works as intended, but chapter divisions need to be checked

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/obsequens.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.find('p').string.strip()
    date = "no date found"


    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Julius Obsequens'")


        for url in textsURL:
            chapter = "-1"
            title = colltitle
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')



            getp = textsoup.find_all('p')

            verses = []
            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                # append the bolded sections to [verses], then get their appropriate chapter numbers from the subsequent paragraph.

                bold_f = p.find('b')
                if bold_f is not None:
                    text = p.get_text().strip()
                    verses.append(text)
                    continue

                text = p.get_text()
                text = text.strip()
                # get chapters
                if text is None or text == '' or text.isspace():
                    continue
                elif text[0].isdigit():
                    chapter = text.split(".")[0]

                # leave chapter numbers as part of the text.
                verses.append(text.strip())

                 # reset immediately before assignment to make sure no extra resets occur
                for v in verses:
                    if v.startswith("The"):
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'prose'))
                verses = []
                verse = 0



if __name__ == '__main__':
    main()
