import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger

#

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


def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/liberpontificalis.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = 'no date found'
    textsURL = getBooks(collSOUP)

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')

        c.execute("DELETE FROM texts WHERE title = 'Liber Pontificalis'")
        c.execute("DELETE FROM texts WHERE title = 'Catalogue Libérien'")
        c.execute("DELETE FROM texts WHERE title = 'Fragmentum Laurentianum'")
        c.execute("DELETE FROM texts WHERE title = 'Epitome Feliciana'")
        c.execute("DELETE FROM texts WHERE title = 'Epitome Cononiana'")


        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            title = textsoup.title.string.strip()
            print(title)
            chapter = -1
            verse = 0

            if title.startswith("Liber"):
                date = textsoup.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
                chapter = "Preface"
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
                        print(chapter)
                        continue

                    verses = re.split("([0-9]+\s)", text)

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        if len(v) < 10:
                            continue
                            # this is a stray punctuation mark or something
                        if chapter == "XI. PIVS":  # leave numbers in on this chapter
                            if v.startswith("Pius"):
                                v = "1 Pius, natione Italus, ex patre Rufino, frater Pastoris, de ciuitate Aquilegia, sedit ann. XVIIII m. IIII d. III. Fuit autem temporibus Antonini Pii, a consolatu Clari et Seueri (146)."
                            elif v.startswith("Sub"):
                                v = "2 Sub huius episcopatum Hermis librum scripsit in quo mandatum continet quod ei praecepit angelus Domini, cum uenit ad eum in habitu pastoris ; et praecepit ei ut Paschae die dominico celebraretur."
                            elif v.startswith("Hic constituit"):
                                v = "3 Hic constituit hereticum uenientem ex Iudaeorum herese suscipi et baptizari ; et constitutum de ecclesia fecit. †"
                            elif v.startswith("Hic fecit"):
                                v = " 5 Hic fecit ordinationes V per mens. Decemb., presbiteros XVIIII, diaconos XXI ; episcopos per diuersa loca numero XII. Qui etiam sepultus est iuxta corpus beati Petri, in Vaticanum, V id. Iul. Et cessauit episcopatus dies XIIII."
                            else:
                                v = "† 4 Hic ex rogatu beate Praxedis dedicauit aecclesiam thermas Nouati, in uico Patricii, in honore sororis sue sanctae Potentianae, ubi et multa dona obtulit ; ubi sepius sacrificium Domino offerens ministrabat. Inmo et fontem baptismi construi fecit, manus suas benedixit et consecrauit ; et multos uenientes ad fidem baptizauit in nomine Trinitatis."

                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Catalogue"):
                date = textsoup.span.string.replace('(', '').replace(')', '').replace(u"\u2013", '-').strip()
                chapter = "-1"
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

                    verses.append(text)

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            elif title.startswith("Fragmentum"):
                date = 'no date found'
                chapter = "-1"
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []
                    brtags = p.findAll('br')
                    if brtags != []:
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
                    else:
                        text = p.get_text()
                        verses.append(text.strip())

                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        verse += 1
                        # verse number assignment.
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v.strip(), url, 'prose'))

            else:
                date = 'no date found'
                chapter = "Preface"
                getp = textsoup.find_all('p')
                for p in getp:
                    try:
                        if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                                     'internal_navigation']:  # these are not part of the main text
                            continue
                    except:
                        pass

                    verses = []
                    brtags = p.findAll('br')

                    text = p.get_text()
                    text = text.strip()

                    if brtags != []:
                        try:
                            firstline = brtags[0].previous_sibling.previous_sibling.strip()
                        except:
                            firstline = brtags[0].previous_sibling.strip()
                        verses.append(firstline)

                        for br in brtags:
                            try:
                                t = br.next_sibling.next_sibling.strip()
                            except:
                                t = br.next_sibling.strip()
                            if t is None or t == '' or t.isspace():
                                continue
                            verses.append(t)
                    elif re.match("[IVXL]+\.", text):
                        # this is a chapter heading
                        chapter = text.split(",")[0]
                        text = text.replace(chapter + ",", '')
                        verses.append(text)
                        verse = 0
                        print(chapter)
                    else:
                        verses.append(text)

                    for v in verses:
                        if v.startswith('Christian'):
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
