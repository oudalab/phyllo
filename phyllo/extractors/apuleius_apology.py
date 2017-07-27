import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# A function to put entries in the table.
# Note that this table only contains Chapter, Verse, and Passage for testing purposes.
def inplace(collectiontitle, title, author, date, chapter, num, sentn, url, db):
    c = db.cursor()
    c.execute('INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)',
              (None, collectiontitle, title, 'Latin', author, date, chapter,
               num + 1, sentn, url, 'prose'))
    db.commit()


def main():
    # Obtain information from main apuleius page
    apulURL = 'http://www.thelatinlibrary.com/apuleius.html'
    apulURLopen = urllib.request.urlopen(apulURL)
    apulSoup = BeautifulSoup(apulURLopen, 'html5lib')

    author = apulSoup.title.contents[0].strip()
    collectiontitle = apulSoup.h1.contents[0].strip()
    date = apulSoup.h2.contents[0].strip().replace('(', '').replace(')', '').replace(u"\u2013", '-')

    # obtain soup
    url = "http://www.thelatinlibrary.com/apuleius/apuleius.apol.shtml"
    openurl = urllib.request.urlopen(url)
    soup = BeautifulSoup(openurl, "html5lib")

    # get book title
    title = soup.title.contents[0]
    title = [re.sub(r'^\s+', '', t) for t in title] # remove whitespace
    title = [re.sub(r'^\n', '', t) for t in title] # remove newline
    title = [re.sub(r'^\t', '', t) for t in title] #remove tabs
    title = ''.join(title)
    logger.info("Book: " + title)
    souptext = soup.get_text()

    # Split the text into two parts -- the main text and the apparatus
    split = re.split('Note', souptext)

    # Split the main text into chapters, denoted by [x] where x is some number.
    chapters = re.split('\[+([1-9]|[0-9][0-9]|[0-1][0-1][0-3])+\]', split[0])
    chapters = filter(lambda x: len(x) > 3, chapters)
    chapnum = -1

    with sqlite3.connect("texts.db") as db:
        cursor = db.cursor()
        db.commit()
        c.execute(
            'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
            ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
            ' link TEXT, documentType TEXT)')
        cursor.execute("DELETE FROM texts WHERE book = 'Apology'")

        # Go through each element in the list that was split by chapter
        for chap in chapters:
            chapnum += 1  # increment chapter number
            if chapnum == 0: # skip first line that is not part of the text.
                continue

            # Unnecessary conditional that needs to be removed.
            if chapnum > 251:
                logger.info("Entries placed.")
                break

            # Further split each chapter into sentences, denoted by (x) where x is some number.
            sentence = re.split('\(+([0-9]|[0-9][0-9])+\)', chap)
            # Get rid of useless empty entries
            sentence = filter(lambda x: len(x) > 3, sentence)
            verse = 0 # synonymous with sentence number for this collection

            # Loop trims the hedges and turns list objects into strings.
            for sent in sentence:
                verse = verse + 1
                sent = [re.sub(r'^\s+', '', t) for t in sent]  # remove whitespace
                sent = [re.sub(r'^\n', '', t) for t in sent]  # remove newline
                passage = ""
                for char in sent:
                    # Because the sentence is split by characters, .join() can't preserve word spacing.
                    if char == '':
                        passage += " "
                    passage += char
                inplace(collectiontitle, title, author, date, chapnum, verse, passage, apulURL, db)


if __name__ == '__main__':
    main()
