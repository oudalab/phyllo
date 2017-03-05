import json

import apsw
import sqlitefts as fts
import os

import search
from search import OUWordTokenizer
#import phyllo  # phyllo must be installed
#from pympler.tracker import SummaryTracker

from flask import Flask
app = Flask(__name__)

#tracker = SummaryTracker()
def tokenize():
        connection = apsw.Connection('texts.db', flags=apsw.SQLITE_OPEN_READWRITE)
        c = connection.cursor()
        print("connection to cursor")
        fts.register_tokenizer(c, 'oulatin', fts.make_tokenizer_module(OUWordTokenizer('latin')))
        fts.register_tokenizer(c, 'porter', fts.make_tokenizer_module(OUWordTokenizer('latin')))
        print("registering tokenizer")
        c.execute("begin;")
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx  USING fts4 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("oulatin"))
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx_porter  USING fts4 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("porter"))
        c.execute("commit;")
        print("virtual table created")
        c.execute("INSERT INTO text_idx (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        c.execute("INSERT INTO text_idx_porter (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        print ("inserted data into virtual table")
        print ("Enter a phrase to search:")
        search=input()
        stmt1="select id, title, book, author, link from text_idx where passage MATCH '"+search+"'"
        stmt2="select id, title, book, author, link from text_idx where passage MATCH '"+search+"'"
        r1=c.execute(stmt1)
        r2=c.execute(stmt2)
        r3=(set(r1.fetchall()) or set(r2.fetchall()))
        r4=list(r3)
        print (r4)
        

@app.route('/')
def hello_world():
    print ("Hello world")
    search.word_tokenizer
    print ("word_tokenizers")
    return json.dumps({"name": "test"})


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        tokenize()
    app.run(debug=True, host='0.0.0.0')
    
#tracker.print_diff()
