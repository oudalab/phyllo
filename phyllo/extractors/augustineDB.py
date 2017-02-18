import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# De Civitate Dei, De Trinitate
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
        if len(text) <= 0 or text.startswith('Augustine\n'):
            continue
        text = re.split('^\[(.+)\]\s|^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', text)
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
        if passage.startswith('Augustine'):
            continue
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


# Confessiones, Epistula de Libris de Civitate Dei
def altparsecase1(ptags, c, colltitle, title, author, date, URL):
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
        if len(text) <= 0 or text.startswith('Augustine\n'):
            continue
        # check for chapter
        if text[0].isnumeric() and len(text) < 10:
            chapter = text
            verse = 0
            continue
        # using negative lookbehind assertion to not match with abbreviations of one or two letters and ellipses.
        # ellipses are not entirely captured, but now it doesn't leave empty cells in the database.
        text = re.split('\[([0-9]+)\]|(?<!\s[A-Z]|[A-Z][a-z])\.\s(?!\.\s)', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
            passage = element
            if passage.startswith('Augustine'):
                continue
            verse += 1
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, passage.strip(), URL, 'prose'))


# Contra Secundam Iuliani Responsionem
def altaltparsecase1(ptags, c, colltitle, title, author, date, URL):
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
        if len(text) <= 0 or text.startswith('Augustine\n'):
            continue
        # check chapter
        chapterb = p.find('b')
        if chapterb is not None:
            chapter = text
            verse = 0
            continue
        passage = text
        # check for that last line with the author name that doesn't need to be here
        if passage.startswith('Augustine'):
            continue
        verse +=1
        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                  (None, colltitle, title, 'Latin', author, date, chapter,
                   verse, passage.strip(), URL, 'prose'))


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
        if text.startswith("Augustine\n"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue

        chapterb = p.find('b')
        if chapterb is not None:
            chapter = text
            continue
        text = re.split('([0-9]+)\.\s', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        chapter +=1
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
            if item.isspace() or item == '' or item.startswith("Cicero\n"):
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
    firstp = ''
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
    collURL = 'http://www.thelatinlibrary.com/cic.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Augustine'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            if 'conf' in url or 'epistula.s' in url:
                altparsecase1(getp, c, colltitle, title, author, date, url)
            elif 'civ' in url or 'trin' in url or 'dia.s' in url:
                parsecase1(getp, c, colltitle, title, author, date, url)
            elif 'fide' in url or 'reg.s' in url:
                parsecase2(getp, c, colltitle, title, author, date, url)
            elif 'catechiz' in url:
                parsecase3(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
