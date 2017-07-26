import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# this works
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
    collURL = 'http://thelatinlibrary.com/notitia.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'Notitia Dignitatum'")
        c.execute("DELETE FROM texts WHERE title = 'NOTITIA DIGNITATUM\nIN PARTIBUS OCCIDENTIS'")
        c.execute("DELETE FROM texts WHERE title = 'NOTITIA DIGNITATUM\nIN PARTIBUS ORIENTIS'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.find('p').get_text()
            title = title.strip()
            chapter = -1
            verse = 0

            getp = textsoup.find_all('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                brtags = p.findAll('br')
                verses = []
                if brtags == []:
                    textstr = p.get_text()
                    if textstr.startswith("The"):
                        continue  # ignore links at the end
                    else:
                        chapter_f = p.find('b')
                        if chapter_f is not None:
                            chapter = chapter_f.string.strip()
                            verse = 0
                            continue
                        else:
                            text = p.get_text()
                            verses.append(text.strip())
                else:
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

                for v in verses:
                    if v.startswith("The"):
                        continue  # ignore links at the end
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter.strip(),
                               verse, v.strip(), url, 'prose'))



if __name__ == '__main__':
    main()
