import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger



def getBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com//index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com//index.html")
        textsURL.remove("http://www.thelatinlibrary.com//classics.html")
        textsURL.remove("http://www.thelatinlibrary.com//christian")
    logger.info("\n".join(textsURL))
    return textsURL

def getSermons(soup):
    siteURL = 'http://www.thelatinlibrary.com/augustine'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/augustine//index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/augustine//index.html")
        textsURL.remove("http://www.thelatinlibrary.com/augustine//classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/augustine//christian")
        textsURL.remove("http://www.thelatinlibrary.com/augustine//august.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/august.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "AUGUSTINE OF HIPPO"
    date = collSOUP.span.string.strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Augustine'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            if url.startswith("http://www.thelatinlibrary.com/augustine/iulianus1.shtml"):
                title = "CONTRA SECUNDAM IULIANI RESPONSIONEM LIBER PRIMUS"
            elif url.startswith("http://www.thelatinlibrary.com/augustine/iulianus2.shtml"):
                title = "CONTRA SECUNDAM IULIANI RESPONSIONEM LIBER SECUNDUS"
            else:
                try:
                    title = textsoup.title.string.split(':')[1].strip()
                except:
                    try:
                        title = textsoup.title.string.split(',')[1].strip()
                    except:
                        title = textsoup.find('p', class_='pagehead').string.strip()
            print(title)

            if title.startswith("Confessions"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if re.match("[0-9]+", pstring):
                        if " " in pstring:
                            heading = pstring.split(" ")[0]
                            pstring = pstring.split(" ")[1]
                            chapter = heading.split(".")[1].strip()
                            verse = heading.split(".")[2].strip()
                        else:
                            chapter = pstring.split(".")[1].strip()
                            verse = pstring.split(".")[2].strip()
                            continue

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v.startswith('commentary'):
                            # ignore an english note in there
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))

            elif title.startswith("SANCTI AUGUSTINI EPISTULA"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()
                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))
            elif title.startswith("De Civitate Dei"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if re.match("\[", pstring):
                        # this is a chapter heading
                        chapter = pstring.split("]")[0].replace("[", "").strip()
                        verse = 0
                        pstring = pstring.split("]")[1].strip()

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("de Trinitate"):
                getp = textsoup.find_all('p')
                chapter = "PROLOGUS"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        continue
                        # these headings are handled elsewhere

                    if re.match("\[", pstring):
                        # this is a heading
                        heading = pstring.split("]")[0].replace("[", "").strip()
                        if re.match("[IVXL]+", heading):
                            # this is a chapter and verse heading
                            try:
                                chapter = re.split(" ", heading)[0].strip()
                                verse = re.split(" ", heading)[1].strip()
                            except:
                                verse = heading
                        else:
                            verse = heading

                        pstring = pstring.split("]")[1].strip()

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("CONTRA SECUNDAM IULIANI RESPONSIONEM"):
                getp = textsoup.find_all('p')
                chapter = "PRAEFATIO"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    # does this leave numbers in the text from footnote links?
                    pstring = pstring.strip()

                    if p.find('br') is not None:
                        # skip footnotes - not sure about this?
                        continue

                    # used bolded headings as chapters
                    # left numbers in text
                    # can be changed if neccesary

                    if p.find('b') is not None:
                        if pstring.startswith("PRAEFATIO") or pstring.startswith("LIBER"):
                            continue
                            # these headings are handled elsewhere
                        else:
                            chapter = pstring
                            verse = 0
                            continue

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("de Dialectica"):
                getp = textsoup.find_all('p')
                chapter = 0
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    verses = []
                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if re.match("[IVXL]+", pstring):
                        # this is a chapter heading
                        chapter = pstring.split(".")[0].strip()
                        verse = 0
                        pstring = pstring.split(".")[1].strip()

                    verses.append(pstring)

                    for v in verses:
                        if v.startswith('Augustine'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("de Fide"):
                # verses are split across chapter headings, so they get double entered
                # e.g. there are two verse 21s, one in Caput IX and one in Caput X
                getp = textsoup.find_all('p')
                chapter = "-1"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        chapter = pstring
                        continue

                    lines = re.split("([0-9]+\.)", pstring)
                    for l in lines:
                        if re.match("[0-9]", l):
                            verse += 1
                            continue
                        if l.startswith('Augustine'):
                            continue
                        if l is None or l == '' or l.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, l.strip(), url, 'prose'))

            elif title.startswith("de Catechizandis"):

                getp = textsoup.find_all('p')
                chapter = "-1"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        chapter = p.find('b').string.strip()
                        pstring = pstring.replace(chapter, "").strip()

                    lines = re.split("([0-9]+\.)", pstring)
                    for l in lines:
                        if re.match("[0-9]", l):
                            verse += 1
                            continue
                        if l.startswith('Augustine'):
                            continue
                        if l is None or l == '' or l.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, l.strip(), url, 'prose'))

            elif title.startswith("REGULA SANCTI AUGUSTINI"):
                getp = textsoup.find_all('p')
                chapter = "-1"
                verse = 0

                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation', 'citation']:  # these are not part of the main t
                            continue
                    except:
                        pass

                    pstring = p.get_text()
                    pstring = pstring.strip()

                    if p.find('b') is not None:
                        chapter = pstring
                        continue

                    lines = re.split("([0-9]+\.)", pstring)
                    for l in lines:
                        if re.match("[0-9]", l):
                            verse += 1
                            continue
                        if l.startswith('Augustine'):
                            continue
                        if l is None or l == '' or l.isspace():
                            continue

                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, l.strip(), url, 'prose'))

            else:
                sermons = getSermons(textsoup)
                # these are the Sermons, which have their own page of links
                for s in sermons:
                    sermonurl = urllib.request.urlopen(s)
                    sermonsoup = BeautifulSoup(sermonurl, 'html5lib')

                    title = sermonsoup.title.string.split(':')[1].strip()
                    print(title)
                    getp = sermonsoup.find_all('p')
                    chapter = "-1"
                    verse = 0

                    for p in getp:
                        try:
                            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                         'internal_navigation', 'citation']:  # these are not part of the main t
                                continue
                        except:
                            pass

                        verses = []
                        pstring = p.get_text()
                        pstring = pstring.strip()
                        verses.append(pstring)

                        for v in verses:
                            if v.startswith('Augustine'):
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
