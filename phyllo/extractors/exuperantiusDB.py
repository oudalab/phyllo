import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# this code works as intended and should be good to go.

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/exuperantius.shtml'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.find('p', class_='pagehead').string.strip()
    date = 'no date found'
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Julius Exuperantius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = colltitle
            getp = textsoup.find_all('p')

            chapter = 0
            verse = 0

            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass
                passage = ''
                text = p.get_text().strip()
                # Skip empty paragraphs. and skip the last part with the collection link.
                text = re.split('\[[0-9]+\]\s+| [0-9]\[[0-9]+\]\s+ | \[[0-9]+\s+\]', text)
                # N.B. this re catches all of the typos (i.e. extra spaces) in the verse numbering in this document.
                # it was designed by guess and check for this specific document.
                # should be checked thoroughly before it is used elsewhere.

                for element in text:
                    if element is None or element == '' or element.isspace():
                        text.remove(element)
                # incrememnt chapter for each paragraph
                chapter += 1
                for v in text:
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
