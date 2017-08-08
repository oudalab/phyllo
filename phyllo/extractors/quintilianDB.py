import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# Case 1: Sections split by numbers (Roman or not) followed by a period, or bracketed. Subsections split by <p> tags
# for the Declamationes Maiores
def parsecase1(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = '-1'
    verse = 1

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
        if len(text) <= 0 or text.startswith('Quintilian\n'):
            continue
        text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        # The split should not alter sections with no prefixed roman numeral.
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
        # check for that last line with the author name that doesn't need to be here
        if passage.startswith('Quintilian'):
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))



# Case 2: Sections are split by <p> tags and subsections by un/bracketed numbers.
# for the Institutiones
def parsecase2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = '-1'
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
        if text.startswith("Quintilian\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # find chapter
        potchap = p.find('b')
        if potchap is not None:
            chapter = potchap.find(text=True)
            if title != 'Institutio Oratoria XII' and title != 'Institutio Oratoria XI' and \
                            title != 'Institutio Oratoria X':
                text = text.replace(chapter,'')
                # remove brackets
                if chapter.startswith('['):
                    chapter = chapter[1:]
                    chapter = chapter[:-1]
        text = re.split('([IVX]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric() or len(item) < 5:
                verse = item
            else:
                if item.startswith(verse) or item.startswith('X'):
                    verse = item
                else:
                    passage = item
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, passage.strip(), URL, 'prose'))



def getBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


# main code
def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/quintilian.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Quintilian'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            pagehead = textsoup.find('p',{'class' : 'pagehead'})
            if pagehead is not None:
                ph = pagehead.find(text=True)
                if ph.endswith('VNDEVICENSIMA\n'):
                    title = title.replace('I', 'XIX')
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.

            if title.startswith('Declamatio'):
                parsecase1(getp, c, colltitle, title, author, date, url)
            else:
                parsecase2(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
