import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems to work fine
# should probably check on chapter divisions

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
        textsURL.remove("http://www.thelatinlibrary.com/misc.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/fulgentius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Fulgentius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            # this code handles all three books of Mitologarium b/c the chapter division scheme is very similar.
            if title.startswith("Mitologiarum"):

                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []
                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = p.get_text().strip()
                        verse = 0
                        continue
                    elif p.find('br') is not None:
                        brtags = p.findAll('br')
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
                    else:
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Fulgentius'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif(title.startswith("Expositio Sermonum Antiquorum")):
                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    text = text = p.get_text().strip()
                    # Skip empty paragraphs. and skip the last part with the collection link.
                    text = re.split('[0-9]+\.\s+', text)
                    try:
                        v = text[1].strip()
                    except:
                        v = text[0].strip()
                    if v.startswith('Fulgentius'):
                        continue
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v, url, 'prose'))
            else:
                getp = textsoup.find_all('p')
                chapter = -1
                verse = 0
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass
                    verses = []
                    if p.find('br') is not None:
                        brtags = p.findAll('br')
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
                    else:
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Fulgentius'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
