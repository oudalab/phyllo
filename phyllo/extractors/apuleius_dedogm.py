import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

# scrapes information from a specific book in the collection
def infofetch(url, collectiontitle, author, date):
    openurl = urllib.request.urlopen(url)
    soup = BeautifulSoup(openurl, 'html5lib')

    # get book title
    title = soup.title.contents[0]
    title = [re.sub(r'\t', '', t) for t in title]
    title = [re.sub(r'\n', '', t) for t in title]
    title = ''.join(title)
    # parse text
    getp = soup.findAll('p')[:-1]
    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        # this program runs a few different titles in the collection, but not all.
        if url == 'http://www.thelatinlibrary.com/apuleius/apuleius.dog1.shtml':
            c.execute("DELETE FROM texts WHERE book = 'de Dogmate Platonis I'")
        elif url == 'http://www.thelatinlibrary.com/apuleius/apuleius.dog2.shtml':
            c.execute("DELETE FROM texts WHERE book = 'de Dogmate Platonis II'")
        elif url == 'http://www.thelatinlibrary.com/apuleius/apuleius.florida.shtml':
            c.execute("DELETE FROM texts WHERE book = 'Florida'")
        elif url == 'http://www.thelatinlibrary.com/apuleius/apuleius.mundo.shtml':
            c.execute("DELETE FROM texts WHERE book = 'de Mundo'")
        elif url == 'http://www.thelatinlibrary.com/apuleius/apuleius.deosocratis.shtml':
            c.execute("DELETE FROM texts WHERE book = 'de Deo Socratis'")

        chapter = '1' # initializes chapter
        for p in getp:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass

            # chapters are bold
            ptext = p.get_text()
            potential_chap = p.find('b')
            if potential_chap is not None:
                chapter = potential_chap.find(text=True)
                ptext = re.split('[IVX].\s', ptext)
                ptext = ptext[1:]  # removes the section number from the text
                ptext = ' '.join(ptext)

            # chop into verses (sentences)
            ptext = re.split('([.;?!])\s', ptext)

            #preserve the punctuation
            for i in range(0, len(ptext)-1):
                if len(ptext[i+1]) < 3:
                    ptext[i] = ptext[i] + ptext[i+1]

            ptext = filter(lambda x: len(x) > 3, ptext)
            for num, sentn in enumerate(ptext):
                # This while block strips the paragraph of beginning spaces and dots leftover from the section number.
                while sentn.startswith(' ') or sentn.startswith('.'):
                    sentn = sentn[1:]
                # fixes the first line of Florida.
                if sentn.startswith('ferme religiosis viantium') and chapter == 'I.':
                    sentn = 'Vt ' + sentn
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, collectiontitle, title, 'Latin', author, date, chapter,
                           num+1, sentn, url, 'prose'))


def main():
    urls = ['http://www.thelatinlibrary.com/apuleius/apuleius.dog1.shtml',
            'http://www.thelatinlibrary.com/apuleius/apuleius.dog2.shtml',
            'http://www.thelatinlibrary.com/apuleius/apuleius.florida.shtml',
            'http://www.thelatinlibrary.com/apuleius/apuleius.mundo.shtml',
            'http://www.thelatinlibrary.com/apuleius/apuleius.deosocratis.shtml']

    # Obtain information from main apuleius page
    apulURL = 'http://www.thelatinlibrary.com/apuleius.html'
    apulURLopen = urllib.request.urlopen(apulURL)
    apulSoup = BeautifulSoup(apulURLopen, 'html5lib')

    author = apulSoup.title.contents[0].strip()
    collectiontitle = apulSoup.h1.contents[0].strip()
    date = apulSoup.h2.contents[0].strip().replace('(','').replace(')','').replace(u"\u2013", '-')

    for link in urls:
        #try:
            infofetch(link, collectiontitle, author, date)
            logger.info("Fetched " + link)
        #except:
        #    logger.info("Failed to fetch " + link)
        #    pass
    logger.info("Process completed.")


if __name__ == '__main__':
    main()
