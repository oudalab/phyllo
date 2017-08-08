import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


def main():
    siteURL = 'http://www.thelatinlibrary.com'
    catulURL = 'http://www.thelatinlibrary.com/catullus.shtml'
    catulOPEN = urllib.request.urlopen(catulURL)
    catulSOUP = BeautifulSoup(catulOPEN, 'html5lib')

    # basic information for the collection
    author = catulSOUP.title.string.strip()
    collectiontitle = catulSOUP.h1.contents[0].strip()
    date = '84 B.C. - 54 B.C.'

    ptags = catulSOUP.find_all('p')
    chapter = '-1'
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE author = 'Catullus'")
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass

            potential_chap = p.find('b')
            if potential_chap is not None:
                chapter = p.get_text().strip()
                continue
            else:
                text = p.get_text().strip()
                text = re.split('\n', text)
                text = filter(lambda x: len(x) > 0, text)
                for versenum, verse in enumerate(text):
                    verse = verse.strip()
                    c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                              (None, collectiontitle, '-', 'Latin', author, date, chapter,
                               versenum+1, verse, catulURL, 'poetry'))
                    # Dr. Huskey says that Catullus' collection is one, compiled work traditionally known as the 'Carmina.'
    logger.info('Database loaded.')

if __name__ == '__main__':
    main()
