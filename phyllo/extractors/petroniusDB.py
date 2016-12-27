import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# Case P: Sometimes it's poetry.
def parsepoem(c, colltitle, title, author, date, URL):
    chapter = -1
    verse = 0
    openurl = urllib.request.urlopen(URL)
    textsoup = BeautifulSoup(openurl, 'html5lib')
    try:
        title = textsoup.title.string.split(':')[1].strip()
    except:
        title = textsoup.title.string.strip()
    getp = textsoup.find_all('p')
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        # find chapter
        test_text = p.get_text().strip()
        if test_text.startswith("Frag"):
            verse = 0
            chapter = test_text
            continue
        else:
            brtags = p.findAll('br')
            verses = []
            # Petronius' Fragmenta also includes one-liners and paragraphs.
            if brtags == []:
                verses.append(test_text)
            try:
                try:
                    firstline = brtags[0].previous_sibling.strip()
                except:
                    firstline = brtags[0].previous_sibling.previous_sibling.strip()
                verses.append(firstline)
            except:
                pass
            for br in brtags:
                try:
                    text = br.next_sibling.next_sibling.strip()
                except:
                    text = br.next_sibling.strip()
                if text is None or text == '' or text.isspace():
                    continue
                verses.append(text)
        for v in verses:
            # verse number assignment.
            if v.startswith('The Latin'):
                continue
            verse += 1
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, v, URL, 'poetry'))

# Case 1: Sections split by numbers (Roman or not) followed by a period, or bracketed. Subsections split by <p> tags
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
        if len(text) <= 0 or text.startswith('Petronius\n') or text.startswith('The Latin'):
            continue
        text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
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
        if passage.startswith('Petronius'):
            continue
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
    collURL = 'http://www.thelatinlibrary.com/petronius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Petronius'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.
            if not url.endswith('frag.html'):
                parsecase1(getp, c, colltitle, title, author, date, url)
            else:
                parsepoem(c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
