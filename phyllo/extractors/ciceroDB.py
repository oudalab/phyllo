import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def main():
# Case 1: Sections split by numbers (Roman or not) followed by a period, or bracketed. Subsections split by <p> tags
    def parsecase1(ptags, c, colltitle, title, author, date, URL):
        # ptags contains all <p> tags. c is the cursor object.
        chapter = '-1'
        verse = 1
        # entry deletion is done in main()
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            passage = ''
            text = p.get_text().strip()
            # Skip empty paragraphs.
            if len(text) <= 0 or text.startswith('Cicero\n'):
                continue
            if url.endswith('nd3.shtml'):  # isolate nd3 so we don't accidentally bug out the others
                text = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]|^\[([0-9]+)\]\s', text)
            else:
                text = re.split(
                    '^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s|^\[\s([0-9]+)\]|^\[([0-9]+)',
                    text)
            for element in text:
                if element is None or element == '' or element.isspace():
                    text.remove(element)
            # The split should not alter sections with no prefixed roman numeral.
            if len(text) > 1:
                i = 0
                while text[i] is None:
                    i+=1
                if chapter == 'FRAGMENTA':
                    verse = text[i]
                else:
                    chapter = text[i]
                i+=1
                while text[i] is None:
                    i+=1
                passage = text[i].strip()
                if chapter == 'FRAGMENTA':
                    pass
                else:
                    verse = 1
            else:
                passage = text[0]
                if chapter == 'FRAGMENTA':
                    pass
                else:
                    verse+=1
            if passage.startswith("Cicero"):
                continue
            if passage.startswith("FRAGMENTA"):
                chapter = 'FRAGMENTA'
                continue
            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                      (None, colltitle, title, 'Latin', author, date, chapter,
                       verse, passage.strip(), URL, 'prose'))


# Case 2: Sections are split by <p> tags and subsections by un/bracketed numbers.
    def parsecase2(ptags, c, colltitle, title, author, date, URL):
        # ptags contains all <p> tags. c is the cursor object.
        chapter = 0
        verse = '-1'
        # entry deletion is done in main()
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            passage = ''
            text = p.get_text().strip()
            if text.startswith("Cicero\n"):
                continue
            # Skip empty paragraphs.
            if len(text) <= 0:
                continue
            text = re.split('([IVX]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
            for element in text:
                if element is None or element == '' or element.isspace():
                    text.remove(element)
            chapter +=1
            for count, item in enumerate(text):
                if item is None:
                    continue
                if item.isnumeric() or len(item) < 5:
                    verse = item
                else:
                    passage = item
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, passage.strip(), URL, 'prose'))


# Case 3: Chapters separated by un/bracketed numbers, similarly to sentences.
    def parsecase3(ptags, c, colltitle, title, author, date, URL):
        chapter = '-1'
        verse = -1
        isnumeral = case3isNumeral(ptags)
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            passage = ''
            text = p.get_text().strip()
            # Skip empty paragraphs.
            if len(text) <= 0:
                continue
            text = re.split('([IVXL]+)\.\s|([0-9]+)\.\s|\[([IVXL]+)\]\s|\[([0-9]+)\]\s', text)
            for item in text:
                if item is None:
                    continue
                item = item.strip()
                if item.isspace() or item == '' or item.startswith("Cicero\n"):
                    continue
                if item.isdigit() and not isnumeral:
                    chapter = item
                elif item.isdigit() and isnumeral:
                    verse = item
                elif len(item) < 5 and isnumeral:
                    chapter = item
                else:
                    passage = item
                    # Remove brackets if they have been picked up.
                    if chapter.startswith('['):
                        chapter = chapter[:-1]
                        chapter = chapter[1:]
                    if passage.startswith('['):
                        passage = passage[:-1]
                        passage = passage[1:]
                    if passage == chapter:
                        continue
                    else: # chapter/passage correction
                        chaptertest = chapter + 'I'
                        chaptertest2 = chapter[:-2] + 'V'
                        chaptertest3 = chapter[:-3] + 'V'
                        chaptertest4 = chapter[:-4] + 'IX'
                        chaptertest5 = chapter[:-2] + 'X'
                        if (chapter == 'LXIX' or chapter == 'LXX') and passage == 'L':
                            continue
                        if passage == chaptertest or passage == chaptertest2 or passage == chaptertest3\
                                or passage == chaptertest4 or passage == chaptertest5:
                            chapter = passage
                            continue
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, colltitle, title, 'Latin', author, date, chapter,
                               verse, passage.strip(), URL, 'prose'))


# this function checks if the work uses Roman Numerals or numerical values for chapters.
    def case3isNumeral(ptags):
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            if p.get_text().strip() is None or p.get_text().strip() == '':
                continue
            firstp = p.get_text().strip()
            break
        firstp = re.split('^([IVX]+)\.\s|^([0-9]+)\.\s|^\[([IVXL]+)\]\s|^\[([0-9]+)\]\s', firstp)
        if firstp[0] is not None:
            if firstp[0].isdigit():
                return False
            else:
                return True
        elif firstp[1] is not None:
            if firstp[1].isdigit():
                return False
            else:
                return True
        elif firstp[2] is not None:
            if firstp[2].isdigit():
                return False
            else:
                return True


    def parsespecial(ptags, c, colltitle, title, author, date, URL):
        chapter = -1
        verse = -1
        isnumeral = case3isNumeral(ptags)
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallborder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            passage = ''
            if title.endswith('FONTEIO') or title.endswith('FLACCO'):
                potentialchap = p.find('I') # chapters italicized #always returns none for some reason.
                text = p.get_text()
                if text is None:
                    continue
                text = text.strip()
                if p.i is not None or p.center is not None: # this also is never true for some reason.
                    chapter = text
                    continue
                if potentialchap is not None:
                    potentialchap = None
                    chapter = p.get_text().strip()
                    continue
                else:
                    # read in verse number and passage
                    text = re.split('\[([0-9]+)\]', text)
                    for element in text:
                        if element is None:
                            continue
                        if element == '' or element.isspace():
                            continue
                        element = element.strip()
                        if element.isdigit():
                            verse = element
                        else:
                            passage = element
                            if passage.startswith("Cicero\n"):
                                continue
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, passage, URL, 'prose'))
            elif title.endswith('Paradoxica'):
                potentialchap = p.find('B') # chapters bolded

                if potentialchap is not None:
                    chapter = potentialchap.find(text=True)
                    continue
                else:
                    # read in verse number and passage
                    text = p.get_text()
                    if text is None:
                        continue
                    text = re.split('\[([0-9]+)\]', text)
                    for element in text:
                        if element is None:
                            continue
                        if element == '' or element.isspace():
                            continue
                        element = element.strip()
                        if element.isdigit():
                            verse = element
                        else:
                            passage = element
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, passage, URL, 'prose'))
            elif title.endswith('Partitione'):
                # chapter split by paragraph, verse by speaker
                text = p.get_text()
                if text is None:
                    continue
                text = text.strip()
                text = re.split('\[([0-9]+)\]', text)
                chaptext = ''
                for item in text:
                    if item.isspace() or item == '' or item is None:
                        continue
                    elif item.isnumeric():
                        chapter = item
                        continue
                    else:
                        chaptext += item
                        if item.startswith('Cicero\n'):
                            continue
                        try:
                            chaptext = re.split('\[([0-9]+)\]|(CICERO FILIUS)\.\s|(CICERO PATER)\.\s|(C\.F\.)\s|(C\.P\.)\s', chaptext)
                            for piece in chaptext:
                                if piece is None:
                                    continue
                                if piece == '' or piece.isspace():
                                    continue
                                piece = piece.strip()
                                if piece.startswith('CI') or piece.startswith("C."):
                                    verse = piece
                                    continue
                                elif piece.isnumeric():
                                    chapter = piece
                                else:
                                    passage = piece
                                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                              (None, colltitle, title, 'Latin', author, date, chapter,
                                               verse, passage, URL, 'prose'))
                        except:
                            c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                      (None, colltitle, title, 'Latin', author, date, chapter,
                                       verse, item.strip(), URL, 'prose'))


    # This case parses poetry
    def parsePoem(ptags, c, colltitle, title, author, date, url):
        chapter = -1
        verse = 0
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            # find chapter
            chapter_f = p.find('b')
            if chapter_f is not None:
                chapter = p.get_text().strip()
                verse = 0
                continue
            else:
                brtags = p.findAll('br')
                verses = []
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
            for v in verses:
                # verse number assignment.
                verse += 1
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v, url, 'poetry'))


    def getBooks(soup):
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


    # for nested hyperlinked works
    def altgetbook(soup):
        textsURL = []
        siteURL = "http://www.thelatinlibrary.com/cicero"
        # get links to books in the collection
        for a in soup.find_all('a', href=True):
            link = a['href']
            textsURL.append("{}/{}".format(siteURL, a['href']))

        # remove unnecessary URLs
        while ("http://www.thelatinlibrary.com/cicero//index.html" in textsURL):
            textsURL.remove("http://www.thelatinlibrary.com/cicero//index.html")
            textsURL.remove("http://www.thelatinlibrary.com/cicero//cic.html")
            textsURL.remove("http://www.thelatinlibrary.com/cicero//classics.html")
        logger.info("\n".join(textsURL))
        return textsURL


# main code
    siteURL = 'http://www.thelatinlibrary.com'
    ciceroURL = 'http://www.thelatinlibrary.com/cic.html'
    ciceroOpen = urllib.request.urlopen(ciceroURL)
    ciceroSOUP = BeautifulSoup(ciceroOpen, 'html5lib')
    author = ciceroSOUP.title.string.strip()
    colltitle = ciceroSOUP.h1.string.strip()
    date = ciceroSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    textsURL = getBooks(ciceroSOUP)

# pro ligario (case 1) needs to be moved to case 3
# pro Deitario is weird.
    caseOneList = ['http://www.thelatinlibrary.com/cicero/quinc.shtml',
                   'http://www.thelatinlibrary.com/cicero/imp.shtml',
                   'http://www.thelatinlibrary.com/cicero/murena.shtml',
                   'http://www.thelatinlibrary.com/cicero/sulla.shtml',
                   'http://www.thelatinlibrary.com/cicero/arch.shtml',
                   'http://www.thelatinlibrary.com/cicero/postreditum.shtml',
                   'http://www.thelatinlibrary.com/cicero/postreditum2.shtml',
                   'http://www.thelatinlibrary.com/cicero/cael.shtml',
                   'http://www.thelatinlibrary.com/cicero/piso.shtml',
                   'http://www.thelatinlibrary.com/cicero/marc.shtml',
                   'http://www.thelatinlibrary.com/cicero/lig.shtml',
                   'http://www.thelatinlibrary.com/cicero/deio.shtml',
                   'http://www.thelatinlibrary.com/cicero/fato.shtml',
                   'http://www.thelatinlibrary.com/cicero/brut.shtml',
                   'http://www.thelatinlibrary.com/cicero/acad.shtml',
                   'http://www.thelatinlibrary.com/cicero/amic.shtml',
                   'http://www.thelatinlibrary.com/cicero/compet.shtml'
                   ]
    caseTwoList = ['http://www.thelatinlibrary.com/cicero/sex.rosc.shtml',
                   'http://www.thelatinlibrary.com/cicero/rosccom.shtml',
                   'http://www.thelatinlibrary.com/cicero/caecina.shtml',
                   'http://www.thelatinlibrary.com/cicero/rabirio.shtml',
                   'http://www.thelatinlibrary.com/cicero/domo.shtml',
                   'http://www.thelatinlibrary.com/cicero/haruspicum.shtml',
                   'http://www.thelatinlibrary.com/cicero/balbo.shtml',
                   'http://www.thelatinlibrary.com/cicero/milo.shtml',
                   'http://www.thelatinlibrary.com/cicero/topica.shtml',
                     'http://www.thelatinlibrary.com/cicero/scauro.shtml'
                   ]
    caseThreeList = ['http://www.thelatinlibrary.com/cicero/cluentio.shtml',
                     'http://www.thelatinlibrary.com/cicero/plancio.shtml',
                     'http://www.thelatinlibrary.com/cicero/sestio.shtml',
                     'http://www.thelatinlibrary.com/cicero/vatin.shtml',
                     'http://www.thelatinlibrary.com/cicero/prov.shtml',
                     'http://www.thelatinlibrary.com/cicero/rabiriopost.shtml'
                     'http://www.thelatinlibrary.com/cicero/optgen.shtml',
                     'http://www.thelatinlibrary.com/cicero/orator.shtml',
                     'http://www.thelatinlibrary.com/cicero/senectute.shtml'
                     ]
    specialcases = ['http://www.thelatinlibrary.com/cicero/flacco.shtml',
                    'http://www.thelatinlibrary.com/cicero/fonteio.shtml',
                    'http://www.thelatinlibrary.com/cicero/paradoxa.shtml',
                    'http://www.thelatinlibrary.com/cicero/partitione.shtml'
                    ]
    getURLList = ['http://www.thelatinlibrary.com/cicero/legagr.shtml',
                  'http://www.thelatinlibrary.com/cicero/ver.shtml',
                  'http://www.thelatinlibrary.com/cicero/cat.shtml',
                  'http://www.thelatinlibrary.com/cicero/phil.shtml',
                  'http://www.thelatinlibrary.com/cicero/inventione.shtml',
                  'http://www.thelatinlibrary.com/cicero/oratore.shtml',
                  'http://www.thelatinlibrary.com/cicero/leg.shtml',
                  'http://www.thelatinlibrary.com/cicero/fin.shtml',
                  'http://www.thelatinlibrary.com/cicero/tusc.shtml',
                  'http://www.thelatinlibrary.com/cicero/nd.shtml',
                  'http://www.thelatinlibrary.com/cicero/divinatione.shtml',
                  'http://www.thelatinlibrary.com/cicero/off.shtml'
                  ]
    #notes: repub uses parenthesis instead of brackets; apparently there are two repub.shtml
    # leg is some kind of play
    # tusc has numbers by itself.
    # divinatione is truly a nightmare
    # caecilium, phillipic, oratore, milone and/or cluentio-oratio, plancio, sestio might/n't need a new case

    poemList = ['http://www.thelatinlibrary.com/cicero/repub.shtml']

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author='Cicero'")

        for url in getURLList:
            openu = urllib.request.urlopen(url)
            soup = BeautifulSoup(openu, 'html5lib')
            urltexts = getBooks(soup)
            for urlt in urltexts:
                openurl = urllib.request.urlopen(url)
                textsoup = BeautifulSoup(openurl, 'html5lib')
                try:
                    title = textsoup.title.string.split(':')[1].strip()
                except:
                    title = textsoup.title.string.strip()
                getp = textsoup.find_all('p')
                # url refers to the url of the collection's  collection. urlt is the url that the text/passages are found
                if url.endswith("legagr.shtml") or urlt.endswith("caecilium.shtml") or url.endswith("cat.shtml") \
                        or url.endswith('phil.shtml') or url.endswith('oratore.shtml') or urlt.endswith("fin1.shtml") \
                        or urlt.endswith('fin2.shtml') or urlt.endswith('fin3.shtml') \
                        or (url.endswith('nd.shtml') and not urlt.endswith('nd3.shtml')):
                    parsecase2(getp, c, colltitle, title, author, date, urlt)
                elif (url.endswith("ver.shtml") and not urlt.endswith('caecilium.shtml')) \
                        or url.endswith('inventione.shtml') or urlt.endswith('nd3.shtml') or url.endswith('off.shtml') \
                        or url.endswith('inventione.shtml') or url.endswith('leg.shtml') or url.endswith('tusc.shtml'):
                    parsecase1(getp, c, colltitle, title, author, date, urlt)
                elif urlt.endswith('fin4.shtml') or urlt.endswith('fin5.shtml') or url.endswith('divinatione.shtml'):
                    parsecase3(getp, c, colltitle, title, author, date, urlt)

        for url in textsURL:
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')
            try:
                title = textsoup.title.string.split(':')[1].strip()
            except:
                title = textsoup.title.string.strip()
            getp = textsoup.find_all('p')
            if url in caseOneList:
                parsecase1(getp, c, colltitle, title, author, date, url)
            elif url in caseTwoList:
                parsecase2(getp, c, colltitle, title, author, date, url)
            elif url in caseThreeList:
                parsecase3(getp, c, colltitle, title, author, date, url)
            elif url in specialcases:
                parsespecial(getp, c, colltitle, title, author, date, url)
            elif url in poemList:
                parsePoem(getp, c, colltitle, title, author, date, url)

    logger.info("Program runs successfully.")


if __name__ == '__main__':
    main()
