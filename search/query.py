import json

import apsw
import sqlitefts as fts
import os
import search
from search import OUWordTokenizer


from flask import Flask
app = Flask(__name__)

def query():
    connection = apsw.Connection('texts.db', flags=apsw.SQLITE_OPEN_READWRITE)
    c = connection.cursor()
    fts.register_tokenizer(c, 'oulatin', fts.make_tokenizer_module(OUWordTokenizer('latin')))
    print ("Enter a phrase to search:")
    search = input()
    stmt1 = "select id, title, book, author, link from text_idx where passage MATCH '" + search + "'"
    stmt2 = "select id, title, book, author, link from text_idx_porter where passage MATCH '" + search + "'"
    r1 = c.execute(stmt1)
    r2 = c.execute(stmt2)
    r3=(set(r2).union(set(r1)))
    r4 = list(r3)
    print (r4)

@app.route('/')
def hello_world():
    print ("Hello world")
    print ("word_tokenizers")
    return json.dumps({"name": "test"})


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        query()
    app.run(debug=True, host='0.0.0.0')
