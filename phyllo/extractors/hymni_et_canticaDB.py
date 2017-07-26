import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

titles = ['Veni, veni, Emmanuel', 'Puer nobis nascitur', 'Corde natus ex parentis', 'Quem pastores laudavere',
          'Angelus ad virginem', 'Personent hodie', 'Dormi, Jesu!', 'Qui creavit coelum', 'Adeste, fideles',
          'Gloria, laus et honor (Hymnus', 'Stabat mater dolorosa (Hymnus',
          'Chorus novae Ierusalem (Hymnus', 'O quanta, qualia (Hymnus de vita', 'Dies irae (Hymnus in']
titlelines = [ 'in die ramorum)', 'de passione)', 'in pascha)', 'aeterna)', 'exequiis)']
dates1 = ['12th century', '14th century']
dates2 = ['Trier, 15th century', 'Aurelius Clemens Prudentius, 4th century', 'John Francis Wade, 1711-1786', 'Thomas of Celano, fl.1215']
dates3 = ['Nunnery of St. Mary, Chester, ca. 1425', 'Theodulph, bishop of Orleans, 9th century', 'Fulbert, bishop of Chartres, d. 1028']
dates4 = ['Jacopone da Todi', 'Peter Abelard']
dates5 = ['(1230-1306)', '(1079-1142)']
def main():
    # The collection URL below.
    collURL = 'http://www.thelatinlibrary.com/hymni.html'
    collOpen = urllib.request.urlopen(collURL)
    collSOUP = BeautifulSoup(collOpen, 'html5lib')
    author = "unknown"
    colltitle = collSOUP.title.string.strip()
    date = "no date found"

    textsURL = [collURL]

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute(
        'CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY, title TEXT, book TEXT,'
        ' language TEXT, author TEXT, date TEXT, chapter TEXT, verse TEXT, passage TEXT,'
        ' link TEXT, documentType TEXT)')
        c.execute("DELETE FROM texts WHERE title = 'placeholder'")
        c.execute("DELETE FROM texts WHERE title = 'Veni, veni, Emmanuel'")
        c.execute("DELETE FROM texts WHERE title = 'Puer nobis nascitur'")
        c.execute("DELETE FROM texts WHERE title = 'Corde natus ex parentis'")
        c.execute("DELETE FROM texts WHERE title = 'Quem pastores laudavere'")
        c.execute("DELETE FROM texts WHERE title = 'Angelus ad virginem'")
        c.execute("DELETE FROM texts WHERE title = 'Personent hodie'")
        c.execute("DELETE FROM texts WHERE title = 'Dormi, Jesu!'")
        c.execute("DELETE FROM texts WHERE title = 'Qui creavit coelum'")
        c.execute("DELETE FROM texts WHERE title = 'Adeste, fideles'")
        c.execute("DELETE FROM texts WHERE title = 'Gloria, laus et honor (Hymnus in die ramorum)'")
        c.execute("DELETE FROM texts WHERE title = 'Stabat mater dolorosa (Hymnus de passione)'")
        c.execute("DELETE FROM texts WHERE title = 'Chorus novae Ierusalem (Hymnus in pascha)'")
        c.execute("DELETE FROM texts WHERE title = 'O quanta, qualia (Hymnus de vita aeterna)'")
        c.execute("DELETE FROM texts WHERE title = 'Dies irae (Hymnus in exequiis)'")


        for url in textsURL:
            chapter = "-1"
            verse = 0
            verses = []
            title = "placeholder"  # we set this later
            openurl = urllib.request.urlopen(url)
            textsoup = BeautifulSoup(openurl, 'html5lib')

            tables = textsoup.find_all('table')
            for t in tables:
                # all tables contain external links and/or redundant titles
                # therefore, we can safely remove them
                t.extract()

            text = textsoup.get_text()

            lines = re.split("\n", text)

            for l in lines:
                l = l.strip()
                # print(l)
                if l is None or l == '' or l.isspace():
                    continue
                elif l in titles:
                    for v in verses:
                        if v.startswith('Christian'):
                            continue
                        if v is None or v == '' or v.isspace():
                            continue
                        # verse number assignment.
                        verse += 1
                        c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                                  (None, colltitle, title, 'Latin', author, date, chapter,
                                   verse, v, url, 'poetry'))
                    verse = 0
                    verses = []
                    title = l
                    print(title)
                    continue
                elif l in titlelines:
                    title = title + " " + l
                    print(title)
                    continue
                elif l in dates1:
                    date = l
                    author = "unknown"
                    continue
                elif l in dates2:
                    author = l.split(",")[0].strip()
                    date = l.split(",")[1].strip()
                    continue
                elif l in dates3:
                    date = l.split(",")[2].strip()
                    l = l.replace(date, '')
                    author = l
                    continue
                elif l in dates4:
                    print("GOT ONE")
                    author = l
                    continue
                elif l in dates5:
                    print("GOT ANOTHER")
                    date = l
                    continue
                elif l.startswith("in the"):
                    date = "ca. 1360"
                    author = "unknown"
                    continue
                elif l.startswith("Latin copied"):
                    date = "no date found"
                    author = "Samuel Taylor Coleridge"
                    continue
                elif l.startswith("Fulbert, bishop of Chartres, d."):
                    author = "Fulbert, bishop of Chartres"
                    date = "d. 1028"
                    continue
                elif l.startswith("HYMNI ET CANTICA") or l.startswith("Latin Hymns") or l.startswith("1028"):
                    continue
                else:
                    verses.append(l)

            for v in verses:
                if v.startswith('Christian'):
                    continue
                if v is None or v == '' or v.isspace():
                    continue
                # verse number assignment.
                verse += 1
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, title, 'Latin', author, date, chapter,
                           verse, v, url, 'poetry'))

if __name__ == '__main__':
    main()
