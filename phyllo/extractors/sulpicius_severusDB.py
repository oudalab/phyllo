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
        textsURL.remove("http://www.thelatinlibrary.com/christian.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/sulpiciusseverus.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.title.string.strip()
    date = date = collSOUP.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        c.execute("DELETE FROM texts WHERE author = 'Sulpicius Severus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()
            print(title)

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

                text = p.get_text()
                text = text.strip()

                if text.startswith("LIBER"):
                    continue
                    # book headings handled elsewhere

                if text.startswith("Praefatio"):
                    chapter = text
                    continue


                lines = re.split("\([0-9]\)", text)
                if lines[0] is None or lines[0] == '' or lines[0].isspace():
                    pass
                else:
                    chapter = lines[0]
                    verse = 0
                    lines.remove(lines[0])
                    # work around chapter headings in different paragraphs

                for l in lines:
                    l = l.strip()
                    if l.startswith('Christian'):
                        continue
                    if l.startswith('The '):
                        continue
                    if l is None or l == '' or l.isspace():
                        continue
                    verses.append(l)

                for v in verses:
                    if v.startswith('Christian'):
                        continue
                    if v.startswith('The '):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    verse += 1
                    # verse number assignment.
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))


if __name__ == '__main__':
    main()
