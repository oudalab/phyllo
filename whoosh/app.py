
import itertools
import io
import lxml
import lxml.html
import lxml.etree
import os
import sys
import urllib.request
import whoosh

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

from whoosh.fields import Schema
from whoosh.fields import TEXT
from whoosh.index import open_dir
from whoosh.index import create_in
from whoosh.qparser import MultifieldParser
from whoosh.qparser import QueryParser

from typing import List

StringArray = List[str]

import logging
# log = logging.getLogger("whoosh-test")
logging.basicConfig(stream=sys.stderr,
                    format='%(asctime)s %(levelname)s:%(name)s %(message)s',
                    level=logging.DEBUG)

import pdb
app = Flask('Phyllo')
Bootstrap(app)

def extract_collection(line, sep='\t'):
    col = {}
    entry = line.strip().split(sep)
    try:
        col['author'] = entry[0].strip()
        col['title'] = entry[1].strip()
        col['links'] = [x.strip() for x in entry[2].split(';')]
    except IndexError as e:
        logging.error('entry: {}'.format(entry))
        col['author'] = ''
        col['title'] = ''
        col['links'] = ''

    return col


def grab_collections(tsvfile, savepath, MAX_LINES=2**64):
    c = []
    with io.open(tsvfile, 'r', encoding='utf-8') as tsv:
        for index, line in enumerate(tsv):
            # Ignore header and empty line
            if index > MAX_LINES: break
            if index == 0 or not line.strip(): continue
            if line.startswith("Author"): continue
            if 'N/A' in line: continue
            c.append(extract_collection(line, '\t'))
    return c



def download_pages(pages: StringArray, verbose = False):
    if not verbose:
        return [urllib.request.urlopen(page).read().decode('utf-8', 'replace') for page in pages]
    else:
        array = []
        for page in pages:
            logging.info("Downloading |{}|".format(page))
            data = urllib.request.urlopen(page)
            array.append(data.read().decode('utf-8', 'replace'))
        return array


# Take a defined collection and download its data
def build_collections(collection_list):
    """Adding data to the collection_list. The @param is a mutable list."""
    for collection in collection_list:
        data = download_pages(collection['links'], verbose=True)
        collection['content'] = data


def grab_all_collection():
    """Grabs the hard coded collections."""
    all_collections = [grab_collections('../scripts/llc-christian.tsv', 'tmp/'),
                       grab_collections('../scripts/llc-main.tsv', 'tmp/'),
                       grab_collections('../scripts/llc-neolatin.tsv', 'tmp/'),
                       grab_collections('../scripts/llc-medieval.tsv', 'tmp/')]

    pages = list(itertools.chain(*all_collections))

    logging.info("collections size: {}".format(len(pages)))
    build_collections(pages)

    return pages


def build_schema():
    """Define Schema and initialize the index."""
    schema = Schema(author=TEXT(stored=True), 
                    title=TEXT(stored=True), 
                    link=TEXT(stored=True),
                    content=TEXT(stored=True))
    # Create index
    if not os.path.exists("index"):
        os.mkdir("index")

    ix = create_in("index", schema)


def write_index(pages):
    ix = open_dir("index")
    writer = ix.writer()
    # 'author', 'title', 'links', 'content'
    for page in pages:
        for link,content in zip(page['links'],page['content']):
            plain = ''
            try:
                html = lxml.html.fromstring(content)
                plain = lxml.html.tostring(html, pretty_print=True, method='text',
                                         encoding='unicode')
            except lxml.etree.ParserError as e:
                logging.warn("Empty: Author {}, Title {}, link \
                             {}".format(page.get('author',""),
                                        page.get('title',""),
                                        page.get('link',"")))
                link = page.get('link', "")

            writer.add_document(author=page.get('author',""),
                                title=page.get('title',""),
                                link=link,
                                content=plain)
    writer.commit()


def build_all():
    logging.info("Starting full build")
    build_schema()
    logging.info("grabbing all collection")
    pages = grab_all_collection()
    logging.info("Pages size: {}".format(len(pages)))
    logging.info("writing the index")
    write_index(pages)
    logging.info("Done")


def search(phrase: str):
    ix = open_dir('index')
    with ix.searcher() as searcher:
        #parser = QueryParser("content", ix.schema)
        parser = MultifieldParser(['author', 'title', 'link', 'content'],
                                  ix.schema)
        myquery = parser.parse(phrase)
        results = searcher.search(myquery, terms=True)
        # for hit in results:
        #     logging.info('hit: {}'.format(hit))
        # return results
        data = []
        for hit in results:
            logging.info("The hit: {}".format(hit.highlights('content')))
            data.append({"rank": hit.rank,
                         "author": {"data": hit["author"],
                                    "highlight" : hit.highlights("author")},
                         "title": {"data": hit["title"], 
                                   "highlight": hit.highlights("title")},
                         "link": {"data": hit["link"],
                                  "highlight":  hit.highlights("link")},
                         "content": {"data": hit["content"],
                                  "highlight":  hit.highlights("content")}
                         })
        return data


@app.route('/search/<string:query>')
def q(query):
    logging.info("Query: {}, type: {}".format(query, type(query)))
    results = search(query)

    return jsonify(results)


@app.route('/search/<string:query>/highlights', methods=['GET', 'POST'])
def q_highlights(query):
    logging.info("Query: {}, type: {}".format(query, type(query)))
    results = search(query)

    #return jsonify([hit.highlights('content') for hit in results])
    #return jsonify(results)
    return render_template('search.html', terms=query, results=results)


@app.route('/search', methods=['GET', 'POST'])
def index():
    logging.info("/search {}|{}".format(request.args, request.method))
    if request.method == 'GET' and request.args['q'] is not None:

        query = request.args['q']
        results = search(query)
        return render_template('search.html', terms=query, results=results)
    else:
        return render_template('search.html', terms="", results=[])

if __name__ == '__main__':
    app.run(host='localhost', port=5000, threaded=True, debug=True)


