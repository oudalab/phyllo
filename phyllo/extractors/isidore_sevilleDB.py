import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# seems to work fine
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
    collURL = 'http://thelatinlibrary.com/isidore.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = collSOUP.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()

        c.execute("DELETE FROM texts WHERE author = 'Isidore of Seville'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()
            print(title)
            chapter = -1
            verse = 0


            if title.startswith("Etymologiae"):
                # add the title to the book number
                try:
                    title = title + ": " + textsoup.find('b').string.strip()
                    print(title)
                except:
                    pass
                getp = textsoup.find_all('p')
                textstr = ''
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    text = p.get_text()
                    text = text.strip()

                    if re.match("[IVXL]+\.", text):
                        # this is a chapter heading
                        verses = re.split('\[[0-9]+\]', textstr)
                        chapter = verses[0]
                        verses.remove(chapter)
                        for v in verses:
                            if v is None or v == '' or v.isspace():
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))
                        textstr = ''
                        verse = 0

                    textstr = textstr + " " + p.get_text()
                verses = re.split('\[[0-9]+\]', textstr)
                chapter = verses[0]
                verses.remove(chapter)
                for v in verses:
                    if v is None or v == '' or v.isspace():
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))



            # does things a bit differently to handle verses split across paragraphs

            elif title.startswith("Sentientiae"):
                chapter = 0
                verse = 0
                getp = textsoup.find_all('p')
                textstr = ''
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass
                    text = p.get_text()
                    text = text.strip()

                    if text.startswith("Isidore"):
                        continue

                    brtags = p.find_all('br')

                    if brtags == []:
                        chapter = text
                        continue

                    else:
                        verses = []
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
                            # remove in-text line numbers
                            if re.match("[IVXL]+\.", text):
                                #this is a chapter heading so we will process the previous chapter
                                for v in verses:
                                    if v is None or v == '' or v.isspace():
                                        continue
                                    if v.startswith('Incipit'):
                                        continue
                                    if v.startswith('Explicit'):
                                        continue
                                    # leave out book markings b/c the title field handles these
                                    # verse number assignment.
                                    verse = v.split(" ")[0].strip()
                                    v = v.replace(verse, "").strip()

                                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                              (None, colltitle, title, 'Latin', author, date, chapter,
                                               verse, v.strip(), url, 'prose'))

                                chapter = text
                                verses = []
                                continue
                            else:
                                if text in verses:
                                    continue
                                else:
                                    verses.append(text)

                    textstr = textstr + " " + p.get_text()
            else:
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []
                    text = p.get_text()
                    text = text.strip()


                    if text.startswith("Prologus") or text.startswith("INCIPIT") or text.startswith("Suevorum"):
                        chapter = text
                        continue
                    else:
                        verse = text.split(" ")[0].strip()
                        text = text.replace(verse, "").strip()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('of Seville'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
