import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# lists of books that are formatted similarly
titles1 = ['Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah',
           'Haggai', 'Zacharias', 'Malachias', 'Prayer of Manasses', 'First Book of Macabees',
           'Second Book of Macabees', 'First Book of Esdras', 'Second Book of Esdras']
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
    collURL = 'http://thelatinlibrary.com/bible.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "various authors"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(":")[1].strip()
            except:
                title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0


            if title.startswith("The Bible"):
                title = "PROLOGI SANCTI HIERONYMI IN BIBLIA SACRA"
                c.execute("DELETE FROM texts WHERE title = '" + title + "'")
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

                    if text.startswith("INCIPIT"):
                        chapter = text
                        verse = 0
                        continue

                    verses.append(text)

                    for v in verses:
                        if v.startswith('The Bible'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Psalms"):
                c.execute("DELETE FROM texts WHERE title = '" + title + "'")
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

                    if p.find('b') is not None:
                        chapter = text
                        verse = 0
                        continue

                    verses = re.split('[0-9]+', text)   # make sure this works with the BR tags

                    for v in verses:
                        if v.startswith('The Bible'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))



            elif title.startswith("Daniel"):
                c.execute("DELETE FROM texts WHERE title = '" + title + "'")
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                # headings are treated as text with chapter = -1, verse = 0
                # Dr. Huskey told me to treat headings as text here.

                brtags = p.findAll('br')
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
                    if text.startswith("et") or text.startswith("laud") or text.startswith("Quia") or text.startswith("quoniam"):
                        # a 2 line verse we gotta put into one verse
                        lastVerse = verses[len(verses) - 1]
                        verses.remove(lastVerse)
                        newVerse = lastVerse + "\n" + text
                        verses.append(newVerse)
                    elif text in verses:
                        continue
                    else:
                        verses.append(text)

                for v in verses:
                    if v.startswith('The Bible'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    # verse/chapter assignment.
                    if re.match('[0-9]+:[0-9]+', v):
                        chapter = v.split(":")[0]
                        v = v.replace(chapter + ":", '')
                        verse = v.split(" ")[0]
                        v = v.replace(verse, '')
                    else:
                        chapter = -1
                        verse = 0

                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))


            elif title in titles1:
                c.execute("DELETE FROM texts WHERE title = '" + title + "'")
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

                    if p.find('b') is not None:
                        chapter = p.find('b').string.strip()
                        text = text.replace(chapter, '')
                        verse = 0

                    verses = re.split('[0-9]+', text)  # make sure this works with the BR tags

                    for v in verses:
                        if v.startswith('The Bible'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))



            else:
                c.execute("DELETE FROM texts WHERE title = '" + title + "'")
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

                    if re.match("\[[0-9]+\]", text):
                        text = text.replace(text.split(" ")[0], "")
                        chapter += 1
                        verse = 0

                    verses = re.split('[0-9]+', text)

                    for v in verses:
                        if v.startswith('The Bible'):
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
