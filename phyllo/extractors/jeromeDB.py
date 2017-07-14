import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# this is mostly good
# problem: it doesn't catch all of the verses in Epistulae
# no idea why really

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
        textsURL.remove("http://www.thelatinlibrary.com/christian.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/jerome.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "SANCTUS HIERONYMUS"
    date = collSOUP.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()

        c.execute("DELETE FROM texts WHERE author = 'Jerome'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(":")[1].strip()
            except:
                title = "Epistulae"
            print(title)
            chapter = -1
            verse = 0


            if title.startswith("Epistulae"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        print(chapter)
                        verse = 0
                        continue

                    else:
                        pstring = p.get_text()
                        pstring = pstring.strip()
                        lines = re.split("(\[[0-9]+\] | \[[0-9]+\.[0-9]+\])", pstring)
                        for l in lines:
                            if l.startswith('St. Jerome'):
                                continue
                            if l is None or l == '' or l.isspace():
                                continue
                            print("NEW ENTRY: " + l)
                            if len (l) < 10:
                                # this is a verse number
                                verse = l
                                print("THIS IS A VERSE")
                                continue
                            # verse number assignment.

                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, l.strip(), url, 'prose'))

            elif title.startswith("Life of Paul"):
                chapter = 0
                verse = 0
                verses = []
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    text = p.get_text()
                    text = text.strip()
                    verses = []

                    if re.match("\([0-9]+\)", text):
                        text = text.replace(text.split(" ")[0], "")
                        chapter += 1
                        verse = 0

                    verses.append(text)

                    for v in verses:
                        if v.startswith('St. Jerome'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))



            elif title.startswith("Life of Malchus"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []

                    chapter_f = p.find('b')
                    if chapter_f is not None:
                        chapter = chapter_f.string.strip()
                        verse = 0
                        continue
                    else:
                        pstring = p.get_text()
                        verses.append(pstring.strip())

                    for v in verses:
                        if v.startswith('St. Jerome'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                chapter = 0
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    text = p.get_text()
                    text = text.strip()
                    verses = []

                    brtags = p.find_all('br')

                    if brtags != []:
                        # these are the footnotes
                        chapter = "Footnotes"
                        verse = 0
                        try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.strip()
                        verses.append(firstline)

                        for br in brtags:
                            try:
                                text = br.next_sibling.next_sibling.strip()
                            except:
                                text = br.next_sibling.strip()
                            if text is None or text == '' or text.isspace():
                                continue
                            verses.append(text)

                    if re.match("[0-9]+\.", text):
                        text = text.replace(text.split(" ")[0], "")
                        chapter += 1
                        verse = 0

                    verses.append(text)

                    for v in verses:
                        if v.startswith('St. Jerome'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
