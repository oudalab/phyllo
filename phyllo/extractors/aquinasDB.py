import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# This case parses poetry.
def parsePoem(ptags, c, colltitle, title, author, date, url):
    chapter = -1
    verse = 0
    for p in ptags:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        # find chapter
        chapter_f = p.find('b')
        if chapter_f is not None:
            chapter = p.get_text().strip()
            verse = 0
            continue
        else:
            brtags = p.findAll('br')
            verses = []
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
            verse += 1
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, v, url, 'poetry'))


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
        if len(text) <= 0 or text.startswith('St. Thomas\n'):
            continue
        chapter_f = p.find('b')
        if chapter_f is not None:
            chapter = p.get_text().strip()
            verse = 0
            continue
        else:
            text = re.split('^^\[([IVXL]+)\]\.', text)
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
                verse += 1
            # check for that last line with the author name that doesn't need to be here
            if passage.startswith('St. Thomas'):
                continue
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, passage.strip(), URL, 'prose'))


# alt Case 2: Sections are split by <p> tags
def parsecase2alt(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = -1
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
        chapter += 1
        passage = ''
        text = p.get_text().strip()
        if text.isupper() or text.startswith("St. Thomas Aquinas\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, text.strip(), URL, 'prose'))


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
        textsURL.remove("http://www.thelatinlibrary.com/christian.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL

def getParsLink(soup):
    siteURL = 'http://www.thelatinlibrary.com/aquinas'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/aquinas//index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/aquinas//index.html")
        textsURL.remove("http://www.thelatinlibrary.com/aquinas//christian.html")
        textsURL.remove("http://www.thelatinlibrary.com/aquinas//aquinas.html")
        textsURL.remove("http://www.thelatinlibrary.com/aquinas//classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below. In this example, we have a link to Cicero.
    collURL = 'http://www.thelatinlibrary.com/aquinas.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = author.upper()
    date = 'A.D. 1224-1274'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='St. Thomas Aquinas'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            title = title.replace('St. Thomas Aquinas ', '')
            getp = textsoup.find_all('p')
            if url.endswith('prologus.shtml') or url.endswith('epist.shtml') or url.endswith('princ.shtml'):
                logger.info('Parsing ' + url + ' ...')
                parsecase2alt(getp, c, colltitle, title, author, date, url)
            elif url.endswith('christi.shtml'):
                logger.info('Parsing ' + url + ' ...')
                parsePoem(getp, c, colltitle, title, author, date, url)
            elif url.endswith('ente.shtml'):
                logger.info('Parsing ' + url + ' ...')
                parsecase1(getp, c, colltitle, title, author, date, url)
            elif url.endswith('p1.shtml'):
                parsprima = getParsLink(textsoup)
                for parsurl in parsprima:
                    logger.info('Parsing '+ parsurl + '...')
                    parsopen = urllib.request.urlopen(parsurl)
                    parssoup = BeautifulSoup(parsopen, 'html5lib')
                    alltext = parssoup.get_text().strip()
                    textsep = re.split('\n', alltext)
                    chapter = '-'
                    verse = 0
                    quaestioget = False
                    for item in textsep:
                        if item is None:
                            continue
                        elif item.strip() == '' or item.strip().isspace():
                            continue
                        elif item.strip().startswith('St. Thomas') or item.strip().startswith('Christian Latin') \
                                or item.strip().startswith('The Latin Lib') or item.strip().startswith('The Classics'):
                            continue
                        if item.startswith("QUAESTIO"):
                            title = item
                            quaestioget = True
                        elif item.startswith('ARTICULUS'):
                            chapter = item
                            verse = 0
                        else:
                            if quaestioget is True:
                                verse += 1
                                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                          (None, colltitle, title, 'Latin', author, date, chapter,
                                           verse, item.strip(), parsurl, 'prose'))


if __name__ == '__main__':
    main()
