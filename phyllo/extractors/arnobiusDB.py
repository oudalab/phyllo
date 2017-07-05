import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

# good to go!

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
    collURL = 'http://www.thelatinlibrary.com/arnobius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "ARNOBIUS OF SICCA"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Arnobius of Sicca'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()

            getp = textsoup.find_all('p')
            chapter = 0
            verse = 0
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                if title.endswith("VII"):
                    # deal w VII weird chapters

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if re.match("[0-9]+\.[0-9]+\. | [0-9]+\.[0-9]+", pstring):
                        # this is a chapter heading
                        chapter = pstring.split(".")[0].strip()
                        print(chapter)
                        verse = 0
                    # manually assign chapters for some paragraphs with typos
                    elif pstring.startswith("1.1"):
                        # this is a chapter heading
                        chapter = "1"
                        print(chapter)
                        verse = 0
                    elif pstring.startswith(".16.1"):
                        # this is a chapter heading
                        chapter = "16"
                        print(chapter)
                        verse = 0
                    elif pstring.startswith("VII.17.1."):
                        # this is a chapter heading
                        chapter = "17"
                        print(chapter)
                        verse = 0
                    elif re.match("[0-9]+\s\[or\s[0-9]+\]\.", pstring):
                        chapter = pstring.split(".")[0].strip()
                        print(chapter)
                        verse = 0
                    else:
                        print(pstring)
                        # see what the chapter finder doesn't catch

                    lines = re.split("[0-9]+\.", pstring)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith("Christian Latin"):
                            continue
                        if len(l) < 12:
                            # get rid of chapter numbers at beginning of paragraphs
                            continue
                        if l.startswith("1 "):
                            l = l.replace("1 ", "")
                        verses.append(l.strip())

                    for v in verses:
                        if v.startswith('Christian Latin'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


                else:
                    # chapters are just divided by paragraphs here, so my life is easy
                    chapter += 1
                    verse = 0
                    verses = []

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    lines = re.split("[0-9]+\. | 19\s | 1\.1", pstring)
                    for l in lines:
                        if l is None or l == '' or l.isspace():
                            continue
                        if l.startswith("Christian Latin"):
                            continue
                        if len(l) < 10:
                            # get rid of chapter numbers at beginning of paragraphs
                            continue
                        # fix something that regex fails to catch
                        try:
                            l = l.replace("1.1", "")
                        except:
                            pass
                        verses.append(l.strip())

                    for v in verses:
                        if v.startswith('Christian Latin'):
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
