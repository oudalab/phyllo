
import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo_logger import logger


# predefine functions credit: sarah otts
def add_to_database(verse_entries, db):
    logger.info("Adding {} entries to the database".format(len(verse_entries)))
    curs = db.cursor()
    #Replaces all available entries of Claudius with new entries.
    curs.execute("DELETE FROM texts WHERE author='Claudian'")
    for i, v in enumerate(verse_entries):
        curs.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                     (None, v["title"], v["book"], "Latin", v["author"], v["date"], v["chapter"], v["verse"],
                      v["text"], v["link"], "poem"))



def add_entry_to_list(entries, title, book, author, date, chapter, verse, text, txturl):
    entry_dict = {"title": title, "book": book, "author": author, "date": date,
                  "chapter": chapter, "verse": verse, "text": text, "link": txturl}
    entries.append(entry_dict)


def get_verses(soup):  # credit: Sarah Otts
    #Return an empty array when there is nothing in the paragraph.
    if len(soup.contents) == 0:
        return None

    #Poems have multiple line breaks (br). Each line is a verse.
    if (len(soup.findAll('br')) > 0):

        #i-tags are unnecessary as we just need the text.
        for i in soup.findAll('i'):
            i.unwrap()

        # find the lines between breaks
        all_br = soup.findAll('br')
        verses = [all_br[0].previous_sibling]  # the first line

        # lines after each break
        for br in all_br:
            if (br.next_sibling == "\n"):
                verses.append(br.next_sibling.next_sibling)
            else:
                verses.append(br.next_sibling)

        # remove unwanted characters and wackadoo elements
        for v in verses:
            if not isinstance(v,str):
                verses.remove(v)
        verses = [re.sub(r'^\s+', '', v) for v in verses]
        verses = [v.replace('\n', '') for v in verses]
        verses = [v.replace(u'\xa0', '') for v in verses]  # remove unprintable character
        return verses


def get_name_and_author_of_book(soup, url):  # credit: Sarah Otts
    # attempt to get it from the page title
    book = ""
    author = ""
    if soup.title:
        pagetitle = soup.title.string
        split_title = pagetitle.split(":")
        if len(split_title) >= 2:
            author = split_title[0]
            book = split_title[-1]

    #Otherwise, author is in the pagetitle, and book in the next p-tag.
        else:
            author = pagetitle
            book = soup.p.br.next_sibling

    # remove any surrounding spaces
    book = re.sub(r"^\s+|\s+$|\n", '', book)
    author = re.sub(r"^\s+|\s+$|\n", '', author)

    return [book, author]


def get_title_and_date(soup):  # credit: Sarah Otts
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
    title = title.upper() #uppercase to maintain Latin convention

    return [title, date]


def main():
    # collection name: Statius
    claudURL = 'http://www.thelatinlibrary.com/claudian.html'
    siteURL = 'http://www.thelatinlibrary.com'
    claudOpen = urllib.request.urlopen(claudURL)
    soup = BeautifulSoup(claudOpen, "html5lib")
    textsURL = []
    #Find links to each work in the collection from the soup.
    for a in soup.find_all('a', href=True):
        link = a['href']
        textsURL.append("{}/{}".format(siteURL, a['href']))
    # remove some unnecessary urls
    while ("http://www.thelatinlibrary.com/index.html" in textsURL):
        textsURL.remove("http://www.thelatinlibrary.com/index.html")
        textsURL.remove("http://www.thelatinlibrary.com/classics.html")

    logger.info("\n".join(textsURL))

    # extract data
    title_dict_claud, date_dict_claud = get_title_and_date(soup)
    verses = []
    for work in textsURL:
        workURL = urllib.request.urlopen(work)
        soup = BeautifulSoup(workURL, "html5lib")
        book, author = get_name_and_author_of_book(soup, workURL)
        date = date_dict_claud
        # go through text to find chapters
        para = soup.findAll('p')[:-1]

        #Default values; unlike most poems, Claudian poems have chapters.
        chapter = "1"
        verse = 0
        text = ""

        for p in para:

            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead',
                                             'shortborder', 'smallboarder',
                                             'margin', 'internal_navigation']:  # these are not part of the main text
                    continue
            except:
                pass

            chap_found = False
            potential_chap = p.find('b')
            if potential_chap is not None:
                chapter = potential_chap.find(text=True)
                # Include italicized part in chap name
                italic = potential_chap.i
                if italic is not None:
                    chapter += italic.string
                chapter = chapter.replace("\n", "")
                chapter = chapter.replace(u'\xa0', '')
                chapter = chapter.title()  # title case
                verse = 0
                continue
            # go through text to find verses
            if (get_verses(p)):
                for i, t in enumerate(get_verses(p)):
                    verse += 1
                    text = t

                    #The commented line probably worked for Python 2.
                    # text = unicode.encode(text, errors="ignore")

                    # add the entry
                    add_entry_to_list(verses, title_dict_claud, book, author,
                                      date, chapter, verse, text, work)
    # with statements automatically close the database
    with sqlite3.connect('texts.db') as db:
        curs = db.cursor()
        # create the database
        curs.execute(
            'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
            ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
            ' link TEXT, documentType TEXT)')
        db.commit()
        # put it all in the db
        add_to_database(verses, db)
        db.commit()

    logger.info("Process finished")


if __name__ == '__main__':
    main()
