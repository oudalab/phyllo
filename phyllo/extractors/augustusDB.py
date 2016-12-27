import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def parseRes2(getp, title, url, c, author, date, collectiontitle):
    chapter = '-'
    tabulacount = 0
    for p in getp:
        # make sure it's not a paragraph without the main text
        try:
            if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                         'internal_navigation']:  # these are not part of the main t
                continue
        except:
            pass

        if url == 'http://www.thelatinlibrary.com/resgestae.html':
            # chapters in Res Gestae 1 are surrounded by a tags
            ptext = p.get_text()
            potentialchap = p.find('a')
            if potentialchap is not None:
                chapter = potentialchap.find(text=True)
                ptext = re.split('\[[0-9]\]\s|\[[0-3][0-9]\]\s', ptext)
                ptext = ptext[1:]  # removes the section number from the text

            ptext = filter(lambda x: len(x) > 3, ptext)
            for num, sentn in enumerate(ptext):
                # This while block strips the paragraph of beginning spaces and dots leftover from the section number.
                while sentn.startswith(' ') or sentn.startswith('.'):
                    sentn = sentn[1:]
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num + 1, sentn, url, 'prose'))
        else:
            # chapters in Res Gestae II are by tablets, inside b or center tags
            ptext = p.get_text()
            ptext = ptext.strip() # remove newline characters and whatnot.
            if ptext == '':
                if tabulacount == 1: chapter = 'TABULA I'
                elif tabulacount == 2: chapter = 'TABULA II'
                elif tabulacount == 3: chapter = 'TABULA III'
                elif tabulacount == 4: chapter = 'TABULA IV'
                elif tabulacount == 5: chapter = 'TABULA V'
                elif tabulacount == 6: chapter = 'TABULA VI'
                tabulacount += 1
            elif ptext[:1].isdigit(): # for some reason, can't be split by number.
                num = ptext[0:2]
                sentn = ptext[3:]
                while num.endswith(' ') or num.endswith('.'):
                    num = num[:-1]
                while sentn.startswith(' ') or sentn.startswith('.'):
                    sentn = sentn[1:]
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
            elif ptext.startswith('App.'):
                ptext = re.split('(App.\sI{1,3}V{,1}.)\s', ptext)
                chapter = '-' # App. not associated with any chapter
                num = ptext[1] # the first element is an empty string.
                sentn = ptext[2].strip()
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num, sentn, url, 'prose'))
            else:
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           '-', ptext, url, 'prose'))

def main():
    # get proper URLs
    siteURL = 'http://www.thelatinlibrary.com'
    augURL = 'http://www.thelatinlibrary.com/aug.html'
    augOPEN = urllib.request.urlopen(augURL)
    augSOUP = BeautifulSoup(augOPEN, 'html5lib')
    textsURL = []

    for a in augSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    author = augSOUP.title.string
    author = author.strip()
    collectiontitle = augSOUP.h1.contents[0].strip()
    date = augSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Augustus'")
        for u in textsURL:
            uOpen = urllib.request.urlopen(u)
            gestSoup = BeautifulSoup(uOpen, 'html5lib')
            title = gestSoup.title.string.split(':')
            title = title[-1].strip()

            getp = gestSoup.find_all('p')[:-1]
            parseRes2(getp, title, u, c, author, date, collectiontitle)


if __name__ == '__main__':
    main()
