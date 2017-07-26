import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# this is good to go

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
    collURL = 'http://thelatinlibrary.com/sidonius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "CAIUS SOLLIUS APOLLINARIS SIDONIUS"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Sidonius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()
            chapter = -1
            verse = 0
            if title.startswith("Epistularum"):
                getp = textsoup.find_all('p')
                verse = -1 # easiest way to keep verse numbering consistent with in-text numbers

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    text = p.get_text()
                    text = text.strip()

                    if text.startswith("EPISTULA"):
                        chapter = text
                        verse = -1  # easiest way to keep verse numbering consistent with in-text numbers
                        continue
                    elif text[0].isdigit():
                        verses.append(re.split('[0-9]+\.', text)[1].strip())
                        # this probably won't work but we can hope
                    else:
                        verses.append(text)

                    for v in verses:
                        if v.startswith("The Miscellany"):
                            continue  # ignore links at the end
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v, url, 'prose'))
            else:
                chap1 = ''
                chap2 = ''
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    textstr = p.get_text()
                    textstr = textstr.strip()
                    if textstr.startswith("CARMEN"):
                        chap1 = textstr
                        continue
                    elif p.find('br') is None or p.find('b') is not None:
                        chap2 = textstr
                        continue
                    else:
                        chapter = chap1 + ": " + chap2
                        verse = 0

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
                                text = br.next_sibling.strip()
                            except:
                                text = br.next_sibling.next_sibling.strip()
                            if text is None or text == '' or text.isspace():
                                continue
                            if text.endswith(r'[0-9]+'):
                                try:
                                    text = text.split(r'[0-9]')[0].strip()
                                except:
                                    pass
                            verses.append(text)

                        for v in verses:
                            if v.startswith('The Miscellany'):
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'poetry'))

if __name__ == '__main__':
    main()
