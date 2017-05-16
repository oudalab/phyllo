import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
#from phyllo_logger import logger

# Case 1: Sections split by numbers (Roman or not) followed by a period, or bracketed. Subsections split by <p> tags
def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 0

    for p in ptags:
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
        if len(text) <= 0 or text.startswith('The Misc\n'):
            continue
        text = re.split('^([0-9]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
            try:
                if text[1].isupper(): # chapters are in all caps
                    if not text[1].startswith('['): # brackets don't belong here!
                        chapter = text[0] + '. ' + text[1] # no harm in putting it back together.
                        verse = 0 # reset verse count
                else: # otherwise it's not a chapter, but listed as a verse
                    group = re.split('(?<!I\.\s)[0-9]+\.\s', element) # often preceded by number
                    for line in group:
                        if line.isspace() or line == '':
                            continue
                        if line.startswith('The Misc'):
                            continue
                        if chapter == line:
                            continue
                        verse+=1 # increment verse
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, line.strip(), URL, 'prose'))
            except:
                if element.startswith('J. '):  # in its own paragraph
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, element.strip(), URL, 'prose'))
                    continue
                group = re.split('(?<!I\.\s)[0-9]+\.\s', element)  # each verse technically preceded by number
                for line in group:
                    if line.isspace() or line == '':
                        continue
                    if line.startswith('The Misc'):
                        continue
                    if chapter == line:
                        continue
                    verse += 1  # increment verse
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, line.strip(), URL, 'prose'))

def main():
    # The collection URL below. In this example, we have a link to Cicero.
    collURL = 'http://www.thelatinlibrary.com/caeciliusbalbus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = 'CAECILIUS BALBUS'
    date = '-' # unknown date
    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Pseudo-Caecilius Balbus'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            parsecase1(getp, c, colltitle, title, author, date, url)

    #logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
