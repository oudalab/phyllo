# Ammianus writes in prose. Things will be a little different from Statius
import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# functions are mostly made by Sarah Otts
def add_to_database(verse_entries, db):
    logger.info("Adding {} entries to the database".format(len(verse_entries)))
    curs = db.cursor()
    #Replace old Ammianus entries with new ones to prevent duplications.
    curs.execute("DELETE FROM texts WHERE author='Ammianus'")
    for i, v in enumerate(verse_entries):
        data = curs.execute("SELECT * FROM texts")
        curs.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                     (None, v["title"], v["book"], "Latin", v["author"], v["date"],
                      v["chapter"], v["verse"], v["text"], v["link"], "prose"))


def add_entry_to_list(entries, title, book, author, date, chapter, verse, text, txturl):
    entry_dict = {"title": title, "book": book, "author": author, "date": date, "chapter": chapter,
                  "verse": verse, "text": text, "link": txturl}
    entries.append(entry_dict)


def get_verses(soup):
    # if there's nothing in the paragraph, return an empty array
    if len(soup.contents) == 0:
        return None
    # verses in prose is split by certain characters
    para_text = soup.get_text()

    verses = re.split('\[?[0-9]+[A-Z]?\]?|\[[ivx]+\]',
                      para_text)  # "[x]" can contain arabic numerals, lower case roman numerals, or upper case letters
    verses = [re.sub(r'^\s+', '', v) for v in verses]  # remove whitespace
    verses = [re.sub(r'^\n', '', v) for v in verses]  # remove \n
    verses = filter(lambda x: len(x) > 0, verses)

    # print verses
    return verses


def get_name_and_author_of_book(soup, url):
    # attempt to get it from the page title
    pagetitle = soup.title.string
    split_title = pagetitle.split(":")
    if len(split_title) >= 2:
        author = split_title[0]
        book = split_title[-1]

    # if that doesn't work, get the author from the page title and the next p-tag
    else:
        author = pagetitle
        book = soup.p.br.next_sibling

    # remove any surrounding spaces
    book = re.sub(r'^\s+|\s+$|\n', '', book)
    author = re.sub(r'^\s+|\s+$|\n', '', author)
    return [book, author]


def get_title_and_date(soup):
    title_soup = soup.find('h1')
    title = ""
    date = ""
    if title_soup != None:
        title = title_soup.string
    else:
        pagehead = soup.find('p', class_="pagehead")
        if (pagehead is not None):
            title = pagehead.find(text=True)
            if (pagehead.find('span') is not None):
                date = pagehead.find('span').string.replace("(", '').replace(")", '')
        else:
            h1 = soup.find('h1')
            title = h1.string
    if date is None or date == "":

        date_tag = soup.find('h2', class_='date')
        if (not date_tag is None):
            date = date_tag.find(text=True).replace('(', '').replace(')', '')
        else:
            date = ""

    date = date.replace(u"\u2013", '-')
    title = title.upper()

    return [title, date]


def main():
    # collection name: Ammianus
    ammaniusURL = 'http://www.thelatinlibrary.com/ammianus.html'
    siteURL = 'http://www.thelatinlibrary.com'
    ammaniusOpen = urllib.request.urlopen(ammaniusURL)
    soup = BeautifulSoup(ammaniusOpen, "html5lib")
    textsURL = []

    # search through Ammanius' soup for links to his works
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))
    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")
    logger.info("\n".join(textsURL))

    # extract data
    # get titles of Ammanius' collection
    title_dict_amm, date_dict_amm = get_title_and_date(soup)

    verses = []
    for work in textsURL:
        workURL = urllib.request.urlopen(work)
        soup = BeautifulSoup(workURL, "html5lib")
        book, author = get_name_and_author_of_book(soup, workURL)
        date = date_dict_amm
        # go through text to find chapters
        para = soup.findAll('p')[:-1]

        chapter = "1" #Note that chapters aren't integers.
        verse = 0
        text = ""

        for p in para:

            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder',
                                             'smallboarder', 'margin', 'internal_navigation']: #not in the main text
                    continue
            except:
                pass

            chap_found = False

            # in other books, chapters are bold or italicized
            potential_chap = p.find('b')

            # some Ammianus texts have italic chapters
            if potential_chap is None:
                potential_chap = p.find('i')

            if potential_chap is not None:
                chapter = potential_chap.find(text=True)

                # Include italicized part in chap name
                italic = potential_chap.i
                if italic is not None:
                    chapter += italic.string
                chapter = chapter.replace("\n", "")

                chapter = chapter.replace(u'\xa0', '')
                chapnum = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                           'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI'}
                if chapter in chapnum:
                    chapter = chapter.upper() #Roman numerals need to be uppercase
                else:
                    chapter = chapter.title()
                verse = 0
                continue
            # go through text to find verses
            if (get_verses(p)):
                for i, t in enumerate(get_verses(p)):
                    verse += 1
                    text = t
                    #The following line works in Python 2, but not here.
                    # text = unicode.encode(text, errors="ignore")

                    # add the entry
                    add_entry_to_list(verses, title_dict_amm, book, author, date, chapter,
                                      verse, text, work)

    with sqlite3.connect('texts.db') as db:
        # open cursor
        curs = db.cursor()
        # create the database if it doesn't already exist
        curs.execute(
            'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
            ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
            ' link TEXT, documentType TEXT)')
        db.commit()
        # put it all in the db
        add_to_database(verses,db)
        db.commit()

    logger.info("Process finished")


if __name__ == '__main__':
    main()