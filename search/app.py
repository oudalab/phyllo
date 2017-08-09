import json

import apsw
import sqlitefts as fts
import os

import search
from search import OUWordTokenizer
#import phyllo  # phyllo must be installed
#from pympler.tracker import SummaryTracker

from flask import Flask

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

from phyllo.phyllo_logger import logger


app = Flask(__name__)


def setup():
    logger.info("Setting up the connnection.")
    connection = apsw.Connection('texts.db', flags=apsw.SQLITE_OPEN_READWRITE)
    c = connection.cursor()

    # Register with the connection
    fts.register_tokenizer(connection,
                           'oulatin',
                           fts.make_tokenizer_module(OUWordTokenizer('latin')))

    # Check if the virtual table exists
    c.execute(("SELECT count(*)"
               " FROM sqlite_master"
               " WHERE type='table'"
               "  AND name='text_idx'"
               "  OR name='text_idx_porter'"))
    rowcount = c.fetchall()

    if rowcount[0][0] < 2 :
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        # Create the virtual table if it doesnt exist
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx USING fts3 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("oulatin"))
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx_porter USING fts3 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("porter"))
        c.execute("INSERT INTO text_idx (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        c.execute("INSERT INTO text_idx_porter (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        # Add the cursor to the app config
        app.config["cursor"] = c

    elif "cursor" not in app.config:
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        app.config["cursor"] = c

    else:
        logger.info("Virtual Table already exists, skipping...")

    return app.config["cursor"]


def do_search(query):
    stmt1 = ("SELECT id, title, book, author, link"
             " FROM text_idx "
             " WHERE text_idx MATCH '{}'")
    stmt2 = ("SELECT id, title, book, author, link"
             " FROM text_idx_porter"
             " WHERE text_idx_porter MATCH '{}'")

    logger.info("Running the queries...")
    if "cursor" in app.config:
        logger.info("Running query 1...")
        r1 = app.config["cursor"].execute(stmt1.format(query))
        r1set = {x[1:] for x in r1}
        logger.info("Result Set 1: {}".format(type(r1)))
        logger.info("Result Set 1: {}".format(list(r1set)[:10]))

        logger.info("Running query 2...")
        r2 = app.config["cursor"].execute(stmt2.format(query))
        r2set = {y[1:] for y in r2}
        logger.info("Result Set 2: {}".format(type(r2)))
        logger.info("Result Set 2: {}".format(list(r2set)[:10]))

        # Union
        r3 = list(r2set | r1set)

        logger.info("Joined query list: {}".format([z for z in r3]))
        logger.info("Total result set size: {}".format(len(r3)))
        return r3

    else:
        logger.error("The cursor is not in app.config")
        return []


@app.route('/search', methods=['GET'])
def search():
    logger.info("/search {}|{}".format(request.args, request.method))
    if request.method == 'GET' and request.args['q'] is not None:
        query = request.args['q']

        logger.info("The query term is {}".format(query))
        result = do_search(query)

        json.dumps(result)

    else:
        logger.error("Could not make the query")
        return json.dumps([])


@app.route('/helloworld')
def hello_world():
    print("Hello world")
    #search.word_tokenizer
    print("word_tokenizers")
    return json.dumps({"name": "test"})


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info("Running setup...")
        setup()

    logger.info("Starting app...")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
