import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


def main():
    siteURL = 'http://www.thelatinlibrary.com'
    catoURL = 'http://www.thelatinlibrary.com/cato.html'
    catoOPEN = urllib.request.urlopen(catoURL)
    catoSOUP = BeautifulSoup(catoOPEN, 'html5lib')
    textsURL = []

    # get links to books in the collection
    for a in catoSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    # basic information for the collection
    author = catoSOUP.title.string.strip()
    collectiontitle = catoSOUP.h1.contents[0].strip()
    date = catoSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Cato the Elder'")
        title = ''
        for URL in textsURL:
            openURL = urllib.request.urlopen(URL)
            soup = BeautifulSoup(openURL, 'html5lib')
            title = soup.title.string.strip()
            ptags = soup.find_all('p')[:-1]
            chapter = '-1'
            sentence = 0
            for p in ptags:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                text = p.get_text().strip()
                passage = ''
                # two books are vastly different in formatting.
                if title == 'DE AGRI CVLTVRA':
                    sentence = sentence + 1
                    if text.startswith('['):
                        sentence = 1
                        text = re.split('\]\s', text)
                        chapter = text[0]
                        chapter = chapter[1:]
                        passage = text[1]
                    else:
                        passage = text
                    # split by sentence was not done due to abbreviations.

                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, collectiontitle, title, 'Latin', author, date, chapter,
                               sentence, passage, URL, 'prose'))
                else:
                    # Orationum Fragmenta
                    potential_chap = p.find('b')
                    if potential_chap is not None:
                        chapter = text
                        continue
                    else:
                        sentnumAvailable = False
                        sentence = '' # resets for each new p
                        for i in range(0,3):
                            sentence += text[i]
                            if sentence.endswith('.'):
                                sentence = sentence[:-1]
                            sentnumAvailable = True
                        if sentnumAvailable is True:
                            text = text.replace(sentence, '')
                            sentnumAvailable = False
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, collectiontitle, title, 'Latin', author, date, chapter,
                               sentence, text, URL, 'prose'))

if __name__ == '__main__':
    main()