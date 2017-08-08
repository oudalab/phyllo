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
    collURL = 'http://thelatinlibrary.com/vegetius.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.p.string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Vegetius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.replace("Vegetius", "Epiroma Rei Militaris").strip()
            logger.info(title)
            chapter = -1
            verse = 0

            getp = textsoup.find_all('p')
            for p in getp:
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main text
                        continue
                except:
                    pass

                verses = []

                if p.find('br') is not None and chapter == -1:
                    # this is the chapter list.

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
                    pstring = p.get_text()
                    if pstring is None:
                        continue
                    pstring = pstring.strip()
                    # deal with nonstandard headings
                    if pstring.startswith("(XXVI. REGVLAE BELLORVM GENERALES)"):
                        chapter = "(XXVI. REGVLAE BELLORVM GENERALES)"
                        verse = 0
                        text = pstring.split(")")[1].strip()
                    elif pstring.startswith("(XXVIII.)"):
                        chapter = "(XXVIII.)"
                        verse = 0
                        text = pstring.split(")")[1].strip()
                    elif pstring.startswith("(XXVIIII.)"):
                        chapter = "(XXVIIII.)"
                        verse = 0
                        text = pstring.split(")")[1].strip()
                    elif pstring.startswith("(XVIII.)"):
                        chapter = "(XVIII.)"
                        verse = 0
                        text = pstring.split(")")[1].strip()
                    else:
                        try:
                            if p.find('br') is not None:
                                brtags = p.findAll('br')
                                try:
                                    try:
                                        firstline = brtags[0].previous_sibling.strip()
                                    except:
                                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                                    verses.append(re.split("[IVXL]+\.", firstline)[1].strip())
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
                                text = re.split("[IVXL]+\.", pstring)[1].strip()
                                verses.append(text)
                            chapter = pstring.split(".")[0].strip()
                            verse = 0
                        except:
                            text = pstring
                            verses.append(text)
                    logger.info(chapter)


                for v in verses:
                    if v.startswith('Vegetius'):
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
