import json
from collections import defaultdict

import apsw
import sqlitefts as fts
import os

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
    rowcount = c.fetchall()

    if rowcount[0][0] < 2 :
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        # Create the virtual table if it doesnt exist
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx USING fts4 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("oulatin"))
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS text_idx_porter USING fts4 (id, title, book, author, date, chapter, verse, passage, link, documentType, tokenize={});".format("porter"))

        c.execute("INSERT INTO text_idx (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        logger.info("Inserted rows into text_idx")

        c.execute("INSERT INTO text_idx_porter (id, title, book, author, date, chapter, verse, passage, link, documentType) SELECT id, title, book, author, date, chapter, verse, passage, link, documentType FROM texts;")
        logger.info("Inserted rows into text_idx_porter")

        # Add the cursor to the app config
        app.config["cursor"] = c
        logger.info("New cursor saved!")

    elif "cursor" not in app.config:
        logger.info("Recreating virtual table <'rowcount:{}, app.config?:{}>"
                    .format(rowcount, "cursor" in app.config))
        app.config["cursor"] = c
        logger.info("New cursor saved!")

    else:
        logger.info("Virtual Table already exists, skipping setup...")

    return app.config["cursor"]


def combine_results(rs1, rs2):
    """Combine the results of two queries.
       It created a dictionary where the group by
       parameters are the keys and the snippet
       is concatenated togther in a set.

       Each result set should have the same format.
       (rowid, title, book, author, link, snippet)

       The dictionary will have the format
       { (title, book, author, link): [snippet] }

       The rowid will be lost. We can preserve it
       later if necessary.
    """
    d = defaultdict(set)
    for r in rs1:
        t = (r[0], r[1], r[2], r[3])
        d[t].add(r[4])

    for r in rs2:
        t = (r[0], r[1], r[2], r[3])
        d[t].add(r[4])

    return d


def do_search_with_snippets(query):
    # OULatin Parser
    # TODO: add a ranking function: "  rank(matchinfo(text_idx)) as rank"
    # look for the bm25 implementation
    stmt1 = ("SELECT title, book, author, link,"
             "  snippet(text_idx) as snippet"
             " FROM text_idx "
             " WHERE text_idx MATCH '{}';")

    # Porter Parser
    stmt2 = ("SELECT title, book, author, link,"
             "  snippet(text_idx_porter) as snippet"
             " FROM text_idx_porter"
             " WHERE text_idx_porter MATCH '{}';")

    logger.info("Running the queries with snippets...")
    if "cursor" not in app.config:
        logger.error("The cursor is not in app.config")
        setup()

    if "cursor" in app.config:
        logger.info("Running query 1...")
        c.execute(stmt1.format(query))
        r1 = []
        while True:
            try:
                try:
                    row = next(c)
                    r1.append(row)
                except UnicodeDecodeError as e:
                    logger.error("Unicode Decode error {}".format(e))
            except StopIteration:
                logger.info("r1 completed")
                break

        logger.info("Running query 2...")
        c.execute(stmt2.format(query))
        r2 = []
        while True:
            try:
                try:
                    row = next(c)
                    r2.append(row)
                except UnicodeDecodeError as e:
                    logger.error("Unicode Decode error {}".format(e))
            except StopIteration:
                logger.info("r2 completed")
                break

        # Union
        logger.info("Combining Results...")
        r3 = combine_results(r1, r2)

        logger.info("OULatin size: {}, Porter size: {}, Union size: {}"
                    .format(len(r1), len(r2), len(r3)))
        logger.info("Total result set size: {}".format(len(r3)))

        return r3

    else:
        logger.error("The cursor is not in app.config -- second try failed.")
        return {}



@app.route('/search', methods=['GET', 'POST'])
def search():
    logger.info("/search {}|{}".format(request.args, request.method))
    if request.method == 'GET' and request.args['q'] is not None:
        query = request.args['q']

        logger.info("The query term is {}".format(query))
        result = do_search_with_snippets(query)
        logger.info(list(result.items())[0:10])
        return render_template('search_snippet.html', terms=query, results=result)

    else:
        logger.error("Could not make the query")
        return json.dumps([])


@app.route('/')
def application():
    setup()
    return render_template('search.html', terms='', results='')


if __name__ == '__main__':
    # Initialize the database 
    setup()
    logger.info("Starting app...")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
