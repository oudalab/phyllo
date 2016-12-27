
import json

import apsw
import sqlitefts as fts

import search
from search import OUWordTokenizer
import phyllo  # phyllo must be installed

from flask import Flask
app = Flask(__name__)


def tokenize():
    with apsw.Connection('texts.db') as connection:
        c = connection.cursor()
        fts.register_tokenizer(c, 'oulatin', fts.make_tokenizer_module(OUWordTokenizer('latin')))
        c.create("CREATE VIRTUAL TABLE text_idx USING fts4 (id, title, book, author, date, chapter, "
                 "verse, package, link, documentType, tokenize={}".format("oulatin"))
        c.execute("INSERT INTO text_idx (id title, book, author, date, chapter, "
                 "verse, package, link, documentType) SELECT id, title, book, author, date, chapter, "
                 "verse, package, link, documentType FROM texts")


@app.route('/')
def hello_world():
    wt = search.word_tokenizer
    return json.dumps({"name": "test"})


if __name__ == '__main__':
    tokenize()
    app.run(debug=True, host='0.0.0.0')
