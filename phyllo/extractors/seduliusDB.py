import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# mostly finished, except for a problem w line numbers in the last poem

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
    collURL = 'http://www.thelatinlibrary.com/sedulius.html'
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

        c.execute("DELETE FROM texts WHERE author = 'Sedulius'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.split(":")[1].strip()
            print(title)
            chapter = -1
            verse = 0

            if title.startswith("Carmen"):
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

                    if url == "http://www.thelatinlibrary.com/sedulius5.html":
                        title = "Carmen Paschale V"
                        # fix a typo in one of the titles

                    if text.startswith("Christian Latin"):
                        continue

                    if p.find('b') is not None:
                        chapter = text
                        continue

                    brtags = p.findAll('br')
                    verses = []
                    try:
                        try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.strip()
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
                        # remove in-text line numbers
                        if text.endswith(r'[0-9]+'):
                            try:
                                text = text.split(r'[0-9]')[0].strip()
                            except:
                                pass
                        verses.append(text)

                    for v in verses:
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'poetry'))

            else:
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

                    lines = re.split("\n", text)
                    for l in lines:
                        l = l.strip()
                        if re.search('[0-9]', l):
                            # remove in-text line numbers
                            l = re.split('[0-9]', l)[0].strip()
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
                                   verse, v.strip(), url, 'poetry'))

if __name__ == '__main__':
    main()
