import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# sections are split by roman numerals, subsections by p tags.
def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 1
    # entry deletion is done in main()
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
        # Skip empty paragraphs.
        if len(text) <= 0 or text.startswith('Cicero\n'):
            continue
        text = re.split('^([IVX]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)

        if len(text) > 1:
            i = 0
            while text[i] is None:
                i+=1
            chapter = text[i]
            i+=1
            while text[i] is None:
                i+=1
            passage = text[i].strip()
            verse = 1
        else:
            passage = text[0]
            verse+=1
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


def main():
    siteURL = 'http://www.thelatinlibrary.com'
    curtiusURL = 'http://www.thelatinlibrary.com/curtius.html'
    curtiusOpen = urllib.request.urlopen(curtiusURL)
    curtiusSOUP = BeautifulSoup(curtiusOpen, 'html5lib')
    author = curtiusSOUP.title.string.strip()
    colltitle = curtiusSOUP.h1.string.strip()
    date = curtiusSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = []
    # get links to books in the collection
    for a in curtiusSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Curtius Rufus'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            parsecase1(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")

if __name__ == '__main__':
    main()
