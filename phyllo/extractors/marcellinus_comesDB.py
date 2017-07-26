import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# seems ok to me

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
    collURL = 'http://thelatinlibrary.com/marcellinus.html'
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
        c.execute("DELETE FROM texts WHERE author = 'Marcellinus Comes'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = "CHRONICON: " + textsoup.find('span').get_text()
            title = title.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
            chapter = -1
            verse = 0

            if title.startswith("CHRONICON: Mommsen"):
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    brtags = p.findAll('br')
                    verses = []
                    textstr = p.get_text()
                    textstr = textstr.strip()

                    if p.find('b') is not None:
                        chapter = p.find('b').string.strip()
                        verse = 0
                        continue
                    # ignore some headings/links that aren't part of the text
                    elif (textstr.startswith("Medieval")):
                        continue
                    elif (textstr.startswith("CONTINVATIO ")):
                        continue
                    # handle an author's note
                    elif (textstr.startswith("ADDITAMENTVM")):
                        chapter = textstr
                        continue
                    elif not(textstr.startswith("(")):  # this is the preface
                        try:
                            try:
                                firstline = brtags[0].previous_sibling.strip()
                            except:
                                firstline = brtags[0].previous_sibling.previous_sibling.strip()
                            verses.append(firstline)
                        except:
                            verses.append(textstr)

                        for br in brtags:
                            try:
                                text = br.next_sibling.next_sibling.strip()
                            except:
                                text = br.next_sibling.strip()
                            if text is None or text == '' or text.isspace():
                                continue
                            verses.append(text)
                    elif p.find('i') is not None:
                        continue  # there's a note that isn't part of the text

                    else:
                        try:
                            try:
                                chapter = brtags[0].previous_sibling.strip()
                            except:
                                chapter = brtags[0].previous_sibling.previous_sibling.strip()
                            verse = 0
                        except:
                            pass

                        for br in brtags:
                            try:
                                text = br.next_sibling.next_sibling.strip()
                            except:
                                text = br.next_sibling.strip()
                            if text is None or text == '' or text.isspace():
                                continue
                            verselist = re.split('[0-9]+', text)
                            for v in verselist:
                                if v is None or v == '' or v.isspace():
                                    continue
                                verses.append(v.strip())

                    for v in verses:
                        if v.startswith('Medieval'):
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                chapter = "Praefatio"
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []

                    textstr = p.get_text()
                    textstr = textstr.strip()

                    if p.find('b') is not None:
                        continue
                    elif textstr.startswith('Medieval'):  # ignore links at the end
                        continue
                    elif not(textstr.startswith("(")):  # this is the preface
                        verses.append(textstr)
                    elif textstr.startswith("(A. C. 456."):  # this paragraph has a typo (missing ')') so we handle it separately
                        chapter = "(A. C. 456."
                        verse = 0
                        text = textstr.replace("(A. C. 456.", '')
                        verses.append(text.strip())
                    else:  # deal with the bulk of the text.
                        chapter = textstr.split(")")[0].replace('(',"").strip()
                        verse = 0
                        text = textstr.split(")")[1].strip()
                        verses.append(text)

                    for v in verses:

                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

if __name__ == '__main__':
    main()
