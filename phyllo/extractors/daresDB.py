import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# code works as intended.
# question: what to do with "CORNELIUS NEPOS SALLUSTIO CRISPO S."?
# i just ignored it because I'm not sure if it's text or a chapter title or what

def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/dares1.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.split(',')[0].strip()
    colltitle = author.upper()
    date = collSOUP.p.span.string.strip()

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Dares the Phrygian'")

        for url in textsURL:
            chapter = '-1'
            verse = 1
            title = collSOUP.title.string.split(',')[1].strip()
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
                passage = ''
                text = p.get_text().strip()
                # Skip empty paragraphs. and skip the last part with the collection link.
                if len(text) <= 0:
                    continue
                text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
                for element in text:
                    if element is None or element == '' or element.isspace():
                        text.remove(element)
                # The split should not alter sections with no prefixed roman numeral.
                if len(text) > 1:
                    i = 0
                    while text[i] is None:
                        i += 1
                    chapter = text[i]
                    i += 1
                    while text[i] is None:
                        i += 1
                    passage = text[i].strip()
                    verse = 1
                else:
                    passage = text[0]
                    if len(passage) < 6:
                        continue

                # check for that last line with the author name that doesn't need to be here
                if passage.startswith("The Misc"):
                    continue
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
