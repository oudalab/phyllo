
import sqlite3
import urllib
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from phyllo.phyllo_logger import logger

def main():
    siteURL = 'http://www.thelatinlibrary.com/enn.html'
    opensite = urllib.request.urlopen(siteURL)
    soup = BeautifulSoup(opensite, 'html5lib')

    author = 'Ennius'
    colltitle = 'QVINTVS ENNIVS'
    date = '239 - 169 B.C.'
    booktitle = soup.title.contents[0].strip()

    ptags = soup.find_all('p')
    chapter = -1
    verse = -1

    with sqlite3.connect('texts.db') as db:
        c = db.cursor()
        c.execute("DELETE FROM texts WHERE author = 'Ennius'")
        for p in ptags:
            # make sure it's not a paragraph without the main text
            try:
                if p['class'][0].lower() in ['border', 'pagehead', 'shortborder', 'smallboarder', 'margin',
                                             'internal_navigation']:  # these are not part of the main t
                    continue
            except:
                pass
            # find chapter
            chapter_f = p.find('b')
            if chapter_f is not None:
                chapter = p.get_text().strip()
                continue
            else:
                brtags = p.findAll('br')
                verses = []
                try:
                    try:
                        firstline = brtags[0].previous_sibling.strip()
                    except:
                        firstline = brtags[0].previous_sibling.previous_sibling.strip()
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
                if v.startswith('Excita cum tremulis'):
                    verse = 32
                elif v.startswith('Curantes magna'):
                    verse = 80
                elif v.startswith('Pectore diu'):
                    verse = 117
                elif v.startswith('Romulus in caelo'):
                    verse = 116
                elif v.startswith('Quis potis'):
                    verse = 173
                elif v.startswith('Navus repertus'):
                    verse = 178
                elif v.startswith('Aio te'):
                    verse = 174
                elif v.startswith('Nec mi aurum'):
                    verse = 186
                elif v.endswith('audite parumper,'):
                    verse = 200
                elif v.endswith('cum ingentibus signis.'):
                    verse = 205
                elif v.endswith('nec auro.'):
                    verse = 209
                elif v.startswith('scripsere alii'):
                    verse = 231
                elif v.startswith('Haece locutus'):
                    verse = 210
                elif v.startswith('postquam Discordia'):
                    verse = 258
                elif v.startswith('Pellitur e medio'):
                    verse = 263
                elif v.startswith('Additur orator Cornelius'):
                    verse = 300
                elif v.endswith('fortuna repente'):
                    verse = 313
                elif v.startswith('Insece Musa manu'):
                    verse = 322
                elif v.startswith('Egregie cordatus'):
                    verse = 326
                elif v.startswith('O Tite si'):
                    verse = 327
                elif v.startswith('Aspectabat virtutem'):
                    verse = 333
                elif v.startswith('Quae neque Dardaniis'):
                    verse = 349
                elif v.startswith('Concurrunt vel uti'):
                    verse = 430
                elif v.startswith('Undique conveniunt'):
                    verse = 409
                else:
                    verse += 1
                c.execute("INSERT INTO texts VALUES (?,?,?,?,?,?,?, ?, ?, ?, ?)",
                          (None, colltitle, '-', 'Latin', author, date, chapter,
                           verse, v, siteURL, 'poetry'))



if __name__ == '__main__':
    main()
