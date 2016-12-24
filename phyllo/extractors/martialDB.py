import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

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


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/martial.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Martial'")

        for url in textsURL:
            chapter = -1
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            title = title.replace('Martial','Liber') # book title corrections
            getp = textsoup.find_all('p')
            if url.endswith('mart14.shtml'):
                #isolate apophoreta
                for p in getp:
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
                        potchap = p.find('strong')
                        if potchap is not None:
                            chapter = potchap.find(text=True)
                            verse = 0
                            continue

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
                                   verse, v.replace('\n','').replace('\t',' ').replace('  ',' ').strip(), url, 'poetry'))
            else:
                for p in getp:
                    # make sure it's not a paragraph without the main text
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    brtags = p.findAll('br')

                    potchap = p.find('b')
                    if potchap is not None:
                        chapter = potchap.find(text=True)
                        # reset verse after every chapter
                        verse = 0
                        continue
                    else:
                        potchap = p.find('strong')
                        if potchap is not None:
                            chapter = potchap.find(text=True)
                            verse = 0
                            continue
                    # possible prose entry
                    text = p.get_text().strip()
                    if text.startswith('1.'):
                        passage = ''
                        text = p.get_text().strip()
                        if text.startswith("Martial\n"):
                            continue
                        # Skip empty paragraphs.
                        if len(text) <= 0:
                            continue
                        text = re.split('([IVX]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
                        for element in text:
                            if element is None or element == '' or element.isspace():
                                text.remove(element)
                        # chapter += 1
                        for count, item in enumerate(text):
                            if item is None:
                                continue
                            if item.isnumeric() or len(item) < 5:
                                verse = item
                            else:
                                passage = item
                                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                          (None, colltitle, title, 'Latin', author, date, chapter,
                                           verse, passage.strip(), url, 'prose'))
                        continue

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
                        verse = int(verse)
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v, url, 'poetry'))



if __name__ == '__main__':
    main()