import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


###########
# Letters to Caesar are not split by sentences.

# Case 2: Sections are split by <p> tags and subsections by sentences.
# Bellum Iugurthinum
def altparsecase2(ptags, c, colltitle, title, author, date, URL):
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
        if text.startswith("Sallust\n") or text.startswith("SallustThe"):
            continue
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # using negative lookbehind assertion to not match with abbreviations of one or two letters and ellipses.
        # ellipses are not entirely captured, but now it doesn't leave empty cells in the database.
        text = re.split('\[([0-9]+)\]|(?<!\s[A-Z]|[A-Z][a-z])\.\s(?!\.\s)', text)
        for element in text:
            if element is None or element == '' or element.isspace():
                text.remove(element)
        # chapter +=1
        for count, item in enumerate(text):
            if item is None:
                continue
            if item.isnumeric():
                chapter = item
                verse = 0
                continue
            verse+=1
            passage = item.strip()
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, passage.strip(), URL, 'prose'))


# Case 3: Chapters separated by un/bracketed numbers, similarly to sentences.
# Bellum Catilinae, Oratio Lepidi, Oratio Phillipi
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
        if title.endswith("Catilinae"):
            text = re.split('([0-9]+)\s|\[([IVX]+)\]\s|\[([0-9]+)\]\s', text)
        else:
            text = re.split('([IVX]+)\.\s|([0-9]+)\s|\[([IVX]+)\]\s|\[([0-9]+)\]\s', text)
        if title.endswith("Lepidus") or title.endswith("Philippus"):
            chapter = int(chapter) + 1
        for item in text:
            if item is None:
                continue
            item = item.strip()
            if item.isspace() or item == '' or item.startswith("Sallust\n") or item.startswith("SallustThe"):
                continue
            if item.isdigit() and not isnumeral:
                chapter = item
            elif item.isdigit() and isnumeral:
                verse = item
                if int(verse) == 1:
                    # chapters are in p tags most of the time.
                    if not title.startswith('Letter to Caesar'):
                        chapter = int(chapter) + 1
            elif len(item) < 5 and isnumeral and title.startswith("Letter to Caesar"):
                chapter = item
                if title.startswith("Letter to"):
                    verse = 0
            else:
                passage = item
                # Remove brackets if they have been picked up.
                chapter = str(chapter)
                if chapter.startswith('['):
                    chapter = chapter[:-1]
                    chapter = chapter[1:]
                if passage.startswith('['):
                    passage = passage[:-1]
                    passage = passage[1:]
                if passage == chapter:
                    continue
                if title.startswith("Letter to"):
                    verse += 1
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
    firstp = re.split('^([IVX]+)\.\s|^([0-9]+)\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', firstp)
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


# Alternative Case 3: Chapters are split by [numbers] and sentences by unbracketed number
# Fragmenta
def altcase3(ptags, c, colltitle, title, author, date, URL):
    chapter = -1
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
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # check if chapter is in the paragraph tag
        potchap = p.find('b')
        if potchap is not None:
            chapter = text
            verse = 1
            continue
        # split the paragraph by chapter: [#] -- it's always at the front of the line
        text = re.split('^\[([0-9]+)\]', text)
        try: text.remove('')
        except: pass
        if text[0].isnumeric():
            # overwrites bold chapters.
            chapter = text[0]
            # if the paragraph has a chapter number, the next item may have numbers to delimit subsections
            passage = re.split('([0-9]+)', text[1])
        else:
            # alternatively, it may not have a chapter number.
            passage = re.split('([0-9]+)', text[0])

        try: passage.remove('')
        except: pass
        for item in passage:
            if item is None or item.isspace() or item == '':
                continue
            elif item.strip().isnumeric():
                verse = item.strip()
            else:
                # not sure where the \n came from but I gotta' replace 'em
                item = item.replace('\n', ' ')
                # item must be a bunch of words
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, item.strip(), URL, 'prose'))


# there are no numbers. Sections are split by <p> tags, subsections by punctuation.
# Note: For Speech of Pompey, the last paragraph has verse 0s because they are unassigned.
def parsecase4(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = '-1'
    hasversenum = False
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
        if text.startswith("SallustThe"):
            continue
        # various special things to exclude one- and two-letter abbreviations from the dot parsing
        text = re.split('([0-9]+)|(?<!\s[A-Z]|[A-Z][a-z])\.\s(?!\.\s)', text)
        chapter+=1 # each section is a paragraph
        verse = 0 # reset each verse; overwritten by subsection number if available
        try: text.remove('')
        except: pass
        for item in text:
            if item is None or item.isspace():
                continue
            if item.isnumeric():
                verse = item # overwrites verse reset
                hasversenum = True
                continue
            if hasversenum is False:
                verse += 1
            if item.strip() == '' or item.strip().isspace():
                continue
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, item.strip(), URL, 'prose'))


# Parse Cicero - Chapters are bolded, subsections/verses are prefixed by unbracketed numbers.
def parsecase5(ptags, c, colltitle, title, author, date, URL):
    # ptags contains all <p> tags. c is the cursor object.
    chapter = 0
    verse = 0
    hasversenum = False
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
        if text.startswith("SallustThe"):
            continue
        potchap = p.find('b')
        if potchap is not None:
            chapter = potchap.find(text=True)
            text = text.replace(chapter,'')
        text = re.split('([0-3])\.\s', text)
        try: text.remove('')
        except: pass
        for item in text:
            if item is None or item.isspace():
                continue
            item = item.strip()
            if item.isnumeric():
                verse = item
                continue
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, item, URL, 'prose'))


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
    # The collection URL below. In this example, we have a link to Cicero.
    collURL = 'http://thelatinlibrary.com/sall.html'
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
        c.execute("DELETE FROM texts WHERE author='Sallust'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            # finally, pick ONE case to parse with.
            if title.endswith("Iugurthinum"):
                altparsecase2(getp, c, colltitle, title, author, date, url)
            elif title.endswith("Fragmenta"):
                altcase3(getp, c, colltitle, title, author, date, url)
            elif title.endswith("Cotta") or title.endswith("Pompey") or title.endswith("Macer")\
                    or title.endswith("Mithridates"):
                parsecase4(getp,c, colltitle, title, author, date, url)
            elif title.endswith("Cicero"):
                parsecase5(getp, c, colltitle, title, author, date, url)
            else:
                parsecase3(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
