import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

def main():
    # sets the basic information and whatnot
    siteURL = 'http://www.thelatinlibrary.com'
    caesarURL = 'http://www.thelatinlibrary.com/caes.html'
    caesarOPEN = urllib.request.urlopen(caesarURL)
    caesarSOUP = BeautifulSoup(caesarOPEN, 'html5lib')
    # empty list to store URLs of Caesar's works.
    textsURL = []

    # get links to books in the collection
    for a in caesarSOUP.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))

    # remove unnecessary URLs
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    # basic information for the collection
    author = caesarSOUP.title.string
    author = author.strip()
    collectiontitle = caesarSOUP.h1.contents[0].strip()
    date = caesarSOUP.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
            ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
            ' link TEXT, documentType TEXT)')
        # clears out so that we can replace it later.
        c.execute("DELETE FROM texts WHERE author = 'Caesar'")
        title = ''
        # this loop then goes through individual works.
        for URL in textsURL:
            openURL = urllib.request.urlopen(URL)
            soup = BeautifulSoup(openURL, 'html5lib')
            try:
                title = soup.title.string.split(':')[-1].strip()
            except:
                pass
            # stores a bunch of instances where <p> tags were found. So pretty much each paragraph.
            ptags = soup.find_all('p')[:-1]
            # the following two are initialized early since they sometimes need to carry over
            # to the next <p> tag.
            chapter = '-1'
            sentence = '-1'
            for p in ptags:
                # make sure it's not a paragraph without the main text
                try:
                    # these classes of <p> don't contain any information we need, so we skip over them.
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:
                        continue
                except:
                    pass

                # chapters are surrounded by <a> tags
                potentialchapter = p.find('a')
                if potentialchapter is not None:
                    chapter = potentialchapter.find(text=True)
                    if chapter.endswith(']'): # some books have ']' inside the tag
                        chapter = chapter[:-1]
                    a = p.a.decompose() # removing it now makes splitting easier
                text = p.get_text().strip()
                if text.startswith('[]'): # gets rid of brackets outside the tag
                    text = text[2:].strip()
                elif text.startswith('['):
                    text = text[1:].strip()
                # Only the Bello Gallico is split in sentences. Others cannot be split by '.' due to abbreviations.
                text = re.split('([0-1][0-3][0-9])|([0-9][0-9])|([0-9])', text)
                # each unit is generally supposed to be what was split via regular expression
                for unit in text:
                    if unit is None or unit == '' or unit.isspace():
                        continue
                    unit = unit.strip()
                    if unit.isnumeric(): # applies to subsection number in Bellum Gallicum
                        sentence = unit
                        continue
                    else:
                        # one occasion where title was found in the header tag and not title tag.
                        if title == 'The Latin Library':
                            title = soup.h1.string.strip()
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, collectiontitle, title, 'Latin', author, date, chapter,
                                   sentence, unit, URL, 'prose'))


if __name__ == '__main__':
    main()
