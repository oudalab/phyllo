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
        print("registering tokenizer")
        c.execute("begin;")
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx  USING fts3 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("oulatin"))
        c.execute("commit;")
        print("virtual table created")
        c.execute("INSERT INTO text_idx (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        print ("inserted data into virtual table")

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
