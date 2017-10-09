import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger
import nltk
from itertools import cycle

nltk.download('punkt')

from nltk import sent_tokenize


# Case 2: Sections are split by <p> tags and subsections by un/bracketed numbers.
def parsecase2(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = 0
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
        if text.startswith("Dante\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        if URL.endswith('ep.shtml'):
            chaptest = p.find('b')
            if chaptest is not None:
                chapter = text
                continue
        if text.startswith('I') or text.startswith('V') or text.startswith('X'):
            chapter = text
            continue
        text = re.split('^([0-9]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)

        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric() or len(item) < 5:
                verse = item
            else:
                passage = item
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), URL, 'prose'))


# Case 3: Chapters separated by un/bracketed numbers, similarly to sentences.
def parsecase3(ptags, c, colltitle, title, author, date, URL):
    chapter = -1
    verse = -1
    isnumeral = case3isNumeral(ptags)
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
        if len(text) <= 0:
            continue
        text = re.split('([IVXL]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
        for item in text:
            if item is None:
                continue
            item = item.strip()
            if item.isspace() or item == '' or item.startswith("Dante\n"):
                continue
            if item.isdigit() and not isnumeral:
                chapter = item
            elif item.isdigit() and isnumeral:
                verse = item
            elif len(item) < 5 and isnumeral:
                chapter = item
            else:
                passage = item
                # Remove brackets if they have been picked up.
                if chapter.startswith('['):
                    chapter = chapter[:-1]
                    chapter = chapter[1:]
                if passage.startswith('['):
                    passage = passage[:-1]
                    passage = passage[1:]
                if passage == chapter:
                    continue
                else: # chapter/passage correction
                    chaptertest = chapter + 'I'
                    chaptertest2 = chapter[:-2] + 'V'
                    chaptertest3 = chapter[:-3] + 'V'
                    chaptertest4 = chapter[:-4] + 'IX'
                    chaptertest5 = chapter[:-2] + 'X'
                    if (chapter == 'LXIX' or chapter == 'LXX') and passage == 'L':
                        continue
                    if passage == chaptertest or passage == chaptertest2 or passage == chaptertest3\
                            or passage == chaptertest4 or passage == chaptertest5:
                        chapter = passage
                        continue
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, passage.strip(), URL, 'prose'))


# this function checks if the work uses Roman Numerals or numerical values for chapters.
def case3isNumeral(ptags):
    for p in ptags:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        if p.get_text().strip() is None or p.get_text().strip() == '':
            continue
        firstp = p.get_text().strip()
        break
    firstp = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', firstp)
    if firstp[0] is not None:
        if firstp[0].isdigit():
            return False
        else:
            return True
    elif firstp[1] is not None:
        if firstp[1].isdigit():
            return False
        else:
            return True
    elif firstp[2] is not None:
        if firstp[2].isdigit():
            return False
        else:
            return True


# This case parses poetry
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
        textsURL.remove("http://www.thelatinlibrary.com/medieval.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below and other information from the author's main page
    collURL = 'http://www.thelatinlibrary.com/dante.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = 'DANTE ALAGHERI'
    date = '1265-1321'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Dante'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')

            if url.endswith('mon1.shtml') or url.endswith('mon2.shtml') or url.endswith('mon3.shtml'):
                parsecase3(getp, c, colltitle, title, author, date, url)
            elif url.endswith('vulgar.shtml') or url.endswith('vulgar2.shtml') or url.endswith('ep.shtml'):
                parsecase2(getp, c, colltitle, title, author, date, url)
            elif url.endswith('ec1.shtml'):
                parsePoem(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")

if __name__ == '__main__':
    main()
