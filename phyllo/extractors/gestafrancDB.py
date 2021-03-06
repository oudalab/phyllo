#http://www.thelatinlibrary.com/gestafrancorum.html
#prose

import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger


# functions are mostly made by Sarah Otts
def add_to_database(verse_entries, db):
    logger.info("Adding {} entries to the database".format(len(verse_entries)))
    curs = db.cursor()
    curs.execute("DELETE FROM texts WHERE author='Gesta Francorum'")
    for i, v in enumerate(verse_entries):
        data = curs.execute("SELECT * FROM texts")
        curs.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                     (None, v["title"], v["book"], "Latin", v["author"], v["date"], v["chapter"], v["verse"],
                      v["text"], v["link"], "prose"))


def add_entry_to_list(entries, title, book, author, date, chapter, verse, text, txturl):
    entry_dict = {"title": title, "book": book, "author": author, "date": date, "chapter": chapter, "verse": verse,
                  "text": text, "link": txturl}
    entries.append(entry_dict)


def get_verses(soup):
    # if there's nothing in the paragraph, return an empty array
    if len(soup.contents) == 0:
        return None

    para_text = soup.get_text()

    verses = re.split('\[?[0-9]+[A-Z]?\]?|\[[ivx]+\]',
                      para_text)  # "[x]" can contain arabic numerals, lower case roman numerals, or upper case letters
    verses = [re.sub(r'^\s+', '', v) for v in verses]  # remove whitespace
    verses = [re.sub(r'^\n', '', v) for v in verses]  # remove \n
    verses = filter(lambda x: len(x) > 0, verses)

    verses = [v for v in verses]
    # print verses
    return verses


def get_name_and_author_of_book(soup, url):
    # attempt to get it from the page title
    # print soup
    pagetitle = soup.title.string
    split_title = pagetitle.split(":")
    if len(split_title) >= 2:
        book = split_title[-1]

    # if that doesn't work, get the author from the page title and the
    else:
        book = soup.p.br.next_sibling

    # remove any surrounding spaces
    book = re.sub(r'^\s+|\s+$|\n', '', book)
    author = "Anonymous" #Gesta Francorum has an anonymous author.
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
    # collection name: Gesta Francorum
    gestaURL = 'http://www.thelatinlibrary.com/gestafrancorum.html'
    siteURL = 'http://www.thelatinlibrary.com'
    gestaMain = urllib.request.urlopen(gestaURL)
    soup = BeautifulSoup(gestaMain, "html5lib")
    textsUrl = []

    # search through soup for prose and links
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsUrl.append("{}/{}".format(siteURL, a['href']))
    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsUrl):
        textsUrl.remove("http://www.thelatinlibrary.com/index.html")
        textsUrl.remove("http://www.thelatinlibrary.com/classics.html")
        textsUrl.remove("http://www.thelatinlibrary.com/medieval.html")
    logger.info("\n".join(textsUrl))

    # extract data
    # get titles of this collection
    title_dict_ges, date_dict_ges = get_title_and_date(soup)

    verses = []
    for u in textsUrl:
        uURL = urllib.request.urlopen(u)
        soup = BeautifulSoup(uURL, "html5lib") # check pep 8 for file/fuction name
        book, author = get_name_and_author_of_book(soup, uURL)
        date = date_dict_ges
        # go through text to find chapters
        para = soup.findAll('p')[:-1]

        chapter = "1" #Note that chapters aren't integers.
        verse = 0
        text = ""

        for p in para:

            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass

            chap_found = False

            # in other books, chapters are bold or italicized
            potential_chap = p.find('b')

            if potential_chap is not None:
                chapter = potential_chap.find(text=True)

                # Include italicized part in chap name
                italic = potential_chap.i
                if italic is not None:
                    chapter += italic.string
                chapter = chapter.replace("\n", "")

                chapter = chapter.replace(u'\xa0', '')
                #Note: Some chapters have Roman numerals as part of the chapter name.
                #e.g. Roman numeral is only part of the string and is not capitalized. Needs fixing.
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

                    # text = unicode.encode(text, errors="ignore")

                    # add the entry
                    add_entry_to_list(verses, title_dict_ges, book, author, date, chapter, verse, text, u)

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
    main() #do thsi dunder thing for everything else
