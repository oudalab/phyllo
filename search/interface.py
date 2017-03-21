from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
import json

import search
from search import OUWordTokenizer

import apsw
import sqlitefts as fts
import os

import warnings
warnings.filterwarnings("ignore")

app=Flask(__name__)
Bootstrap(app)

class SearchForm(Form):
    user_query = StringField('user_query', validators=[DataRequired()])

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/search/', methods=["GET", "POST"])
def search():
    sf = SearchForm(csrf_enabled=False)
    if sf.validate():
        results(sf.user_query.data)
    return render_template("search.html", form=sf)

@app.route('/search_results/', methods=["GET", "POST"])
def results(query):
    connection = apsw.Connection('texts.db', flags=apsw.SQLITE_OPEN_READWRITE)
    c1 = connection.cursor()
    c2 = connection.cursor()
    fts.register_tokenizer(c1, 'oulatin', fts.make_tokenizer_module(OUWordTokenizer('latin')))
    c1.execute("SELECT * FROM text_idx WHERE passage MATCH ?", [query])
    c2.exexute("SELECT * FROM text_idx_porter WHERE passage MATCH ?", [query])
    r1=set(c1.fetchall()).union(set(c2.fetchall()))
    render_template("search_results.html", results=r1)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')