import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

# works as intended, but chapter divisions need to be checked

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/andronicus.html'
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
        c.execute("DELETE FROM texts WHERE author = 'Livius Andronicus'")


        for url in textsURL:
            chapter = "-1"
            title = collSOUP.title.string.split(":")[1].strip()
            verse = 0
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

                chapter_f = p.find('b')
                if chapter_f is not None:
                    chapter = p.get_text().strip()
                    continue

                try:
                    try:
                        text = p.find('br').previous_sibling.previous_sibling.strip()
                    except:
                        text = p.find('br').previous_sibling.strip()
                    try:
                        verse = p.find('br').next_sibling.next_sibling.strip()
                    except:
                        verse = p.find('br').next_sibling.strip()

                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, text, url, 'poetry'))
                except:
                    pass # should only throw an exception on the last <p> tag with nothing but links



if __name__ == '__main__':
    main()
