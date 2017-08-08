import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# lists of books that contain more links
haslinks = ['ad Nationes', 'ad Uxorem', 'de Cultu Feminarum', 'Adversus Marcionem']

# list of books formatted I. [1].... [2].... etc.
# or CAPUT 1. [1].....
# De Anima is a possible problem child - check this
# De Carne Christi - same problem - has text in span tags. idk if get_text() will catch theses
# we need to correct for verses split across paragraphs - see Leges for template code
# set default title to I. probably
# fix a wonky chapter name in de Pallio
# two books named de Oratione - the second is actually de Pudicitia
titles1 = ['ad Nationes I', 'ad Nationes II', 'Liber adversus Hermogenem', 'Adversus Iudaeos',
           'Adversus Praexean', 'Adversus Valentinianos', 'Apology', 'De Anima', 'de Baptismo',
           'de Carne Christi', 'Liber De Corona Militis', 'De Exhortatione Castitatis', 'De Fuga in Persecutione',
           'De Idololatria', 'Liber de Monogamia', 'de Oratione', 'de Pallio', 'De Paenitentia', 'De Patientia',
           'De Praescriptione Haereticorum', 'de Pudicitia', 'De Resurrectione Carnis',
           'de Virginibus Velandis', 'Scorpiace', 'Adversus Omnes Haereses', 'ad Uxorem I',
           'ad Uxorem II', 'De Cultu Feminarum I: DE HABITU MULIEBRI', 'De Cultu Feminarum II']

# list of books formatted CAP. I. 1. .... 2. ... etc.
# set default chapter to "-1"
titles2 = ['ad Scapulam', 'de Ieiunio', 'De Execrandis Gentium Diis']

# list of books formatted <b> Capitulum I</b> w verses in separate <p> tags
titles3 = ['Ad Martyres']

# list of books with chapter titles centered - has the potential to be a mess
# look at Eugippius Epistulae for help
titles4 = ['de Spectaculis', 'de Testimonio Animae']

# these have the first chapter not actually enclosed in a p tag.
# probably going to have to use soup.get_text(), split on chapters, then split on verses.
titles5 = ['Adversus Marcionem I', 'Adversus Marcionem II', 'Adversus Marcionem III', 'Adversus Marcionem IV', 'Adversus Marcionem V',]

# list of books that are poetry
titles6 = ['ad Senatorem', 'Carmen de Iona propheta', 'Carmen de Iudicio Domini', 'Carmen Genesis']


# list of books that need titles manually set (e.g. there are two ':' in the title, 2 part title, etc.]
# De Cultu Feminarum 1 and 2
# de Pudicitia
# ad Senatorem
# Carmen de Iona propheta
# Carmen de Iudicio Domini


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

def getSmallBooks(soup):
    siteURL = 'http://www.thelatinlibrary.com/tertullian'
    textsURL = []
    # get links to books in the collection
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/tertullian//index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/tertullian//index.html")
        textsURL.remove("http://www.thelatinlibrary.com/tertullian//tertullian.html")
        textsURL.remove("http://www.thelatinlibrary.com/tertullian//classics.html")
        textsURL.remove("http://www.thelatinlibrary.com/tertullian//christian.html")
    logger.info("\n".join(textsURL))
    return textsURL


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/tertullian.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = collSOUP.title.string.strip()
    colltitle = "Q. SEPTIMIVS FLORENS TERTVLLIANVS"
    date = collSOUP.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        c.execute("DELETE FROM texts WHERE author = 'Tertullianus'")

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            # set the titles
            try:
                title = textsoup.title.string.split("]")[1].strip()
            except:
                title = textsoup.title.string.split(":")[1].strip()
            # fix a few titles
            if url == "http://www.thelatinlibrary.com/tertullian/tertullian.cultu1.shtml":
                title = "De Cultu Feminarum I: DE HABITU MULIEBRI"
            elif url == "http://www.thelatinlibrary.com/tertullian/tertullian.cultu2.shtml":
                title = "De Cultu Feminarum II"
            elif url == "http://www.thelatinlibrary.com/tertullian/tertullian.pudicitia.shtml":
                title = 'de Pudicitia'
            print(title)
            chapter = -1
            verse = 0


            if title in haslinks:
                urls = getSmallBooks(textsoup)  # probably won't work
                for u in urls:
                    if u == "http://www.thelatinlibrary.com/tertullian.html":
                        continue
                    else:
                        textsURL.append(u)

            elif title in titles1:
                titles1.remove(title)
                chapter = "I."
                verse = 0
                verses = []
                textstr = ''
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

                    if re.match("[IVXL]+\.", text):
                        # reset chapter and verse at the next chapter
                        verses = re.split('\[[0-9]+\]', textstr)
                        for v in verses:
                            if v.startswith('Tertullian'):
                                continue
                            if v is None or v == '' or v.isspace():
                                continue
                            # verse number assignment.
                            verse += 1
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, v.strip(), url, 'prose'))
                        textstr = ''
                        chapter = text.split("[")[0].strip()
                        if chapter == "I. I.":
                            chapter = "I."  # fix a typo
                        text = text.replace(chapter, '')
                        verse = 0
                        verses = []
                        continue

                    textstr = textstr + " " + text

            elif title in titles2:

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

                    verses = re.split("[0-9]+\.", text)
                    if re.match("CAP", text):
                        chapter = verses[0].strip()
                        verse = 0
                        verses.remove(verses[0])

                    for v in verses:
                        if v.startswith('Tertullian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title in titles3:
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
                    if text.startswith('Tertullian'):
                        continue
                    verses = []

                    if p.find('b') is not None:
                        chapter = text
                        print(chapter)
                        verse = 0
                        continue

                    try:
                        text = text.split("]")[1].strip()  # remove in text verse numbers
                    except:
                        pass

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Tertullian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title in titles4:
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

                    findB = p.find('b')
                    if findB is not None:  # this may or may not work
                        print("FOUND A <B>")
                        chapter = text
                        print(chapter)
                        verse = 0
                        continue

                    verses = re.split('\[[0-9]+\]', text)

                    for v in verses:
                        if v.startswith('Tertullian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title in titles5:
                alltext = textsoup.get_text()
                text = alltext.split("2.")[0]
                verses = re.split('\[[0-9]+\]', text)
                chapter = "1."
                verse = 0
                verses.remove(verses[0])

                for v in verses:
                    if v.startswith('Tertullian'):
                        continue
                    if v is None or v == '' or v.isspace():
                        continue
                    # verse number assignment.
                    verse += 1
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, v.strip(), url, 'prose'))

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

                    verses = re.split('\[[0-9]+\]', text)
                    chapter = verses[0]
                    if chapter.startswith("etiam saecularis"):
                        # correct for a weird <p> break
                        chapter = "8"
                        verses.remove(verses[0])
                        verse = 3
                    else:
                        verse = 0
                        verses.remove(chapter)

                    for v in verses:
                        v = v.strip()
                        if v.startswith('Tertullian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        if v.startswith("Nam etsi per medios evasit"):
                            v = v + "\nTangere enim et tangi nisi corpus nulla potest res,\netiam saecularis sapientiae digna sententia est."
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))


            elif title in titles6:
                chapter = 0
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    ptext = p.get_text()
                    ptext = text.strip()

                    if ptext.startswith("Tertullian"):
                        continue
                    elif p.find('b') is not None:
                        chapter = text
                        verse = 0
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
                        # this should only throw an exception on links and headings - not actual text

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
                        if v.startswith('Tertullian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))
            else:
                pass # an extraneous URL


if __name__ == '__main__':
    main()
