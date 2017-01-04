import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

def parsecase3(ptags, c, colltitle, title, author, date, URL):
    chapter = -1
    verse = -1
    for p in ptags:
        try:
            if p['class'][0].lower() in ['pagehead']:
                ptitle = p.get_text().strip()
                if 'LIBER POS' in ptitle:
                    title = 'Liber Posterior'
                elif 'LIBER PR' in ptitle:
                    title = 'Liber Prior'
                continue
        except:
            pass
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass
        passage = ''
        text = p.get_text().strip()
        # Skip empty paragraphs.
        if len(text) <= 0:
            continue
        # split the text by section.
        text = re.split('\[([0-9]+)\]\s', text)
        for item in text:
            if item is None:
                continue
            item = item.strip()
            if item.isspace() or item == '' or item.startswith("Velleius\n"):
                continue
            if item.isnumeric():
                chapter = item
                continue
            else:
                # split by verse
                sent = re.split('([0-9]+)', item)
                for v in sent:
                    if v is None:
                        continue
                    v = v.strip()
                    if v.isspace() or v == '' or v.startswith("Velleius\n"):
                        continue
                    if v.isnumeric():
                        verse = v
                        continue
                    else:
                        passage = v
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, passage.strip(), URL, 'prose'))


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


# main code
def main():
    collURL = 'http://www.thelatinlibrary.com/vell.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = collSOUP.h1.string.strip()
    date = collSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author='Velleius Paterculus'")
        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            parsecase3(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
