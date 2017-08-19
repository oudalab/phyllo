import json

import apsw
import sqlitefts as fts
import os
import html

import search
from flask import Flask
from flask import abort
from flask import request
from flask import jsonify

from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import render_template
from flask import flash

from flask_bootstrap import Bootstrap
from search import OUWordTokenizer

from flask import Flask
from flask import request

from phyllo.phyllo_logger import logger


app = Flask('Phyllo')
Bootstrap(app)
connection = apsw.Connection('texts.db', flags=apsw.SQLITE_OPEN_READWRITE)
c = connection.cursor()
# Register with the connection
fts.register_tokenizer(connection,
                       'oulatin',
                       fts.make_tokenizer_module(OUWordTokenizer('latin')))


def setup():
    logger.info("Setting up the connnection.")

    # Check if the virtual table exists
    c.execute(("SELECT count(*)"
               " FROM sqlite_master"
               " WHERE type='table'"
               "  AND name='text_idx'"
               "  OR name='text_idx_porter'"))
    r = c.fetchall()
    rowcount = list(r[0])
    print(rowcount)

    if rowcount[0] < 2 :
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        # Create the virtual table if it doesnt exist
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx USING fts3 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("oulatin"))
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx_porter USING fts3 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("porter"))
        c.execute("INSERT INTO text_idx (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        c.execute("INSERT INTO text_idx_porter (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        # Add the cursor to the app config
        logger.info("Virtual Table data inserted...")

        app.config["cursor"] = c

    elif "cursor" not in app.config:
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        app.config["cursor"] = c

    else:
        logger.info("Virtual Table already exists, skipping...")

    return app.config["cursor"]


def do_search(query):
    stmt1 = ("SELECT title, book, author, link, snippet(text_idx)"
             " FROM text_idx "
             " WHERE text_idx MATCH '{}';")
    stmt2 = ("SELECT title, book, author, link, snippet(text_idx_porter)"
             " FROM text_idx_porter"
             " WHERE text_idx_porter MATCH '{}';")

    logger.info("Running the queries...")
    if c:
        logger.info("Running query 1...")
        print(stmt1.format(query))
        c.execute(stmt1.format(query))
        r1 = c.fetchall()
        r1set = {x[1:] for x in r1}
        logger.info("Result Set 1: {}".format(type(r1)))
        logger.info("Result Set 1: {}".format(list(r1set)[:10]))

        logger.info("Running query 2...")
        c.execute(stmt2.format(query))
        r2 = c.fetchall()
        r2set = {y[1:] for y in r2}
        logger.info("Result Set 2: {}".format(type(r2)))
        logger.info("Result Set 2: {}".format(list(r2set)[:10]))

        # Union
        r3 = list(set(r1).union(set(r2)))
        print(r3)

        logger.info("Joined query list: {}".format([z for z in r3]))
        logger.info("Total result set size: {}".format(len(r3)))
        return r3

    else:
        logger.error("The cursor is not in app.config")
        return []


@app.route('/search', methods=['GET', 'POST'])
def search():
    result=[]
    logger.info("/search {}|{}".format(request.args, request.method))
    if request.method == 'GET' and request.args['q'] is not None:
        query = request.args['q']

        logger.info("The query term is {}".format(query))
        r = do_search(query)
        for h in r:
            li = list(h)
            y = h[4]
            li[4] = y
            result.append(li)

        return render_template('search.html', terms=query, results=result)

    else:
        logger.error("Could not make the query")
        return json.dumps([])


@app.route('/helloworld')
def hello_world():
    print("Hello world")
    #search.word_tokenizer
    print("word_tokenizers")
    return json.dumps({"name": "test"})

@app.route('/')
def application():
    return render_template('search.html', terms='', results='')



if __name__ == '__main__':
    setup()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
    logger.info("Starting app...")

