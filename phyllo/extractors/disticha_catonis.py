import sqlite3
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup




def main():
    # The collection URL below.
    collURL = 'http://thelatinlibrary.com/cato.dis.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "Cato"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"


    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'Disticha Catonis'")
        # i went with title rather than author to avoid deleting entries for other authors named Cato

        for url in textsURL:
            chapter = "-1"
            verse = 0
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')



            getp = textsoup.find_all('p')

            for p in getp:
                # make sure it's not a paragraph without the main text
                try:
                    if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                                 'internal_navigation']:  # these are not part of the main t
                        continue
                except:
                    pass

                # find poem titles
                title_f = p.find('b')
                if title_f is not None:
                    title = p.get_text().strip()
                    verse = 0
                    chapter = "-1"
                    continue

                #find chapter numbers
                chaptext = p.get_text()
                chapter = chaptext.split(".")[0].strip()

                brtags = p.findAll('br')
                verses = []
                try:
                    try:
                        firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
                    try:
                        firstline = firstline.split(".")[1].strip()
                    except:
                        pass
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



if __name__ == '__main__':
    main()
